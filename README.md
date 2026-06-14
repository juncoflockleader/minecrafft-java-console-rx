# minecrafft-java-console-rx

A lightweight web UI to control a **Minecraft Java** server (Paper / Spigot / Vanilla) over **RCON**, with **live log streaming** and a server **status panel**. No build step, minimal dependencies (`express` + `ws`).

## Features

- **Interactive console** — send any server command over RCON (`op`, `gamemode`, `time set`, `give`, `whitelist`, `say`, …) and see the response, rendered with Minecraft `§` color codes.
- **Live log stream** — tails the server log file over a WebSocket; new lines appear in real time, with recent history replayed on connect.
- **Status panel** — version, online/max players, and MOTD via the Minecraft Server List Ping (no RCON needed).
- **Whitelist manager** — toggle the whitelist on/off and add/remove players (over RCON, applied live).
- **Plugin manager** — list installed plugins, enable/disable (`.jar` ⇄ `.jar.disabled`), delete, and **install** from a [Modrinth](https://modrinth.com) slug (auto-resolves the newest build for your server version) or a direct `.jar` URL.
- **Settings editor** — edit common `server.properties` keys (difficulty, gamemode, view-distance, PvP, …) with friendly controls.
- **Mod manager** — same install/manage flow for Fabric/Forge **mods**, activated when the server has a `mods/` directory (or `MC_MODS_DIR` is set). On a Paper/Bukkit server the Mods tab explains that the server uses plugins instead.
- **Restart button** — runs an operator-configured command (e.g. `launchctl kickstart`) to restart the server.
- **Optional HTTP Basic Auth** — gate the UI (and the WebSocket) behind a username/password.

> **Plugins vs mods:** Paper/Spigot/Bukkit servers load **plugins**; Fabric/Forge servers load **mods**. They are not interchangeable. This tool manages plugins by default and unlocks the Mods panel only on a modded server.

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
| `MC_SERVER_DIR` | _(empty)_ | Server install dir — enables the plugins / mods / settings panels (`<dir>/plugins`, `<dir>/mods`, `<dir>/server.properties`) |
| `MC_PLUGINS_DIR` | `<MC_SERVER_DIR>/plugins` | Override the plugins directory |
| `MC_MODS_DIR` | `<MC_SERVER_DIR>/mods` | Override the mods directory; setting it force-enables the Mods panel |
| `MC_RESTART_COMMAND` | _(empty)_ | Shell command the "Restart" button runs (e.g. `sudo launchctl kickstart -k system/com.junco.minecraft`) |
| `WEBUI_USER` / `WEBUI_PASSWORD` | _(empty)_ | Enable Basic Auth when both set |

> **Tip:** run this *on the same host* as the Minecraft server so it can reach RCON over `127.0.0.1` and read the local log file. If you expose the UI beyond localhost (`HOST=0.0.0.0`), set `WEBUI_USER`/`WEBUI_PASSWORD`.

## HTTP / WebSocket API

- `GET /api/status` → `{ online, version, protocol, players:{online,max}, motd }`
- `GET /api/capabilities` → which panels are available + detected `version`/`gameVersion`
- `POST /api/command` `{ "command": "list" }` → `{ command, response }`
- `GET /api/whitelist` · `POST /api/whitelist/add|remove` `{ name }` · `POST /api/whitelist/enabled` `{ enabled }`
- `GET /api/properties` · `POST /api/properties` `{ patch: { key: value } }`
- `GET /api/plugins` · `POST /api/plugins/install` `{ slug | url, gameVersion? }` · `POST /api/plugins/toggle` `{ name, enabled }` · `POST /api/plugins/remove` `{ name }`
- `GET /api/mods` … (same shape as plugins; `409` when the server isn't modded)
- `POST /api/server/restart` → runs `MC_RESTART_COMMAND`
- `WS /ws` — messages from server: `history`, `log`, `echo`, `response`, `error`, `system`; send `{ "type":"command", "command":"..." }`.

## Running as a service

Point `MC_LOG_PATH` at the server's log and keep it alive with your process manager of choice (launchd on macOS, systemd on Linux, `pm2`, etc.). Example launchd/systemd snippets live in [`docs/`](docs/).

## Security notes

- RCON traffic is unencrypted; keep RCON on `localhost` or a trusted network.
- This tool can run **any** server command — protect it with Basic Auth and/or a reverse proxy with TLS if reachable beyond your LAN.

## License

MIT
