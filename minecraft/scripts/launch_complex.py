#!/usr/bin/env python3
"""Large, detailed Space Shuttle LAUNCH COMPLEX east of the apartment district.
  - leveled concrete apron w/ markings + flame trench
  - Mobile Launcher Platform (raised, flame holes over the trench)
  - Fixed Service Structure (steel lattice tower) w/ access arms, white room,
    GOX 'beanie cap' arm, hammerhead crane, lightning mast
  - lightning catenary masts, sound-suppression water tower, LOX/LH2 spheres
  - full vertical stack: External Tank (orange) + 2 SRBs (white, nosecones)
    + Orbiter (white/black, delta wings, tail, 3 SSME nozzles, OMS pods, cockpit)
Stack center (ET) x350 z165; ground y66; MLP deck y74."""
import socket, struct
HOST, PORT, PW = "127.0.0.1", 25575, "GU+bvxeYn7dnS7qY"
s = socket.create_connection((HOST, PORT), timeout=120); _id = 0
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
def col(x, z, y0, y1, bl): return fill(x, y0, z, x, y1, z, bl)
def octprism(cx, cz, r, y0, y1, bl, ch=None):     # solid octagonal column
    if ch is None: ch = 1 if r <= 2 else 2
    fill(cx - r, y0, cz - r, cx + r, y1, cz + r, bl)
    fill(cx - r, y0, cz - r, cx - r + ch - 1, y1, cz - r + ch - 1, "air")
    fill(cx + r - ch + 1, y0, cz - r, cx + r, y1, cz - r + ch - 1, "air")
    fill(cx - r, y0, cz + r - ch + 1, cx - r + ch - 1, y1, cz + r, "air")
    fill(cx + r - ch + 1, y0, cz + r - ch + 1, cx + r, y1, cz + r, "air")
def disc(cx, cz, r, y, bl):                        # filled ~circle at one y
    for dx in range(-r, r + 1):
        for dz in range(-r, r + 1):
            if dx * dx + dz * dz <= r * r + r:
                sb(cx + dx, y, cz + dz, bl)
SX, SZ = 350, 165
cmd("forceload add 315 125 396 205")

# ============================ 1. LEVEL + CONCRETE APRON ============================
AX0, AX1, AZ0, AZ1 = 318, 384, 132, 198
for y in range(67, 96):
    fill(AX0, y, AZ0, AX1, y, AZ1, "air")
fill(AX0, 61, AZ0, AX1, 65, AZ1, "stone")
fill(AX0, 66, AZ0, AX1, 66, AZ1, "grass_block")
fill(322, 66, 136, 380, 66, 194, "gray_concrete")             # main apron
fill(326, 66, 140, 376, 66, 190, "light_gray_concrete")       # inner pad
# yellow hazard border + markings
for x in range(326, 377, 3): sb(x, 66, 140, "yellow_concrete"); sb(x, 66, 190, "yellow_concrete")
for z in range(140, 191, 3): sb(326, 66, z, "yellow_concrete"); sb(376, 66, z, "yellow_concrete")
for (mx, mz) in [(332, 146), (334, 146), (332, 145), (332, 147), (332, 148)]:  # painted "39"
    sb(mx, 66, mz, "white_concrete")
fill(335, 66, 145, 335, 66, 148, "white_concrete"); fill(336, 66, 145, 337, 66, 145, "white_concrete")
fill(336, 66, 146, 337, 66, 146, "white_concrete"); fill(336, 66, 148, 337, 66, 148, "white_concrete"); sb(337, 66, 147, "white_concrete")
# crawlerway approach (west)
fill(300, 66, 158, 322, 66, 172, "gravel"); fill(300, 65, 158, 322, 65, 172, "stone")

# ============================ 2. FLAME TRENCH + MOBILE LAUNCHER PLATFORM ============================
fill(326, 60, 160, 357, 65, 170, "air")                       # the trench (opens west)
fill(326, 59, 159, 357, 59, 171, "deepslate_tiles")           # trench floor
fill(326, 60, 159, 357, 65, 159, "deepslate_tiles"); fill(326, 60, 171, 357, 65, 171, "deepslate_tiles")
fill(357, 60, 160, 357, 65, 170, "deepslate_tiles")
for x in range(350, 358):                                     # flame deflector wedge
    fill(x, 60, 162, x, 60 + (x - 350), 168, "iron_block")
