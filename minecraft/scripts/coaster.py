#!/usr/bin/env python3
"""Giant looping rollercoaster (pure blocks, no mod).

A rideable powered rectangular circuit a minecart loops around forever, a big
hill, and a GIANT decorative vertical loop the track runs through (vanilla rails
can't ride a real vertical loop, so the loop is a block showpiece). Themed
red/white supports on a plaza, with a station + minecart + lights.
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
def fill(a, b, c, d, e, f, bl): return cmd(f"fill {a} {b} {c} {d} {e} {f} {bl}")
def sb(x, y, z, bl): return cmd(f"setblock {x} {y} {z} {bl}")

CX, CZ = 285, 45
TY = 80                 # rail level
BED = TY - 1            # 79 (track bed)
BASE = 62               # ground
X0, X1 = 265, 305       # circuit footprint
Z0, Z1 = 33, 57

cmd("forceload add 258 28 320 64")

# --- 1) clear the build volume + plaza ---
fill(X0 - 4, BASE + 1, Z0 - 4, X1 + 4, 108, Z1 + 4, "air")
fill(X0 - 4, BASE, Z0 - 4, X1 + 4, BASE, Z1 + 4, "gray_concrete")            # plaza
fill(X0 - 4, BASE, Z0 - 4, X1 + 4, BASE, Z0 - 4, "smooth_quartz")            # plaza trim
fill(X0 - 4, BASE, Z1 + 4, X1 + 4, BASE, Z1 + 4, "smooth_quartz")

# --- 2) themed support pillar ---
def pillar(x, z, topY):
    for y in range(BASE + 1, topY + 1):
        sb(x, y, z, "red_concrete" if (y % 4 < 2) else "white_concrete")

# --- 3) rideable circuit: powered straights + curved corners ---
def powered(x, z):
    sb(x, BED, z, "redstone_block")
    sb(x, TY, z, "powered_rail")
def corner(x, z):
    sb(x, BED, z, "smooth_stone")
    sb(x, TY, z, "rail")
# straights (powered), laid in order so rails orient cleanly
for x in range(X0 + 1, X1):
    powered(x, Z0); powered(x, Z1)
for z in range(Z0 + 1, Z1):
    powered(X0, z); powered(X1, z)
for (cx, cz) in [(X0, Z0), (X1, Z0), (X0, Z1), (X1, Z1)]:
    corner(cx, cz)
# track-bed support pillars every 6 blocks
for x in range(X0, X1 + 1, 6):
    pillar(x, Z0, BED - 1); pillar(x, Z1, BED - 1)
for z in range(Z0, Z1 + 1, 6):
    pillar(X0, z, BED - 1); pillar(X1, z, BED - 1)

# --- 4) GIANT VERTICAL LOOP (decorative) straddling the front straight (Z0) ---
R = 12
LCY = BED + R                                   # loop centre y (91); bottom at BED
for deg in range(0, 360, 3):
    a = math.radians(deg)
    x = CX + int(round(R * math.cos(a)))
    y = LCY + int(round(R * math.sin(a)))
    sb(x, y, Z0 - 1, "red_concrete")            # two parallel rails straddling the track
    sb(x, y, Z0 + 1, "red_concrete")
    if deg % 21 == 0:
        fill(x, y, Z0 - 1, x, y, Z0 + 1, "white_concrete")   # cross-ties
# loop legs (A-frame) to the plaza
for (lx, ly) in [(CX - 11, LCY - 5), (CX + 11, LCY - 5)]:
    for y in range(BASE + 1, ly + 1):
        sb(lx, y, Z0 - 1, "white_concrete"); sb(lx, y, Z0 + 1, "white_concrete")
for y in range(BASE + 1, BED):                  # centre column under loop bottom
    sb(CX, y, Z0 - 1, "iron_block"); sb(CX, y, Z0 + 1, "iron_block")

# --- 5) station on the back straight (Z1) ---
fill(CX - 4, BED, Z1 + 1, CX + 4, BED, Z1 + 3, "polished_andesite")          # platform
fill(CX - 4, BED + 1, Z1 + 3, CX + 4, BED + 1, Z1 + 3, "oak_fence")          # railing
cmd(f"setblock {CX} {BED} {Z1 + 2} oak_wall_sign[facing=south]{{front_text:{{messages:['\"LOOP COASTER\"','\"right-click the\"','\"cart to ride\"','\"\"']}}}}")
cmd(f"summon minecart {CX}.5 {TY} {Z1}.5")

# --- 6) lights ---
for x in range(X0, X1 + 1, 8):
    sb(x, BED, Z0, "sea_lantern"); sb(x, BED, Z1, "sea_lantern")
for deg in (45, 135, 90):
    a = math.radians(deg)
    sb(CX + int(round(R * math.cos(a))), LCY + int(round(R * math.sin(a))), Z0, "sea_lantern")

cmd("forceload remove all")
print("COASTER DONE")
print("rail at station (285,80,57):", cmd(f"execute if block {CX} {TY} {Z1} #minecraft:rails"))
print("loop top (285,103,32) red:", cmd(f"execute if block {CX} {LCY + R} {Z0 - 1} minecraft:red_concrete"))
print("minecart present:", cmd("execute if entity @e[type=minecart]"))
