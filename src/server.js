import express from "express";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { WebSocketServer } from "ws";

import { config, validateConfig } from "./config.js";
import { rconCommand } from "./rcon.js";
import { LogTailer } from "./logtail.js";
import { pingStatus } from "./status.js";
import { basicAuth, wsAuthorized } from "./auth.js";

validateConfig();

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const publicDir = path.join(__dirname, "..", "public");

const app = express();
app.use(express.json({ limit: "64kb" }));
app.use(basicAuth(config.auth));
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

const server = http.createServer(app);

// Live log streaming + interactive console over WebSocket.
const wss = new WebSocketServer({ noServer: true });
const tailer = new LogTailer(config.logPath).start();

server.on("upgrade", (req, socket, head) => {
  if (req.url.split("?")[0] !== "/ws") return socket.destroy();
  if (!wsAuthorized(req, config.auth)) {
    socket.write("HTTP/1.1 401 Unauthorized\r\nWWW-Authenticate: Basic realm=\"minecrafft-console\"\r\n\r\n");
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
