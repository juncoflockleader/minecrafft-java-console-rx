import fs from "node:fs";

// Curated, commonly-tweaked keys surfaced as friendly controls in the UI.
// (Any key in server.properties can still be written; these just get nice widgets.)
export const CURATED = [
  { key: "motd", type: "string", label: "MOTD" },
  { key: "difficulty", type: "enum", options: ["peaceful", "easy", "normal", "hard"], label: "Difficulty" },
  { key: "gamemode", type: "enum", options: ["survival", "creative", "adventure", "spectator"], label: "Default gamemode" },
  { key: "max-players", type: "int", label: "Max players" },
  { key: "pvp", type: "bool", label: "PvP" },
  { key: "hardcore", type: "bool", label: "Hardcore" },
  { key: "white-list", type: "bool", label: "Whitelist enabled" },
  { key: "online-mode", type: "bool", label: "Online mode (auth)" },
  { key: "allow-flight", type: "bool", label: "Allow flight" },
  { key: "spawn-monsters", type: "bool", label: "Spawn monsters" },
  { key: "view-distance", type: "int", label: "View distance" },
  { key: "simulation-distance", type: "int", label: "Simulation distance" },
  { key: "level-seed", type: "string", label: "Level seed" },
  { key: "enable-command-block", type: "bool", label: "Command blocks" },
];

const KEY_RE = /^[A-Za-z0-9._-]+$/;

export function makeProperties(propertiesPath) {
  function readAll() {
    if (!propertiesPath || !fs.existsSync(propertiesPath)) return {};
    const out = {};
    for (const line of fs.readFileSync(propertiesPath, "utf8").split("\n")) {
      const t = line.trim();
      if (!t || t.startsWith("#")) continue;
      const eq = t.indexOf("=");
      if (eq === -1) continue;
      out[t.slice(0, eq)] = t.slice(eq + 1);
    }
    return out;
  }

  return {
    available: () => Boolean(propertiesPath && fs.existsSync(propertiesPath)),
    get() {
      const all = readAll();
      return { all, curated: CURATED };
    },
    // Apply a {key: value} patch, preserving comments and unrelated lines.
    update(patch) {
      if (!propertiesPath || !fs.existsSync(propertiesPath)) throw new Error("server.properties not accessible");
      for (const k of Object.keys(patch)) {
        if (!KEY_RE.test(k)) throw new Error(`invalid property key: ${k}`);
        if (/[\n\r]/.test(String(patch[k]))) throw new Error("invalid property value");
      }
      const lines = fs.readFileSync(propertiesPath, "utf8").split("\n");
      const seen = new Set();
      const next = lines.map((line) => {
        const t = line.trim();
        if (!t || t.startsWith("#")) return line;
        const eq = t.indexOf("=");
        if (eq === -1) return line;
        const key = t.slice(0, eq);
        if (key in patch) {
          seen.add(key);
          return `${key}=${patch[key]}`;
        }
        return line;
      });
      for (const k of Object.keys(patch)) {
        if (!seen.has(k)) next.push(`${k}=${patch[k]}`);
      }
      fs.writeFileSync(propertiesPath, next.join("\n"));
      return readAll();
    },
  };
}
