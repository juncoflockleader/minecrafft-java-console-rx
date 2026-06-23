#!/usr/bin/env python3
"""GIANT APARTMENT TOWER on expanded land north of the castle.
One repeated floor blueprint stacked 50x from y66 to y316 (~250 blocks tall,
near the y319 build limit). Each floor: 4 apartments around a cross-corridor,
a 2x2 scaffolding express-elevator core, curtain-wall glass, lights, furniture."""
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
def door(x, y, z, bl, facing):
    sb(x, y, z, f"{bl}[facing={facing},half=lower]"); sb(x, y + 1, z, f"{bl}[facing={facing},half=upper]")
def ring(x0, x1, z0, z1, y, bl):
    fill(x0, y, z0, x0, y, z1, bl); fill(x1, y, z0, x1, y, z1, bl)
    fill(x0, y, z0, x1, y, z0, bl); fill(x0, y, z1, x1, y, z1, bl)

TX0, TX1, TZ0, TZ1 = 216, 248, 199, 231           # tower footprint (33x33)
EX0, EX1, EZ0, EZ1 = 232, 233, 215, 216           # elevator shaft (2x2)
FRAME, GLASS, INNER, SLABM = "light_gray_concrete", "light_blue_stained_glass", "white_concrete", "smooth_stone"
NFLOORS, BASE, FH = 50, 66, 5
cmd("forceload add 196 163 268 255")

# ============================ 1. EXPAND + LEVEL THE DISTRICT ============================
DX0, DX1, DZ0, DZ1 = 198, 266, 165, 253
for y in range(67, 91):
    fill(DX0, y, DZ0, DX1, y, DZ1, "air")
fill(DX0, 61, DZ0, DX1, 65, DZ1, "stone")
fill(DX0, 66, DZ0, DX1, 66, DZ1, "grass_block")
fill(TX0 - 2, 66, TZ0 - 2, TX1 + 2, 66, TZ1 + 2, "stone_bricks")   # tower plinth/plaza

# ============================ 2. THE REPEATED FLOOR BLUEPRINT ============================
QUAD = [(217, 200), (233, 200), (217, 218), (233, 218)]   # apartment inner origins
BEDS = ["red", "blue", "lime", "yellow"]
def floorbp(y, punch):
    fill(TX0, y, TZ0, TX1, y, TZ1, SLABM)                  # floor slab
    if punch:
        fill(EX0, y, EZ0, EX1, y, EZ1, "air")             # elevator shaft hole
    ring(TX0, TX1, TZ0, TZ1, y + 1, FRAME)                # curtain wall: sill / glass / glass / header
    ring(TX0, TX1, TZ0, TZ1, y + 2, GLASS)
    ring(TX0, TX1, TZ0, TZ1, y + 3, GLASS)
    ring(TX0, TX1, TZ0, TZ1, y + 4, FRAME)
    for x in range(TX0, TX1 + 1, 6):                      # vertical mullions
        fill(x, y + 1, TZ0, x, y + 4, TZ0, FRAME); fill(x, y + 1, TZ1, x, y + 4, TZ1, FRAME)
    for z in range(TZ0, TZ1 + 1, 6):
        fill(TX0, y + 1, z, TX0, y + 4, z, FRAME); fill(TX1, y + 1, z, TX1, y + 4, z, FRAME)
    fill(TX0 + 1, y + 1, 213, TX1 - 1, y + 4, 213, INNER) # corridor walls (corridor = z214-216)
    fill(TX0 + 1, y + 1, 217, TX1 - 1, y + 4, 217, INNER)
    fill(232, y + 1, 200, 232, y + 4, 213, INNER)         # apartment dividers (x232)
    fill(232, y + 1, 217, 232, y + 4, 230, INNER)
    for (dx, dz, face) in [(224, 213, "north"), (240, 213, "north"), (224, 217, "south"), (240, 217, "south")]:
        sb(dx, y + 1, dz, "air"); sb(dx, y + 2, dz, "air"); door(dx, y + 1, dz, "oak_door", face)
    for (lx, lz) in [(224, 206), (240, 206), (224, 224), (240, 224), (228, 215), (236, 215)]:
        sb(lx, y + 4, lz, "lantern[hanging=true]")        # ceiling lights (no dark spawns)
    for i, (qx, qz) in enumerate(QUAD):                   # furnish each apartment
        sb(qx + 1, y + 1, qz + 1, f"{BEDS[i]}_bed[facing=east,part=foot]")
        sb(qx + 2, y + 1, qz + 1, f"{BEDS[i]}_bed[facing=east,part=head]")
        fill(qx + 4, y + 1, qz + 2, qx + 8, y + 1, qz + 6, "light_gray_carpet")
        sb(qx + 11, y + 1, qz + 1, "crafting_table"); sb(qx + 12, y + 1, qz + 1, "barrel")
        sb(qx + 13, y + 1, qz + 1, "smoker[facing=west]"); sb(qx + 5, y + 1, qz + 1, "oak_stairs[facing=north]")

