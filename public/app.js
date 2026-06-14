const consoleEl = document.getElementById("console");
const form = document.getElementById("prompt");
const input = document.getElementById("input");

const esc = (s) =>
  String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

async function api(path, opts = {}) {
  const res = await fetch(path, { headers: { "content-type": "application/json" }, ...opts });
  let data = null;
  try { data = await res.json(); } catch {}
  if (!res.ok) throw new Error(data?.error || `HTTP ${res.status}`);
  return data;
}
const post = (path, body) => api(path, { method: "POST", body: JSON.stringify(body || {}) });

// ===== Console (WebSocket) =====
const COLORS = {
  "0": "#000", "1": "#0000aa", "2": "#00aa00", "3": "#00aaaa", "4": "#aa0000",
  "5": "#aa00aa", "6": "#ffaa00", "7": "#aaaaaa", "8": "#555", "9": "#5555ff",
  a: "#55ff55", b: "#55ffff", c: "#ff5555", d: "#ff55ff", e: "#ffff55", f: "#fff",
};
function renderColored(parent, text) {
  const parts = text.split("§");
  parent.appendChild(document.createTextNode(parts[0]));
  for (let i = 1; i < parts.length; i++) {
    const seg = parts[i];
    if (!seg) continue;
    const code = seg[0].toLowerCase();
    const rest = seg.slice(1);
    if (COLORS[code]) {
      const span = document.createElement("span");
      span.style.color = COLORS[code];
      span.textContent = rest;
      parent.appendChild(span);
    } else {
      parent.appendChild(document.createTextNode(rest));
    }
  }
}
function addLine(text, cls = "") {
  const atBottom = consoleEl.scrollHeight - consoleEl.scrollTop - consoleEl.clientHeight < 40;
  for (const raw of String(text).split("\n")) {
    const line = document.createElement("div");
    line.className = "line" + (cls ? " " + cls : "");
    renderColored(line, raw);
    consoleEl.appendChild(line);
  }
  while (consoleEl.childElementCount > 2000) consoleEl.removeChild(consoleEl.firstChild);
  if (atBottom) consoleEl.scrollTop = consoleEl.scrollHeight;
}

let ws;
let reconnectTimer;
function connect() {
  const proto = location.protocol === "https:" ? "wss" : "ws";
  ws = new WebSocket(`${proto}://${location.host}/ws`);
  ws.onopen = () => setConn(true);
  ws.onclose = () => {
    setConn(false);
    clearTimeout(reconnectTimer);
    reconnectTimer = setTimeout(connect, 2000);
  };
  ws.onerror = () => ws.close();
  ws.onmessage = (ev) => {
    let msg;
    try { msg = JSON.parse(ev.data); } catch { return; }
    switch (msg.type) {
      case "history": msg.lines.forEach((l) => addLine(l)); break;
      case "log": addLine(msg.line); break;
      case "echo": addLine(msg.line, "echo"); break;
      case "response": if (msg.line.trim()) addLine(msg.line, "resp"); break;
      case "error": addLine("⚠ " + msg.line, "err"); break;
      case "system": addLine(msg.line, "system"); break;
    }
  };
}
function setConn(on) {
  const pill = document.getElementById("pill-conn");
  pill.dataset.state = on ? "on" : "off";
  pill.textContent = on ? "connected" : "disconnected";
}
function sendCommand(command) {
  if (!command) return;
  if (ws && ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ type: "command", command }));
  else addLine("⚠ not connected", "err");
}

const history = [];
let histIdx = -1;
form.addEventListener("submit", (e) => {
  e.preventDefault();
  const command = input.value.trim();
  if (!command) return;
  history.push(command);
  if (history.length > 100) history.shift();
  histIdx = history.length;
  sendCommand(command);
  input.value = "";
});
input.addEventListener("keydown", (e) => {
  if (e.key === "ArrowUp" && histIdx > 0) { histIdx--; input.value = history[histIdx]; e.preventDefault(); }
  else if (e.key === "ArrowDown") {
    if (histIdx < history.length - 1) { histIdx++; input.value = history[histIdx]; }
    else { histIdx = history.length; input.value = ""; }
    e.preventDefault();
  }
});
document.getElementById("quick").addEventListener("click", (e) => {
  const cmd = e.target?.dataset?.cmd;
  if (cmd) { sendCommand(cmd); input.focus(); }
});

// ===== status =====
async function pollStatus() {
  try {
    const s = await api("/api/status");
    const pv = document.getElementById("pill-version");
    const pp = document.getElementById("pill-players");
    const pm = document.getElementById("pill-motd");
    if (s.online) {
      pv.textContent = s.version || "online";
      pp.textContent = `${s.players.online}/${s.players.max} players`;
      pm.textContent = (s.motd || "").replace(/§./g, "").trim();
    } else {
      pv.textContent = "server offline";
      pp.textContent = "—";
      pm.textContent = "";
    }
  } catch {}
}