# MLP deck on 4 corner pedestals, bridging the trench
for (px, pz) in [(344, 156), (356, 156), (344, 174), (356, 174)]:
    fill(px - 1, 66, pz - 1, px + 1, 73, pz + 1, "gray_concrete")
fill(344, 73, 156, 356, 74, 174, "gray_concrete")             # the deck (2 thick)
fill(345, 74, 157, 355, 74, 173, "light_gray_concrete")       # deck surface
# flame holes through the deck (SSME + 2 SRB) down into the trench
fill(341, 73, 163, 345, 74, 167, "air")                       # main engine hole (extends under orbiter)
fill(347, 73, 157, 351, 74, 159, "air"); fill(347, 73, 171, 351, 74, 173, "air")  # SRB holes
fill(344, 67, 162, 344, 73, 168, "iron_bars")                 # MLP west fascia detail
sb(346, 75, 156, "lantern"); sb(354, 75, 156, "lantern"); sb(346, 75, 174, "lantern"); sb(354, 75, 174, "lantern")

# ============================ 3. EXTERNAL TANK (orange) ============================
ET = "orange_terracotta"
octprism(SX, SZ, 4, 74, 126, ET)                              # main barrel
sb(SX, 74, SZ, "iron_block")                                  # (interior placeholder, hidden)
# intertank band + ogive nose
fill(SX - 4, 98, SZ - 4, SX + 4, 99, SZ + 4, "brown_terracotta")
octprism(SX, SZ, 3, 127, 129, ET); octprism(SX, SZ, 2, 130, 131, ET); sb(SX, 132, SZ, ET); sb(SX, 133, SZ, "white_concrete")
fill(SX - 4, 76, SZ + 4, SX + 1, 90, SZ + 4, "iron_bars")     # LH2 feedline conduit (front face toward orbiter)

# ============================ 4. SOLID ROCKET BOOSTERS (white, x2) ============================
def srb(cz):
    octprism(SX, cz, 2, 72, 116, "white_concrete")            # casing (segment lines below)
    for y in range(80, 116, 9): fill(SX - 2, y, cz - 2, SX + 2, y, cz + 2, "light_gray_concrete")
    octprism(SX, cz, 2, 117, 119, "white_concrete"); octprism(SX, cz, 1, 120, 122, "white_concrete"); sb(SX, 123, cz, "white_concrete")  # nose cone
    fill(SX - 1, 70, cz - 1, SX + 1, 71, cz + 1, "gray_concrete")    # aft skirt
    disc(SX, cz, 1, 69, "iron_block")                         # nozzle
srb(158); srb(172)

# ============================ 5. ORBITER (white/black, on -x face of ET) ============================
OX = 345                                                      # belly column (against ET)
# fuselage: white top (x339) -> black belly (x345), z161-169, y77-114
fill(339, 77, 161, 345, 114, 169, "white_concrete")
fill(345, 77, 161, 345, 114, 169, "black_concrete")           # black belly (faces ET)
fill(339, 77, 161, 344, 78, 169, "black_concrete")            # black underside (aft/lower)
# rounded nose
fill(340, 110, 162, 344, 113, 168, "white_concrete"); fill(341, 114, 163, 343, 115, 167, "white_concrete"); sb(342, 116, 165, "white_concrete")
fill(345, 108, 163, 345, 113, 167, "black_concrete")          # black nose underside
# cockpit windows near the nose (top, -x side)
fill(339, 108, 164, 339, 110, 166, "black_concrete")
sb(339, 109, 164, "light_blue_stained_glass"); sb(339, 109, 165, "light_blue_stained_glass"); sb(339, 109, 166, "light_blue_stained_glass")
# delta wings (flare out in z at the lower fuselage), black leading edges
for i, y in enumerate(range(80, 92)):
    span = min(9, 1 + i)                                      # widen going down
    fill(340, y, SZ - 4 - span, 344, y, SZ - 4, "white_concrete")
    fill(340, y, SZ + 4, 344, y, SZ + 4 + span, "white_concrete")
    sb(344, y, SZ - 4 - span, "black_concrete"); sb(344, y, SZ + 4 + span, "black_concrete")
