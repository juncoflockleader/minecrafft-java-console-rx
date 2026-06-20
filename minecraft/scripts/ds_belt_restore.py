#!/usr/bin/env python3
"""Restore the Death Star's exterior 'black belt': the equatorial trench
back-wall (y138-142) was turned yellow_terracotta by the backrooms reskin.
Recolor ONLY the outermost shell-facing run back to black_concrete, so the
interior backrooms maze (which is also yellow, but deeper) is left untouched.

Per angle, march inward from R=51; skip the recess (air); on the first solid
run, convert any yellow_terracotta -> black_concrete for up to 3 cells, then
stop at the air gap behind the wall.
"""
import socket, struct, math
HOST, PORT, PW = "127.0.0.1", 25575, "GU+bvxeYn7dnS7qY"
s = socket.create_connection((HOST, PORT), timeout=30); _id = 0
def raw(t, b):
    global _id; _id += 1; rid = _id
    d = struct.pack('<ii', rid, t) + b.encode() + b'\x00\x00'
    s.sendall(struct.pack('<i', len(d)) + d); buf = b''
    while True:
        while len(buf) < 4: buf += s.recv(8192)
        ln = struct.unpack('<i', buf[:4])[0]
        while len(buf) < 4 + ln: buf += s.recv(8192)
        pid = struct.unpack('<i', buf[4:8])[0]
        body = buf[12:4 + ln - 2].decode('utf8', 'replace'); buf = buf[4 + ln:]
        if pid == rid: return body
raw(3, PW)
def cmd(c): return raw(2, c)
def isb(x, y, z, b): return "passed" in cmd(f"execute if block {x} {y} {z} {b}")
CX, CZ = 120, 112
YBAND = range(138, 143)        # trench back-wall band
fixed = 0
cmd("forceload add 70 90 170 162")
for ai in range(0, 720):       # 0.5-degree steps (idempotent on dup cells)
    rad = math.radians(ai * 0.5)
    cos, sin = math.cos(rad), math.sin(rad)
    for y in YBAND:
        started = False; depth = 0; last = None
        for R10 in range(510, 399, -5):   # R 51.0 -> 40.0 in 0.5 steps
            R = R10 / 10.0
            x = CX + int(round(R * cos)); z = CZ + int(round(R * sin))
            if (x, y, z) == last:
                continue
            last = (x, y, z)
            if isb(x, y, z, "minecraft:air"):
                if started:
                    break                  # behind the wall -> stop (spare interior)
                continue                    # still in the recess
            started = True; depth += 1
            if isb(x, y, z, "minecraft:yellow_terracotta"):
                cmd(f"setblock {x} {y} {z} black_concrete"); fixed += 1
            if depth >= 3:
                break
cmd("forceload remove all")
print(f"belt restore done; converted {fixed} yellow cells -> black_concrete")