// ===== capabilities + restart =====
let caps = {};
async function loadCaps() {
  try { caps = await api("/api/capabilities"); } catch { caps = {}; }
  const rb = document.getElementById("restart-btn");
  rb.hidden = !caps.restart;
}
document.getElementById("restart-btn").onclick = async () => {
  if (!confirm("Restart the Minecraft server now?")) return;
  try { await post("/api/server/restart"); addLine("⟳ restart requested", "system"); }
  catch (e) { alert("Restart failed: " + e.message); }
};

// ===== whitelist =====
async function loadWhitelist() {
  const wl = await api("/api/whitelist");
  const enabled = document.getElementById("wl-enabled");
  enabled.checked = wl.enabled === true;
  enabled.indeterminate = wl.enabled === null;
  const list = document.getElementById("wl-list");
  list.innerHTML = "";
  if (!wl.players.length) { list.innerHTML = '<li class="muted">no whitelisted players</li>'; return; }
  for (const name of wl.players) {
    const li = document.createElement("li");
    li.innerHTML = `<span class="name">${esc(name)}</span>`;
    const actions = document.createElement("div");
    actions.className = "actions";
    const btn = document.createElement("button");
    btn.className = "ghost";
    btn.textContent = "Remove";
    btn.onclick = async () => { await post("/api/whitelist/remove", { name }); loadWhitelist(); };
    actions.appendChild(btn);
    li.appendChild(actions);
    list.appendChild(li);
  }
}
document.getElementById("wl-enabled").addEventListener("change", async (e) => {
  try { await post("/api/whitelist/enabled", { enabled: e.target.checked }); } catch (err) { alert(err.message); }
  loadWhitelist();
});
document.getElementById("wl-add-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const el = document.getElementById("wl-name");
  const name = el.value.trim();
  if (!name) return;
  try { await post("/api/whitelist/add", { name }); el.value = ""; loadWhitelist(); }
  catch (err) { alert(err.message); }
});

// ===== jar panels (plugins + mods share this) =====
function jarPanel({ kind, listEl, installForm, sourceInput, refreshBtn }) {
  async function load() {
    let data;
    try { data = await api(`/api/${kind}`); }
    catch (e) { listEl.innerHTML = `<li class="muted">${esc(e.message)}</li>`; return; }
    listEl.innerHTML = "";
    if (!data.items.length) { listEl.innerHTML = `<li class="muted">no ${kind} installed</li>`; return; }
    for (const it of data.items) {
      const li = document.createElement("li");
      if (!it.enabled) li.className = "disabled";
      li.innerHTML = `<span class="name">${esc(it.name)} <span class="tag">${(it.size / 1048576).toFixed(1)} MB</span></span>`;
      const actions = document.createElement("div");
      actions.className = "actions";
      const toggle = document.createElement("button");
      toggle.className = "ghost";
      toggle.textContent = it.enabled ? "Disable" : "Enable";
      toggle.onclick = async () => { try { await post(`/api/${kind}/toggle`, { name: it.name, enabled: !it.enabled }); load(); } catch (e) { alert(e.message); } };
      const del = document.createElement("button");
      del.className = "danger";
      del.textContent = "Delete";
      del.onclick = async () => { if (confirm(`Delete ${it.name}?`)) { await post(`/api/${kind}/remove`, { name: it.name }); load(); } };
      actions.append(toggle, del);
      li.appendChild(actions);
      listEl.appendChild(li);
    }
  }
  installForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const v = sourceInput.value.trim();
    if (!v) return;
    const body = /^https?:\/\//i.test(v) ? { url: v } : { slug: v };
    const btn = installForm.querySelector("button");
    const old = btn.textContent;
    btn.textContent = "Installing…";
    btn.disabled = true;
    try {
      const r = await post(`/api/${kind}/install`, body);
      sourceInput.value = "";
      await load();
      alert(`Installed ${r.installed.name}${r.installed.version ? ` (${r.installed.version})` : ""}. Restart the server to load it.`);
    } catch (err) {
      alert("Install failed: " + err.message);
    } finally {
      btn.textContent = old;
      btn.disabled = false;
    }
  });
  if (uploadForm && fileInput) {
    uploadForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const f = fileInput.files[0];
      if (!f) return;
      const btn = uploadForm.querySelector("button");
      const old = btn.textContent;
      btn.textContent = "Uploading…";
      btn.disabled = true;
      try {
        const r = await fetch(`/api/${kind}/upload?name=${encodeURIComponent(f.name)}`, {
          method: "POST",
          headers: { "content-type": "application/java-archive" },
          body: f,
        });
        const d = await r.json().catch(() => ({}));
        if (!r.ok) throw new Error(d.error || `HTTP ${r.status}`);
        fileInput.value = "";
        await load();
        alert(`Uploaded ${d.installed.name}. Restart the server to load it.`);
      } catch (err) {
        alert("Upload failed: " + err.message);
      } finally {
        btn.textContent = old;
        btn.disabled = false;
      }
    });
  }
  if (refreshBtn) refreshBtn.onclick = load;
  return { load };
}

