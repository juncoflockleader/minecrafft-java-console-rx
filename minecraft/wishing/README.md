# 🌟 Wishing Well (MVP) — AI wish-granting for the Minecraft server

A player makes a wish in-game; a **sibling Claude Code session** reads it and builds it.

```
in-game chat:  wish: a giant panda statue
      │
 wish_tailer.py  (daemon on the mini — tails the log, captures player + position)
      │  writes ~/wishes/queue/<id>.json   and tells the player "✨ received"
      ▼
 SIBLING Claude Code session:  /loop /grant-wishes
      │  reads the queue → designs + builds via RCON → verifies → tellraw → done/
      ▼
```

## How a player wishes
Stand where you want it and type in chat:
```
wish: a giant panda statue
```
(Anything starting with `wish:` — it's built a few blocks in front of you.)

## Run the granter (the sibling session)
1. Open a **new Claude Code session** in this repo (`minecrafft-java-console-rx`).
2. Start the loop:
   ```
   /loop /grant-wishes
   ```
   It drains `~/wishes/queue/` every ~20–30s, builds each wish, notifies the player, and moves it to `~/wishes/done/`.
   Keep this session separate from your "design" session.

## Easy stop / restart (three ways)
| Where | Pause/resume capture+granting | Fully stop / restart capture |
|---|---|---|
| **In-game (op)** | `wish: !off` / `wish: !on` (and `wish: !status`) | — |
| **Terminal (mini)** | `~/wishes/bin/wishctl off` / `on` / `status` | `~/wishes/bin/wishd stop` / `start` / `restart` / `status` |
| **The granter** | — | stop the `/loop` in the sibling session; restart with `/loop /grant-wishes` |

- `wishctl off` = the well "rests": players are told it's closed, the granter idles, the daemon keeps running.
- `wishd stop` = kills the capture daemon entirely.
- These are independent: you can pause granting (`wishctl off`) while leaving capture running, or stop capture while a session drains the backlog.

## Files
- **On the mini:** `~/wishes/{queue,done,backup}/`, `~/wishes/control` (`on`/`off`), `~/wishes/bin/{wish_tailer.py,wishd,wishctl}`, `~/wishes/wishd.log`.
- **In this repo:** `minecraft/wishing/` (the scripts) and `.claude/commands/grant-wishes.md` (the granter's instructions).

## Guardrails
Builds are bounded to a ~48³ box near the player, snapshotted (`clone` to x+6000) for undo, kid-friendly only, and never run admin/destructive commands. See `grant-wishes.md`.

## Not yet (easy upgrades)
- Real `/wish <text>` command in the arsenal mod (instead of chat-tailing) — needs a local mod rebuild.
- `wishd` as a launchd service for reboot-durability (currently `nohup`).
- `/unwish` to restore the last snapshot.

## Install note
`.claude/` is gitignored, so the slash command's source of truth lives at
`minecraft/wishing/grant-wishes.md`. After a fresh clone, install it with:
```
cp minecraft/wishing/grant-wishes.md .claude/commands/grant-wishes.md
```
(It's already installed in this working copy.)
