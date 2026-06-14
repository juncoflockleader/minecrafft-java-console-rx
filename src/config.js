import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

// Minimal .env loader (no dependency). Only sets vars that aren't already set.
function loadDotEnv() {
  const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
  const file = path.join(root, ".env");
  if (!fs.existsSync(file)) return;
  for (const raw of fs.readFileSync(file, "utf8").split("\n")) {
    const line = raw.trim();
    if (!line || line.startsWith("#")) continue;
    const eq = line.indexOf("=");
    if (eq === -1) continue;
    const key = line.slice(0, eq).trim();
    let val = line.slice(eq + 1).trim();
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
      val = val.slice(1, -1);
    }
    if (process.env[key] === undefined) process.env[key] = val;
  }
}

loadDotEnv();

const rconHost = process.env.RCON_HOST || "127.0.0.1";

export const config = {
  host: process.env.HOST || "127.0.0.1",
  port: Number(process.env.PORT || 8765),
  rcon: {
    host: rconHost,
    port: Number(process.env.RCON_PORT || 25575),
    password: process.env.RCON_PASSWORD || "",
  },
  mc: {
    host: process.env.MC_HOST || rconHost,
    port: Number(process.env.MC_PORT || 25565),
  },
  logPath: process.env.MC_LOG_PATH || "",
  auth: {
    user: process.env.WEBUI_USER || "",
    password: process.env.WEBUI_PASSWORD || "",
  },
};

export function validateConfig() {
  if (!config.rcon.password) {
    throw new Error("RCON_PASSWORD is required. Copy .env.example to .env and set it.");
  }
}
