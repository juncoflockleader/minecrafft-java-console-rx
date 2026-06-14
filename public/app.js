const consoleEl = document.getElementById("console");
const form = document.getElementById("prompt");
const input = document.getElementById("input");

// Minecraft §-color codes -> CSS colors. Formatting codes (k,l,m,n,o,r) are stripped.
const COLORS = {
  "0": "#000000", "1": "#0000aa", "2": "#00aa00", "3": "#00aaaa",
  "4": "#aa0000", "5": "#aa00aa", "6": "#ffaa00", "7": "#aaaaaa",
  "8": "#555555", "9": "#5555ff", a: "#55ff55", b: "#55ffff",
  c: "#ff5555", d: "#ff55ff", e: "#ffff55", f: "#ffffff",
};

// Render a string containing §-codes into colored spans appended to `parent`.
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
      parent.appendChild(document.createTextNode(rest)); // drop formatting codes
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
  // Cap DOM size.
  while (consoleEl.childElementCount > 2000) consoleEl.removeChild(consoleEl.firstChild);
  if (atBottom) consoleEl.scrollTop = consoleEl.scrollHeight;
}

// ---- WebSocket console ----
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
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: "command", command }));
  } else {
    addLine("⚠ not connected", "err");
  }
}

// ---- command input + history ----
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
  if (e.key === "ArrowUp") {
    if (histIdx > 0) { histIdx--; input.value = history[histIdx]; e.preventDefault(); }
  } else if (e.key === "ArrowDown") {
    if (histIdx < history.length - 1) { histIdx++; input.value = history[histIdx]; }
    else { histIdx = history.length; input.value = ""; }
    e.preventDefault();
  }
});

document.getElementById("quick").addEventListener("click", (e) => {
  const cmd = e.target?.dataset?.cmd;
  if (cmd) { sendCommand(cmd); input.focus(); }
});

// ---- status polling (SLP) ----
async function pollStatus() {
  try {
    const r = await fetch("/api/status");
    const s = await r.json();
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
  } catch {
    /* ignore */
  }
}

connect();
pollStatus();
setInterval(pollStatus, 5000);
input.focus();
