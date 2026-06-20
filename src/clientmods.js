import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

// Publishes the client-side mod set (fabric-api + our mods) plus a manifest and
// a Windows updater script, so players can keep their client in sync with the
// server. All routes are intentionally UNAUTHENTICATED (LAN distribution).

const sha256 = (file) =>
  crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");

export function makeClientMods(dir, opts = {}) {
  const minecraft = opts.minecraft || "1.21.11";
  const available = () => Boolean(dir) && fs.existsSync(dir);

  function listJars() {
    if (!available()) return [];
    return fs
      .readdirSync(dir)
      .filter((f) => f.toLowerCase().endsWith(".jar"))
      .sort()
      .map((name) => {
        const full = path.join(dir, name);
        const st = fs.statSync(full);
        return { name, size: st.size, sha256: sha256(full), url: `/clientmods/files/${encodeURIComponent(name)}` };
      });
  }

  function manifest() {
    return {
      minecraft,
      loader: "fabric",
      generated: new Date().toISOString(),
      mods: listJars(),
    };
  }

  // Resolve a requested filename safely to a jar inside `dir`.
  function filePath(name) {
    const base = path.basename(String(name || ""));
    if (!base.toLowerCase().endsWith(".jar")) return null;
    const full = path.join(dir, base);
    if (!full.startsWith(path.resolve(dir) + path.sep)) return null;
    return fs.existsSync(full) ? full : null;
  }

  function updateScript(base) {
    return `#requires -version 5
<#
  Arsenal mod sync — keeps your Minecraft client mods in step with ${base}
  Usage:   right-click -> Run with PowerShell      (or)   .\\Update-Mods.ps1
  Options: -Base <url>   -ModsDir <path>   -Launch
#>
param(
  [string]$Base = "${base}",
  [string]$ModsDir = "$env:APPDATA\\.minecraft\\mods",
  [switch]$Launch
)
$ErrorActionPreference = "Stop"
Write-Host "Arsenal mod sync  <-  $Base" -ForegroundColor Cyan

if (!(Test-Path $ModsDir)) { New-Item -ItemType Directory -Force -Path $ModsDir | Out-Null }
$stateFile = Join-Path $ModsDir ".arsenal-sync.json"
$prev = @()
if (Test-Path $stateFile) { try { $prev = (Get-Content $stateFile -Raw | ConvertFrom-Json).managed } catch {} }

$manifest = Invoke-RestMethod -Uri "$Base/clientmods/manifest.json" -UseBasicParsing
Write-Host ("Minecraft {0} / {1}  -  {2} mod(s)" -f $manifest.minecraft, $manifest.loader, $manifest.mods.Count)

$managed = @()
foreach ($m in $manifest.mods) {
  $managed += $m.name
  $dest = Join-Path $ModsDir $m.name
  $have = $false
  if (Test-Path $dest) {
    $h = (Get-FileHash -Algorithm SHA256 -Path $dest).Hash.ToLower()
    if ($h -eq $m.sha256.ToLower()) { $have = $true }
  }
  if ($have) {
    Write-Host ("  ok    {0}" -f $m.name) -ForegroundColor DarkGray
  } else {
    Write-Host ("  fetch {0}" -f $m.name) -ForegroundColor Yellow
    Invoke-WebRequest -Uri "$Base$($m.url)" -OutFile $dest -UseBasicParsing
  }
}

# Remove mods we previously installed that are no longer in the manifest
# (leaves any other mods the player added alone).
foreach ($old in $prev) {
  if ($managed -notcontains $old) {
    $p = Join-Path $ModsDir $old
    if (Test-Path $p) { Remove-Item $p -Force; Write-Host ("  remove {0}" -f $old) -ForegroundColor Red }
  }
}
@{ managed = $managed; updated = (Get-Date).ToString("o") } | ConvertTo-Json | Set-Content $stateFile

Write-Host "Done. Mods are in sync." -ForegroundColor Green
Write-Host "Reminder: install the Fabric Loader for Minecraft $($manifest.minecraft) once, then play."
if ($Launch) {
  Start-Process "minecraft://" -ErrorAction SilentlyContinue
}
`;
  }

  function pageHtml(base) {
    const mods = listJars();
    const rows = mods
      .map(
        (m) =>
          `<tr><td><a href="${m.url}">${m.name}</a></td><td>${(m.size / 1024).toFixed(0)} KB</td><td class="hash">${m.sha256.slice(0, 12)}…</td></tr>`
      )
      .join("\n");
    return `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Minecraft client mods — sync</title>
<style>
 body{font-family:system-ui,Segoe UI,Roboto,sans-serif;max-width:760px;margin:2rem auto;padding:0 1rem;color:#1b1f24;line-height:1.5}
 h1{font-size:1.4rem} code,kbd{background:#eef1f5;padding:.1em .4em;border-radius:4px}
 table{border-collapse:collapse;width:100%;margin:1rem 0} td,th{border:1px solid #dde2e8;padding:.4rem .6rem;text-align:left;font-size:.92rem}
 .hash{color:#788;font-family:ui-monospace,monospace}
 .cta{display:inline-block;background:#2f6df6;color:#fff;padding:.6rem 1rem;border-radius:8px;text-decoration:none;font-weight:600}
 .note{background:#fff7e6;border:1px solid #f0d9a8;border-radius:8px;padding:.8rem 1rem;margin:1rem 0}
 ol{padding-left:1.2rem}
</style></head><body>
<h1>🛰️ Minecraft client mods</h1>
<p>Keep this PC's mods in sync with the server (Minecraft <b>${minecraft}</b>, Fabric).</p>

<h2>Easy way (auto-sync)</h2>
<ol>
 <li>Install the <b>Fabric Loader for Minecraft ${minecraft}</b> once (<a href="https://fabricmc.net/use/installer/">fabricmc.net</a>).</li>
 <li>Download the updater: <a class="cta" href="/clientmods/Update-Mods.ps1">Update-Mods.ps1</a></li>
 <li>Right-click it → <b>Run with PowerShell</b>. It downloads/updates the mods automatically. Run it again any time to re-sync.</li>
 <li>Launch Minecraft (Fabric ${minecraft}) and connect to the server.</li>
</ol>
<div class="note">The updater only touches mods it manages; any other mods you add are left alone. Source of truth: <code>${base}</code>.</div>

<h2>Manual way</h2>
<p>Drop these jars into <code>%APPDATA%\\.minecraft\\mods</code>:</p>
<table><thead><tr><th>file</th><th>size</th><th>sha256</th></tr></thead><tbody>
${rows || '<tr><td colspan="3">(no mods published yet)</td></tr>'}
</tbody></table>
<p><a href="/clientmods/manifest.json">manifest.json</a></p>
</body></html>`;
  }

  return { available, manifest, filePath, updateScript, pageHtml };
}
