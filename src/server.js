import express from "express";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { WebSocketServer } from "ws";

import { config, validateConfig } from "./config.js";
import { rconCommand } from "./rcon.js";
import { LogTailer } from "./logtail.js";
import { pingStatus } from "./status.js";
import {
  authGate,
  wsAuthorized,
  verifyCredentials,
  createSession,
  destroySession,
  sessionTokenFromReq,
  sessionCookieHeader,
  clearCookieHeader,
} from "./auth.js";
import { makeWhitelist } from "./whitelist.js";
import { makeProperties } from "./properties.js";
import { makeJarManager } from "./jardir.js";
import { makeLifecycle } from "./lifecycle.js";

validateConfig();

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const publicDir = path.join(__dirname, "..", "public");

const app = express();
app.use(express.json({ limit: "64kb" }));

// --- auth: form login -> session cookie ---
app.post("/api/login", (req, res) => {
  const { user, password } = req.body || {};
  if (verifyCredentials(user, password, config.auth)) {
    res.setHeader("Set-Cookie", sessionCookieHeader(createSession()));
    return res.json({ ok: true });
  }
  res.status(401).json({ error: "invalid credentials" });
});
app.post("/api/logout", (req, res) => {
  destroySession(sessionTokenFromReq(req));
  res.setHeader("Set-Cookie", clearCookieHeader());
  res.json({ ok: true });
});

app.use(authGate(config.auth));
app.use(express.static(publicDir));

// Run a single RCON command.
async function runCommand(command) {
  const text = await rconCommand(command, config.rcon);
  return text;
}

app.get("/api/status", async (_req, res) => {
  try {
    const status = await pingStatus(config.mc);
    res.json(status);
  } catch (err) {
    res.json({ online: false, error: String(err.message || err) });
  }
});

app.post("/api/command", async (req, res) => {
  const command = (req.body?.command || "").trim();
  if (!command) return res.status(400).json({ error: "command required" });
  try {
    res.json({ command, response: await runCommand(command) });
  } catch (err) {
    res.status(502).json({ command, error: String(err.message || err) });
  }
});

// ---- management: whitelist, properties, plugins, mods, lifecycle ----
const whitelist = makeWhitelist(config.rcon, config.server.propertiesPath);
const properties = makeProperties(config.server.propertiesPath);
const plugins = makeJarManager(config.server.pluginsDir, { kind: "plugin", loaders: ["paper", "spigot", "bukkit"] });
const mods = makeJarManager(config.server.modsDir, { kind: "mod", loaders: ["fabric", "forge", "neoforge", "quilt"] });
const lifecycle = makeLifecycle({
  start: config.server.startCommand,
  stop: config.server.stopCommand,
  restart: config.server.restartCommand,
});
// Mods are only manageable on a modded server (mods/ exists) or when explicitly configured.
const modsEnabled = Boolean(process.env.MC_MODS_DIR) || mods.available();

// async route wrapper -> JSON errors
const h = (fn) => (req, res) =>
  Promise.resolve(fn(req, res)).catch((e) => res.status(e.status || 500).json({ error: String(e.message || e) }));

const extractGameVersion = (v) => {
  const m = String(v || "").match(/(\d+\.\d+(?:\.\d+)?)/);
  return m ? m[1] : null;
};
async function detectGameVersion() {
  try {
    return extractGameVersion((await pingStatus(config.mc)).version);
  } catch {
    return null;
  }
}

app.get("/api/capabilities", async (_req, res) => {
  let version = null;
  try { version = (await pingStatus(config.mc)).version; } catch {}
  res.json({
    plugins: plugins.available(),
    mods: modsEnabled,
    properties: properties.available(),
    start: lifecycle.canStart(),
    stop: lifecycle.canStop(),
    restart: lifecycle.canRestart(),
    logStream: Boolean(config.logPath),
    serverType: mods.available() ? "modded" : "plugin",
    version,
    gameVersion: extractGameVersion(version),
  });
});

app.get("/api/whitelist", h(async (_req, res) => res.json(await whitelist.get())));
app.post("/api/whitelist/add", h(async (req, res) => res.json({ result: await whitelist.add(String(req.body?.name || "").trim()) })));
app.post("/api/whitelist/remove", h(async (req, res) => res.json({ result: await whitelist.remove(String(req.body?.name || "").trim()) })));
app.post("/api/whitelist/enabled", h(async (req, res) => res.json({ result: await whitelist.setEnabled(Boolean(req.body?.enabled)) })));