fill(344, 80, SZ - 13, 344, 91, SZ + 13, "black_concrete")    # wing leading edge underline
# vertical tail fin (aft = bottom, on -x), and body flap
fill(337, 77, 164, 338, 92, 166, "white_concrete"); fill(336, 78, 165, 336, 88, 165, "white_concrete")
fill(338, 77, 164, 338, 79, 166, "black_concrete")
# OMS pods (aft upper sides)
sb(340, 90, 161, "white_concrete"); sb(340, 91, 161, "gray_concrete"); sb(340, 90, 169, "white_concrete"); sb(340, 91, 169, "gray_concrete")
# 3 SSME nozzles (aft, pointing down into the flame hole)
for (nx, nz) in [(342, 165), (341, 164), (341, 166)]:
    fill(nx, 74, nz, nx, 76, nz, "gray_concrete"); sb(nx, 73, nz, "iron_block")
# payload-bay door seam along the top
fill(339, 92, 165, 339, 108, 165, "light_gray_concrete")

# ============================ 6. FIXED SERVICE STRUCTURE (lattice tower, +x) ============================
TX0, TX1, TZ0, TZ1 = 361, 371, 159, 171
for (cx, cz) in [(TX0, TZ0), (TX1, TZ0), (TX0, TZ1), (TX1, TZ1)]:
    fill(cx, 66, cz, cx, 144, cz, "iron_block")               # corner columns
    fill(cx - 1, 66, cz, cx - 1, 144, cz, "iron_bars") if False else None
for y in range(74, 145, 12):                                  # platform levels + lattice belts
    fill(TX0, y, TZ0, TX1, y, TZ1, "iron_bars")
    fill(TX0 + 1, y, TZ0 + 1, TX1 - 1, y, TZ1 - 1, "iron_block")  # deck
    fill(TX0, y + 1, TZ0, TX1, y + 1, TZ1, "iron_bars")       # railing
for y in range(66, 145, 3):                                   # vertical lattice (bars between columns)
    for (a, b, c, d) in [(TX0, TZ0, TX1, TZ0), (TX0, TZ1, TX1, TZ1), (TX0, TZ0, TX0, TZ1), (TX1, TZ0, TX1, TZ1)]:
        fill(a, y, b, c, y, d, "iron_bars")
fill(TX0, 145, TZ0, TX1, 148, TZ1, "red_concrete")           # painted top section
fill(TX0 + 1, 149, TZ0 + 1, TX1 - 1, 149, TZ1 - 1, "iron_block")
# hammerhead crane (boom reaches -x over the stack)
fill(353, 146, 164, 366, 146, 166, "iron_block"); fill(353, 145, 165, 353, 147, 165, "iron_bars")
sb(353, 144, 165, "iron_bars"); sb(353, 143, 165, "iron_block")    # hook
# orbiter access arm + WHITE ROOM (reaches the stack's near face ~y100; must NOT cut the ET)
fill(355, 100, 164, 361, 100, 166, "iron_block"); fill(355, 101, 164, 360, 101, 166, "iron_bars")
fill(355, 99, 163, 357, 103, 167, "white_concrete"); fill(356, 100, 164, 356, 102, 166, "air")   # white room (hollow)
sb(355, 101, 165, "iron_block")
# GOX vent 'beanie cap' arm (reaches over the ET nose ~y128; start just off the nose)
fill(354, 128, 164, 361, 128, 166, "iron_block")
fill(348, 130, 162, 354, 133, 168, "white_concrete"); fill(349, 130, 163, 353, 132, 167, "air")  # the cap
# tower lightning mast
fill(366, 149, 165, 366, 168, 165, "iron_bars"); sb(366, 169, 165, "lightning_rod")
# floodlights up the tower
for y in (86, 110, 134): sb(TX0, y + 2, TZ0, "lantern"); sb(TX1, y + 2, TZ1, "lantern")