const pluginsPanel = jarPanel({
  kind: "plugins",
  listEl: document.getElementById("pl-list"),
  installForm: document.getElementById("pl-install-form"),
  sourceInput: document.getElementById("pl-source"),
  refreshBtn: document.getElementById("pl-refresh"),
  uploadForm: document.getElementById("pl-upload-form"),
  fileInput: document.getElementById("pl-file"),
});

// ===== settings =====
async function loadSettings() {
  const grid = document.getElementById("set-grid");
  let data;
  try { data = await api("/api/properties"); }
  catch (e) { grid.innerHTML = `<p class="notice">${esc(e.message)}</p>`; return; }
  grid.innerHTML = "";
  for (const c of data.curated) {
    const field = document.createElement("div");
    field.className = "field";
    const id = "prop-" + c.key;
    let inputEl;
    if (c.type === "bool") {
      inputEl = document.createElement("select");
      ["true", "false"].forEach((o) => inputEl.add(new Option(o, o)));
      inputEl.value = data.all[c.key] ?? "false";
    } else if (c.type === "enum") {
      inputEl = document.createElement("select");
      c.options.forEach((o) => inputEl.add(new Option(o, o)));
      inputEl.value = data.all[c.key] ?? c.options[0];
    } else {
      inputEl = document.createElement("input");
      inputEl.type = c.type === "int" ? "number" : "text";
      inputEl.value = data.all[c.key] ?? "";
    }
    inputEl.id = id;
    inputEl.dataset.key = c.key;
    const label = document.createElement("label");
    label.textContent = `${c.label} (${c.key})`;
    label.htmlFor = id;
    field.append(label, inputEl);
    grid.appendChild(field);
  }
}
document.getElementById("set-refresh").onclick = loadSettings;
document.getElementById("set-save").onclick = async () => {
  const patch = {};
  document.querySelectorAll("#set-grid [data-key]").forEach((i) => (patch[i.dataset.key] = i.value));
  const st = document.getElementById("set-status");
  st.textContent = "saving…";
  try { await post("/api/properties", { patch }); st.textContent = "saved — restart to apply"; }
  catch (e) { st.textContent = "error: " + e.message; }
};

// ===== mods (capability-gated) =====
function renderModsPanel() {
  const c = document.getElementById("mods-content");
  if (!caps.mods) {
    c.innerHTML = `<div class="card"><h2>Mods</h2><p class="notice">This server reports <strong>${esc(caps.version || "Paper/Bukkit")}</strong>, which loads <strong>plugins</strong>, not Fabric/Forge <strong>mods</strong>. Use the <strong>Plugins</strong> tab.<br><br>To manage mods, run a Fabric/Forge server and set <code>MC_MODS_DIR</code> — this panel then installs mods from Modrinth or a URL.</p></div>`;
    return;
  }
  c.innerHTML =
    `<div class="card"><h2>Install mod</h2>` +
    `<form class="row" id="mod-install-form"><input id="mod-source" placeholder="Modrinth slug or https://…/mod.jar" autocomplete="off"/><button type="submit">Install</button></form>` +
    `<form class="row" id="mod-upload-form"><input type="file" id="mod-file" accept=".jar"/><button type="submit">Upload .jar</button></form>` +
    `<p class="hint">Install from Modrinth/URL, or upload your own <code>.jar</code> (e.g. a mod you built). Loads on next restart.</p></div>` +
    `<div class="card"><div class="row spread"><h2>Installed mods</h2><button class="ghost" id="mod-refresh">Refresh</button></div><ul class="list" id="mod-list"></ul></div>`;
  jarPanel({
    kind: "mods",
    listEl: c.querySelector("#mod-list"),
    installForm: c.querySelector("#mod-install-form"),
    sourceInput: c.querySelector("#mod-source"),
    refreshBtn: c.querySelector("#mod-refresh"),
    uploadForm: c.querySelector("#mod-upload-form"),
    fileInput: c.querySelector("#mod-file"),
  }).load();
}

// ===== tabs =====
const onOpen = {
  whitelist: loadWhitelist,
  plugins: () => pluginsPanel.load(),
  settings: loadSettings,
  mods: renderModsPanel,
};
document.getElementById("tabs").addEventListener("click", (e) => {
  const tab = e.target?.dataset?.tab;
  if (tab) activateTab(tab);
});
function activateTab(tab) {
  document.querySelectorAll("#tabs button").forEach((b) => b.classList.toggle("active", b.dataset.tab === tab));
  document.querySelectorAll(".panel").forEach((p) => p.classList.toggle("active", p.id === "panel-" + tab));
  if (onOpen[tab]) onOpen[tab]();
}

// ===== boot =====
connect();
pollStatus();
setInterval(pollStatus, 5000);
loadCaps();
input.focus();