app.get("/api/properties", h(async (_req, res) => res.json(properties.get())));
app.post("/api/properties", h(async (req, res) => {
  const patch = req.body?.patch;
  if (!patch || typeof patch !== "object") throw new Error("patch object required");
  res.json({ all: properties.update(patch) });
}));

function registerJarRoutes(prefix, mgr, isEnabled) {
  const guard = (res) => {
    if (isEnabled()) return true;
    res.status(409).json({ error: `${prefix} management not available on this server` });
    return false;
  };
  app.get(`/api/${prefix}`, (_req, res) => { if (guard(res)) res.json({ items: mgr.list() }); });
  app.post(`/api/${prefix}/install`, h(async (req, res) => {
    if (!guard(res)) return;
    const { url, slug, gameVersion } = req.body || {};
    let result;
    if (url) result = await mgr.installUrl(String(url));
    else if (slug) result = await mgr.installModrinth(String(slug), gameVersion ? String(gameVersion) : await detectGameVersion());
    else throw new Error("provide a url or a Modrinth slug");
    res.json({ installed: result });
  }));
  app.post(`/api/${prefix}/toggle`, h(async (req, res) => {
    if (!guard(res)) return;
    res.json(mgr.toggle(String(req.body?.name || ""), Boolean(req.body?.enabled)));
  }));
  app.post(`/api/${prefix}/remove`, h(async (req, res) => {
    if (!guard(res)) return;
    res.json(mgr.remove(String(req.body?.name || "")));
  }));
  // Upload a jar: raw binary body, filename in ?name= query.
  app.post(`/api/${prefix}/upload`, express.raw({ type: () => true, limit: "256mb" }), h(async (req, res) => {
    if (!guard(res)) return;
    res.json({ installed: mgr.saveUpload(req.query.name, req.body) });
  }));
}
registerJarRoutes("plugins", plugins, () => plugins.available());
registerJarRoutes("mods", mods, () => modsEnabled);

app.post("/api/server/start", h(async (_req, res) => res.json(await lifecycle.start())));
app.post("/api/server/stop", h(async (_req, res) => res.json(await lifecycle.stop())));
app.post("/api/server/restart", h(async (_req, res) => res.json(await lifecycle.restart())));

const server = http.createServer(app);

// Live log streaming + interactive console over WebSocket.
const wss = new WebSocketServer({ noServer: true });
const tailer = new LogTailer(config.logPath).start();

server.on("upgrade", (req, socket, head) => {
  if (req.url.split("?")[0] !== "/ws") return socket.destroy();
  if (!wsAuthorized(req, config.auth)) {
    socket.write("HTTP/1.1 401 Unauthorized\r\n\r\n");
    return socket.destroy();
  }
  wss.handleUpgrade(req, socket, head, (ws) => wss.emit("connection", ws, req));
});

function send(ws, obj) {
  if (ws.readyState === ws.OPEN) ws.send(JSON.stringify(obj));
}

wss.on("connection", (ws) => {
  // Replay recent history so the console isn't blank on connect.
  send(ws, { type: "history", lines: tailer.getHistory() });
  if (!config.logPath) {
    send(ws, { type: "system", line: "(log streaming disabled: MC_LOG_PATH not set)" });
  }

  const onLine = (line) => send(ws, { type: "log", line });
  tailer.on("line", onLine);
  ws.on("close", () => tailer.off("line", onLine));

  ws.on("message", async (raw) => {
    let msg;
    try {
      msg = JSON.parse(raw.toString());
    } catch {
      return;
    }
    if (msg.type !== "command") return;
    const command = (msg.command || "").trim();
    if (!command) return;
    send(ws, { type: "echo", line: `> ${command}` });
    try {
      const response = await runCommand(command);
      send(ws, { type: "response", command, line: response });
    } catch (err) {
      send(ws, { type: "error", command, line: String(err.message || err) });
    }
  });
});

server.listen(config.port, config.host, () => {
  const authNote = config.auth.user ? "auth enabled" : "no auth";
  console.log(`minecrafft-console listening on http://${config.host}:${config.port} (${authNote})`);
  console.log(`  RCON -> ${config.rcon.host}:${config.rcon.port}   SLP -> ${config.mc.host}:${config.mc.port}`);
  console.log(`  log  -> ${config.logPath || "(disabled)"}`);
});
