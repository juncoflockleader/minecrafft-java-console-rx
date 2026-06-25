#!/usr/bin/env python3
"""Wish capture daemon. Tails the Fabric server log for player chat starting
with 'wish:' and enqueues each wish (with the player's position) to
~/wishes/queue/<id>.json for a Claude Code 'grant-wishes' agent to build.

Controls:
  - ~/wishes/control  : 'on' | 'off'  (off = capture paused, players told)
  - in-game OP chat   : 'wish: !on' / 'wish: !off' / 'wish: !status'
Run/managed via ~/wishes/bin/wishd {start|stop|restart|status}."""
import socket, struct, time, json, re, os

HOME = os.path.expanduser("~")
BASE = os.path.join(HOME, "wishes")
QUEUE = os.path.join(BASE, "queue")
CONTROL = os.path.join(BASE, "control")
LOGFILE = os.path.join(HOME, "minecraft-fabric", "logs", "latest.log")
OPSFILE = os.path.join(HOME, "minecraft-fabric", "ops.json")
RHOST, RPORT, RPW = "127.0.0.1", 25575, "GU+bvxeYn7dnS7qY"
WISH_RE = re.compile(r"<([A-Za-z0-9_]{1,16})>\s*wish:\s*(.+?)\s*$", re.IGNORECASE)


def rcon(cmd):
    try:
        s = socket.create_connection((RHOST, RPORT), timeout=10)
        rid = 7

        def send(t, body):
            d = struct.pack('<ii', rid, t) + body.encode() + b'\x00\x00'
            s.sendall(struct.pack('<i', len(d)) + d)
            buf = b''
            while len(buf) < 4:
                buf += s.recv(4096)
            ln = struct.unpack('<i', buf[:4])[0]
            while len(buf) < 4 + ln:
                buf += s.recv(4096)
            return buf[12:4 + ln - 2].decode('utf8', 'replace')
        send(3, RPW)
        out = send(2, cmd)
        s.close()
        return out
    except Exception as e:
        log(f"rcon error: {e}")
        return None


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def control_state():
    try:
        return open(CONTROL).read().strip().lower() or "on"
    except Exception:
        return "on"


def set_control(v):
    open(CONTROL, "w").write(v + "\n")


def is_op(name):
    try:
        ops = json.load(open(OPSFILE))
        return any(o.get("name", "").lower() == name.lower() for o in ops)
    except Exception:
        return False


def tellraw(name, text, color="aqua"):
    rcon('tellraw %s {"text":%s,"color":"%s"}' % (name, json.dumps(text), color))


def get_pos(name):
    out = rcon(f'data get entity {name} Pos')
    if not out:
        return None
    m = re.search(r"\[([-0-9.]+)d,\s*([-0-9.]+)d,\s*([-0-9.]+)d\]", out)
    if not m:
        return None
    return [float(m.group(1)), float(m.group(2)), float(m.group(3))]


def get_rot(name):
    out = rcon(f'data get entity {name} Rotation')
    m = re.search(r"\[([-0-9.]+)f,\s*([-0-9.]+)f\]", out or "")
    return float(m.group(1)) if m else 0.0


def handle_wish(player, text):
    text = text.strip()
    # OP control commands: 'wish: !off' etc.
    if text.startswith("!"):
        if not is_op(player):
            tellraw(player, "Only an operator can control the wishing well.", "red")
            return
        cmdw = text[1:].strip().lower()
        if cmdw in ("off", "pause", "stop"):
            set_control("off"); rcon('say [Wishing Well] paused by %s.' % player); log(f"OP {player} -> OFF")
        elif cmdw in ("on", "resume", "start"):
            set_control("on"); rcon('say [Wishing Well] is open! Type: wish: <something>') ; log(f"OP {player} -> ON")
        elif cmdw == "status":
            n = len(os.listdir(QUEUE)) if os.path.isdir(QUEUE) else 0
            tellraw(player, f"Wishing well: {control_state().upper()} — {n} wish(es) queued.", "yellow")
        else:
            tellraw(player, "Wish controls: !on  !off  !status", "yellow")
        return
    # a real wish
    if control_state() != "on":
        tellraw(player, "The wishing well is resting right now — try again later. ✨", "light_purple")
        return
    pos = get_pos(player)
    if not pos:
        tellraw(player, "I couldn't find where you are — make a wish while standing in the Overworld.", "red")
        log(f"no pos for {player}, skipping")
        return
    wid = f"{int(time.time()*1000)}-{player}"
    wish = {"id": wid, "ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "player": player,
            "x": round(pos[0], 1), "y": round(pos[1], 1), "z": round(pos[2], 1),
            "yaw": get_rot(player), "text": text}
    os.makedirs(QUEUE, exist_ok=True)
    json.dump(wish, open(os.path.join(QUEUE, wid + ".json"), "w"), indent=2)
    log(f"queued wish {wid}: {text!r} @ {wish['x']},{wish['y']},{wish['z']}")
    tellraw(player, f"✨ Wish received: “{text}” — granting it soon!", "gold")


def follow():
    log(f"wish tailer started; watching {LOGFILE}")
    f = None
    inode = None
    while True:
        try:
            if f is None:
                if not os.path.exists(LOGFILE):
                    time.sleep(1); continue
                f = open(LOGFILE, "r", errors="replace")
                inode = os.fstat(f.fileno()).st_ino
                f.seek(0, 2)  # start at end: only new lines
            line = f.readline()
            if not line:
                # detect rotation/truncation
                try:
                    st = os.stat(LOGFILE)
                    if st.st_ino != inode or st.st_size < f.tell():
                        log("log rotated; reopening"); f.close(); f = None; continue
                except FileNotFoundError:
                    f.close(); f = None
                time.sleep(0.5); continue
            m = WISH_RE.search(line)
            if m:
                try:
                    handle_wish(m.group(1), m.group(2))
                except Exception as e:
                    log(f"handle_wish error: {e}")
        except Exception as e:
            log(f"loop error: {e}"); time.sleep(2); f = None


if __name__ == "__main__":
    os.makedirs(QUEUE, exist_ok=True)
    if not os.path.exists(CONTROL):
        set_control("on")
    follow()
