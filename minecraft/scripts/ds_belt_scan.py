#!/usr/bin/env python3
"""Scan the Death Star's exterior shell around the equator and report the
surface block by latitude (y) and angle. Read-only.

Usage: ds_belt_scan.py <y0> <y1>   (e.g. 135 145)
Codes: .=air I=iron_block K=black_concrete G=gray_concrete
       L=light_gray_concrete Y=yellow_terracotta ?=other-solid
"""
import socket, struct, sys, math
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
CANDS = [("minecraft:air", "."), ("minecraft:iron_block", "I"),
         ("minecraft:black_concrete", "K"), ("minecraft:gray_concrete", "G"),
         ("minecraft:light_gray_concrete", "L"), ("minecraft:yellow_terracotta", "Y")]
def classify(x, y, z):
    for b, c in CANDS:
        if isb(x, y, z, b):
            return c
    return "?"
y0, y1 = int(sys.argv[1]), int(sys.argv[2])
cmd("forceload add 70 90 170 162")
step = 4  # degrees
print("    angle: " + "".join(str((a // 10) % 10) if a % 10 == 0 else " " for a in range(0, 360, step)))
for y in range(y0, y1 + 1):
    row = []
    for a in range(0, 360, step):
        rad = math.radians(a)
        found = "."
        for R in range(51, 43, -1):  # march inward, first solid = surface
            x = CX + int(round(R * math.cos(rad)))
            z = CZ + int(round(R * math.sin(rad)))
            c = classify(x, y, z)
            if c != ".":
                found = c
                break
        row.append(found)
    print(f"y{y:>3} " + "".join(row))
cmd("forceload remove all")
print("(angle 0=+x/east toward dish; 90=+z/south; 180=-x/west; 270=-z/north)")