for f in range(NFLOORS):
    floorbp(BASE + f * FH, punch=(f > 0))

# ============================ 3. ELEVATOR + ROOF + LOBBY ============================
TOP = BASE + NFLOORS * FH                                  # 316 (roof slab level)
fill(EX0, BASE + 1, EZ0, EX1, TOP, EZ1, "scaffolding")     # ground-to-roof express shaft
# roof deck
fill(TX0, TOP, TZ0, TX1, TOP, TZ1, SLABM)
fill(EX0, TOP, EZ0, EX1, TOP, EZ1, "air")                  # roof elevator exit
ring(TX0, TX1, TZ0, TZ1, TOP + 1, FRAME); ring(TX0, TX1, TZ0, TZ1, TOP + 2, "light_gray_concrete")
for x in range(TX0, TX1 + 1, 2):                           # parapet crenel-ish caps
    sb(x, TOP + 3, TZ0, FRAME); sb(x, TOP + 3, TZ1, FRAME)
for (rx, rz) in [(220, 203), (244, 203), (220, 227), (244, 227)]:
    sb(rx, TOP + 1, rz, "sea_lantern")
fill(230, TOP + 1, 213, 235, TOP + 1, 218, "smooth_stone")  # rooftop pad around elevator exit
fill(EX0, TOP + 1, EZ0, EX1, TOP + 1, EZ1, "air")
for h in range(TOP + 1, 320):                              # antenna mast + beacon-ish light
    sb(219, h, 202, "iron_bars")
sb(219, 319, 202, "sea_lantern")
# ground lobby: entrance doors on the south wall + sign
fill(231, BASE + 1, TZ0, 233, BASE + 3, TZ0, "air")
door(231, BASE + 1, TZ0, "oak_door", "south"); door(233, BASE + 1, TZ0, "oak_door", "south")
sb(232, BASE + 1, TZ0, "air"); sb(232, BASE + 2, TZ0, "air")
sb(230, BASE + 3, TZ0 - 1, f'oak_wall_sign[facing=south]{{front_text:{{messages:[\"\\\"\\\"\",\"\\\"GRAND TOWER\\\"\",\"\\\"50 FLOORS\\\"\",\"\\\"\\\"\"]}}}}')

cmd("forceload remove all")
print("APARTMENT TOWER DONE")
print("plaza (232,66,200) stone_bricks:", cmd("execute if block 232 66 200 minecraft:stone_bricks"))
print("F1 slab (232,66,205) smooth_stone:", cmd("execute if block 232 66 205 minecraft:smooth_stone"))
print("F1 glass (216,68,210):", cmd("execute if block 216 68 210 minecraft:light_blue_stained_glass"))
print("F1 corridor wall (224,68,213) inner/door:", cmd("execute unless block 224 68 213 minecraft:air"))
print("F1 bed (218,67,201) red_bed:", cmd("execute if block 218 67 201 minecraft:red_bed"))
print("mid-floor slab F25 (232,191,205):", cmd("execute if block 232 191 205 minecraft:smooth_stone"))
print("top-floor slab F50 (232,311,205):", cmd("execute if block 232 311 205 minecraft:smooth_stone"))
print("elevator scaffolding low (232,80,215):", cmd("execute if block 232 80 215 minecraft:scaffolding"))
print("elevator scaffolding high (232,300,215):", cmd("execute if block 232 300 215 minecraft:scaffolding"))
print("roof deck (232,316,205):", cmd("execute if block 232 316 205 minecraft:smooth_stone"))
print("antenna tip light (219,319,202):", cmd("execute if block 219 319 202 minecraft:sea_lantern"))
print("lobby door (231,67,199):", cmd("execute if block 231 67 199 minecraft:oak_door"))
