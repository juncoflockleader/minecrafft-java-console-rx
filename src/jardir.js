import fs from "node:fs";
import fsp from "node:fs/promises";
import path from "node:path";
import { pipeline } from "node:stream/promises";
import { Readable } from "node:stream";

const UA = "minecrafft-java-console-rx";

// Only allow a safe basename ending in .jar (blocks path traversal).
function safeJar(name) {
  const base = path.basename(name);
  if (base !== name || !/^[\w.\- ]+\.jar$/.test(base)) throw new Error("invalid jar filename");
  return base;
}

async function download(url, destPath) {
  const res = await fetch(url, { headers: { "User-Agent": UA }, redirect: "follow" });
  if (!res.ok) throw new Error(`download failed: HTTP ${res.status}`);
  const tmp = destPath + ".part";
  await pipeline(Readable.fromWeb(res.body), fs.createWriteStream(tmp));
  await fsp.rename(tmp, destPath);
}

/**
 * Manage a directory of plugin/mod jars. `kind` is "plugin" or "mod" (for the
 * Modrinth loader filter). Returns null-safe operations; `available()` reports
 * whether the directory exists.
 */
export function makeJarManager(dir, { kind = "plugin", loaders = ["paper", "spigot", "bukkit"] } = {}) {
  function ensureDir() {
    if (!dir) throw new Error("directory not configured");
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  }

  return {
    kind,
    dir,
    available: () => Boolean(dir) && fs.existsSync(dir),

    list() {
      if (!dir || !fs.existsSync(dir)) return [];
      return fs
        .readdirSync(dir)
        .filter((f) => f.endsWith(".jar") || f.endsWith(".jar.disabled"))
        .map((f) => {
          const enabled = f.endsWith(".jar");
          const name = enabled ? f : f.slice(0, -".disabled".length);
          let size = 0;
          try { size = fs.statSync(path.join(dir, f)).size; } catch {}
          return { name, enabled, size };
        })
        .sort((a, b) => a.name.localeCompare(b.name));
    },

    async installUrl(url) {
      ensureDir();
      let u;
      try { u = new URL(url); } catch { throw new Error("invalid URL"); }
      if (u.protocol !== "https:" && u.protocol !== "http:") throw new Error("URL must be http(s)");
      let fname = safeJar(path.basename(u.pathname));
      await download(url, path.join(dir, fname));
      return { name: fname };
    },

    // Resolve the newest matching version on Modrinth and install it.
    async installModrinth(slug, gameVersion) {
      ensureDir();
      if (!/^[\w!@$()`.+,"\-']{1,64}$/.test(slug)) throw new Error("invalid project slug");
      const base = `https://api.modrinth.com/v2/project/${encodeURIComponent(slug)}/version`;
      const q = (gv) =>
        `${base}?loaders=${encodeURIComponent(JSON.stringify(loaders))}` +
        (gv ? `&game_versions=${encodeURIComponent(JSON.stringify([gv]))}` : "");

      async function fetchVersions(gv) {
        const r = await fetch(q(gv), { headers: { "User-Agent": UA } });
        if (!r.ok) throw new Error(`Modrinth HTTP ${r.status}`);
        return r.json();
      }

      // Try exact game version, then fall back to latest compatible build.
      let versions = gameVersion ? await fetchVersions(gameVersion) : [];
      if (!versions.length) versions = await fetchVersions(null);
      if (!versions.length) throw new Error(`no ${kind} build found on Modrinth for "${slug}"`);

      versions.sort((a, b) => new Date(b.date_published) - new Date(a.date_published));
      const v = versions[0];
      const file = v.files.find((f) => f.primary) || v.files[0];
      if (!file) throw new Error("Modrinth version has no downloadable file");
      const fname = safeJar(path.basename(new URL(file.url).pathname));
      await download(file.url, path.join(dir, fname));
      return { name: fname, version: v.version_number, gameVersions: v.game_versions };
    },

    toggle(name, enabled) {
      if (!dir) throw new Error("directory not configured");
      const base = safeJar(name);
      const jar = path.join(dir, base);
      const off = jar + ".disabled";
      if (enabled) {
        if (!fs.existsSync(off)) throw new Error("disabled jar not found");
        fs.renameSync(off, jar);
      } else {
        if (!fs.existsSync(jar)) throw new Error("jar not found");
        fs.renameSync(jar, off);
      }
      return { name: base, enabled };
    },

    remove(name) {
      if (!dir) throw new Error("directory not configured");
      const base = safeJar(name);
      for (const p of [path.join(dir, base), path.join(dir, base + ".disabled")]) {
        if (fs.existsSync(p)) fs.unlinkSync(p);
      }
      return { name: base, removed: true };
    },
  };
}
