import fs from "node:fs";
import { rconCommand } from "./rcon.js";

const NAME_RE = /^[A-Za-z0-9_]{1,16}$/; // valid Minecraft username chars

function validName(name) {
  if (!NAME_RE.test(name)) throw new Error("invalid player name");
  return name;
}

// Read the on/off state from server.properties when available (RCON has no query for it).
function readEnabled(propertiesPath) {
  if (!propertiesPath || !fs.existsSync(propertiesPath)) return null;
  const m = fs.readFileSync(propertiesPath, "utf8").match(/^white-list=(\w+)/m);
  return m ? m[1] === "true" : null;
}

// Parse "There are N whitelisted player(s): a, b, c" / "... no whitelisted players"
function parseList(text) {
  const idx = text.indexOf(":");
  if (idx === -1) return [];
  const tail = text.slice(idx + 1).trim();
  if (!tail) return [];
  return tail.split(",").map((s) => s.trim()).filter(Boolean);
}

export function makeWhitelist(rcon, propertiesPath) {
  const run = (cmd) => rconCommand(cmd, rcon);
  return {
    async get() {
      const text = await run("whitelist list");
      return { enabled: readEnabled(propertiesPath), players: parseList(text), raw: text.trim() };
    },
    async add(name) {
      return (await run(`whitelist add ${validName(name)}`)).trim();
    },
    async remove(name) {
      return (await run(`whitelist remove ${validName(name)}`)).trim();
    },
    async setEnabled(enabled) {
      // `whitelist on/off` flips white-list in server.properties at runtime too.
      return (await run(`whitelist ${enabled ? "on" : "off"}`)).trim();
    },
    async reload() {
      return (await run("whitelist reload")).trim();
    },
  };
}
