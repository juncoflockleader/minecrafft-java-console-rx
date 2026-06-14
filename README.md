# minecrafft-java-console-rx

A lightweight web UI to control a **Minecraft Java** server (Paper / Spigot / Vanilla) over **RCON**, with **live log streaming** and a server **status panel**. No build step, minimal dependencies (`express` + `ws`).

## Features

- **Interactive console** — send any server command over RCON (`op`, `gamemode`, `time set`, `give`, `whitelist`, `say`, …) and see the response, rendered with Minecraft `§` color codes.
- **Live log stream** — tails the server log file over a WebSocket; new lines appear in real time, with recent history replayed on connect.
- **Status panel** — version, online/max players, and MOTD via the Minecraft Server List Ping (no RCON needed).
- **Quick actions** — one-click buttons for common commands.
- **Optional HTTP Basic Auth** — gate the UI (and the WebSocket) behind a username/password.

## Requirements

- Node.js ≥ 18
- A Minecraft Java server with **RCON enabled** in `server.properties`:
  ```properties
  enable-rcon=true
  rcon.port=25575
  rcon.password=your-strong-password
  broadcast-rcon-to-ops=true
  ```

## Setup

```bash
npm install
cp .env.example .env   # then edit .env
npm start
```

Open the printed URL (default `http://127.0.0.1:8765`).

### Configuration (`.env`)

| Variable | Default | Purpose |
| --- | --- | --- |
| `HOST` | `127.0.0.1` | Web UI bind address (`0.0.0.0` to expose on LAN) |
| `PORT` | `8765` | Web UI port |
| `RCON_HOST` | `127.0.0.1` | RCON host |
| `RCON_PORT` | `25575` | RCON port |
| `RCON_PASSWORD` | _(required)_ | RCON password |
| `MC_HOST` | `RCON_HOST` | Server List Ping host |
| `MC_PORT` | `25565` | Server List Ping port |
| `MC_LOG_PATH` | _(empty)_ | Path to `logs/latest.log` for live streaming (optional) |
| `WEBUI_USER` / `WEBUI_PASSWORD` | _(empty)_ | Enable Basic Auth when both set |

> **Tip:** run this *on the same host* as the Minecraft server so it can reach RCON over `127.0.0.1` and read the local log file. If you expose the UI beyond localhost (`HOST=0.0.0.0`), set `WEBUI_USER`/`WEBUI_PASSWORD`.

## HTTP / WebSocket API

- `GET /api/status` → `{ online, version, protocol, players:{online,max}, motd }`
- `POST /api/command` `{ "command": "list" }` → `{ command, response }`
- `WS /ws` — messages from server: `history`, `log`, `echo`, `response`, `error`, `system`; send `{ "type":"command", "command":"..." }`.

## Running as a service

Point `MC_LOG_PATH` at the server's log and keep it alive with your process manager of choice (launchd on macOS, systemd on Linux, `pm2`, etc.). Example launchd/systemd snippets live in [`docs/`](docs/).

## Security notes

- RCON traffic is unencrypted; keep RCON on `localhost` or a trusted network.
- This tool can run **any** server command — protect it with Basic Auth and/or a reverse proxy with TLS if reachable beyond your LAN.

## License

MIT