# ============================ 7. LIGHTNING MASTS + GROUND SUPPORT ============================
for (mx, mz) in [(330, 144), (330, 186)]:                     # 2 catenary masts
    fill(mx, 67, mz, mx, 120, mz, "iron_bars"); sb(mx, 121, mz, "lightning_rod")
    fill(mx - 1, 67, mz, mx + 1, 67, mz, "iron_block")
# sound-suppression water tower (tall cylinder)
octprism(372, 184, 4, 67, 96, "white_concrete"); fill(368, 88, 180, 376, 90, 188, "light_blue_concrete")
octprism(372, 184, 4, 97, 98, "white_concrete"); octprism(372, 184, 2, 99, 100, "white_concrete"); sb(372, 101, 184, "light_blue_concrete")
# LOX / LH2 storage spheres (2)
for (tx, tz, band) in [(332, 178, "lime_concrete"), (340, 184, "white_concrete")]:
    octprism(tx, tz, 3, 68, 73, "white_concrete"); octprism(tx, tz, 2, 74, 75, "white_concrete"); sb(tx, 76, tz, "white_concrete")
    fill(tx - 3, 70, tz, tx + 3, 70, tz, band)
    fill(tx, 67, tz - 4, tx, 67, tz - 1, "iron_bars")         # pipe toward pad
# perimeter floodlight poles + fence
for (lx, lz) in [(322, 138), (380, 138), (322, 192), (380, 192)]:
    fill(lx, 67, lz, lx, 73, lz, "iron_block"); fill(lx - 1, 73, lz, lx + 1, 73, lz, "iron_block")
    sb(lx - 1, 73, lz, "redstone_lamp"); sb(lx + 1, 73, lz, "redstone_lamp"); sb(lx, 74, lz, "sea_lantern")
for x in range(320, 383, 2): sb(x, 67, 134, "oak_fence"); sb(x, 67, 196, "oak_fence")
for z in range(134, 197, 2): sb(320, 67, z, "oak_fence"); sb(382, 67, z, "oak_fence")
sb(330, 68, 196, 'oak_wall_sign[facing=south]{front_text:{messages:["\\"\\"","\\"LAUNCH COMPLEX 39\\"","\\"SHUTTLE PAD\\"","\\"\\""]}}')

cmd("forceload remove all")
print("LAUNCH COMPLEX DONE")
print("apron pad (350,66,165) light_gray:", cmd("execute if block 350 66 165 minecraft:light_gray_concrete"))
print("flame trench open (340,62,165):", cmd("execute if block 340 62 165 minecraft:air"))
print("MLP deck (350,74,160):", cmd("execute if block 350 74 160 minecraft:light_gray_concrete"))
print("ET barrel (350,100,168) orange:", cmd("execute if block 350 100 168 minecraft:orange_terracotta"))
print("ET nose tip (350,133,165):", cmd("execute if block 350 133 165 minecraft:white_concrete"))
print("SRB casing (350,100,156) white:", cmd("execute if block 350 100 156 minecraft:white_concrete"))
print("SRB nosecone (350,122,172):", cmd("execute if block 350 122 172 minecraft:white_concrete"))
print("orbiter body (340,100,165) white:", cmd("execute if block 340 100 165 minecraft:white_concrete"))
print("orbiter belly black (345,100,165):", cmd("execute if block 345 100 165 minecraft:black_concrete"))
print("orbiter wing (340,85,155):", cmd("execute unless block 340 85 155 minecraft:air"))
print("orbiter cockpit glass (339,109,165):", cmd("execute if block 339 109 165 minecraft:light_blue_stained_glass"))
print("SSME nozzle (342,73,165):", cmd("execute if block 342 73 165 minecraft:iron_block"))
print("FSS column (361,120,159) iron:", cmd("execute if block 361 120 159 minecraft:iron_block"))
print("FSS crane boom (358,146,165):", cmd("execute if block 358 146 165 minecraft:iron_block"))
print("white room (344,101,166):", cmd("execute if block 344 101 166 minecraft:white_concrete"))
print("lightning mast tip (366,169,165):", cmd("execute if block 366 169 165 minecraft:lightning_rod"))
print("water tower (372,90,184):", cmd("execute unless block 372 90 184 minecraft:air"))
print("complex sign:", cmd("execute if block 330 68 196 minecraft:oak_wall_sign"))
