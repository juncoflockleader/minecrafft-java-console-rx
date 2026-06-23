#!/usr/bin/env python3
"""New castle — FIRST-FLOOR INTERIORS (run after castle_shell.py).
Main hall (iron throne + stained glass + columns + grand stairs) and the two
wings partitioned + furnished. Floor surface y66; furniture at y67."""
import socket, struct
HOST, PORT, PW = "127.0.0.1", 25575, "GU+bvxeYn7dnS7qY"
s = socket.create_connection((HOST, PORT), timeout=40); _id = 0
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
def sign(x, y, z, face, txt):
    sb(x, y, z, f"oak_wall_sign[facing={face}]{{front_text:{{messages:['\"{txt}\"','\"\"','\"\"','\"\"']}}}}")
G = 67   # walking level (floor block is y66)
cmd("forceload add 198 98 266 144")

# ============================ MAIN HALL ============================
# checkered floor + red runner from entrance to throne
for x in range(225, 240):
    for z in range(101, 142):
        sb(x, 66, z, "polished_diorite" if (x + z) % 2 == 0 else "polished_andesite")
fill(231, 66, 101, 233, 66, 137, "red_carpet")            # runner (sits on floor)
# columns down both sides, with lanterns
for z in range(104, 140, 6):
    for cx in (226, 238):
        fill(cx, G, z, cx, G + 14, z, "chiseled_stone_bricks")
        sb(cx, G + 12, z, "stone_brick_wall"); sb(cx, G + 13, z, "lantern")
# clerestory stained glass on the upper E/W walls (above the wing roofs)
colors = ["red", "blue", "purple", "yellow", "lime", "magenta", "cyan"]
for i, z in enumerate(range(104, 140, 4)):
    c = colors[i % len(colors)]
    fill(224, 77, z, 224, 80, z, f"{c}_stained_glass")
    fill(240, 77, z, 240, 80, z, f"{c}_stained_glass")
# THRONE: raised dais + jagged iron throne under a big stained-glass window
fill(227, 67, 138, 237, 68, 141, "polished_blackstone")   # dais (2 high)
for x in range(227, 238):                                  # front steps
    sb(x, 67, 137, "polished_blackstone_stairs[facing=south]")
fill(230, 69, 140, 234, 69, 141, "iron_block")            # seat base
fill(230, 70, 141, 234, 75, 141, "iron_block")            # tall back
fill(229, 70, 141, 229, 73, 141, "iron_block"); fill(235, 70, 141, 235, 73, 141, "iron_block")  # arms
sb(231, 70, 140, "iron_block"); sb(233, 70, 140, "iron_block")  # armrests
for x in (229, 231, 232, 233, 235):                        # sword-spike crown
    sb(x, 76, 141, "lightning_rod")
for x in (230, 234):
    sb(x, 74, 141, "iron_bars"); sb(x, 75, 141, "iron_bars")
# big stained-glass window behind the throne (north wall z142)
for x in range(228, 237):
    for y in range(72, 81):
        c = colors[(x + y) % len(colors)]
        sb(x, y, 142, f"{c}_stained_glass")
# entrance doors (south z100)
door(231, G, 100, "dark_oak_door", "south"); door(232, G, 100, "dark_oak_door", "south")
# grand staircases (both sides near entrance) up to the 2nd-floor level (y75)
for i in range(8):
    for sx in (226, 238):
        sb(sx, G + i, 102 + i, "polished_blackstone_stairs[facing=south]")
        fill(sx, 66, 102 + i, sx, G + i - 1, 102 + i, "stone_bricks")
# chandeliers (hung sea lanterns)
for cz in (110, 124, 138):
    sb(232, 82, cz, "chain"); sb(232, 81, cz, "sea_lantern")
sign(231, G + 3, 100, "south", "GREAT HALL")

# door from hall into each wing
fill(224, G, 118, 224, G + 1, 119, "air"); door(224, G, 118, "dark_oak_door", "east")  # -> west wing
fill(240, G, 118, 240, G + 1, 119, "air"); door(240, G, 118, "dark_oak_door", "west")  # -> east wing

# helper: enclosed room divider walls inside a wing (ceiling already at y75)
def wallz(x0, x1, z, bl="stone_bricks"): fill(x0, G, z, x1, G + 7, z, bl)
def wallx(x, z0, z1, bl="stone_bricks"): fill(x, G, z0, x, G + 7, z1, bl)
def opening(x, y, z, w=1, h=2):  # carve a doorway
    fill(x, y, z, x, y + h - 1, z, "air")

# ============================ WEST WING ============================
# ballroom (front) | back: barracks + armory + restroom
wallz(201, 223, 124)                      # ballroom / back divider
opening(206, G, 124); opening(218, G, 124)
wallx(212, 125, 141)                      # barracks | armory-restroom
opening(212, G, 132)
wallz(213, 223, 136)                      # armory | restroom
opening(218, G, 136)
# Ballroom: polished floor + chandeliers + a small dais stage
fill(202, 66, 101, 222, 66, 123, "smooth_quartz")
for cx in (208, 216):
    for cz in (108, 118):
        sb(cx, 74, cz, "sea_lantern")
fill(203, 67, 121, 207, 67, 123, "polished_blackstone")    # musicians' dais
sign(213, G + 2, 124, "south", "BALLROOM")
# Barracks
for bz in range(126, 140, 3):
    sb(202, G, bz, "red_bed[facing=east,part=foot]"); sb(203, G, bz, "red_bed[facing=east,part=head]")
    sb(202, G, bz + 1, "barrel")
sign(211, G + 2, 132, "west", "BARRACKS")
# Armory
for ax in range(214, 222, 2):
    cmd(f"summon armor_stand {ax} {G} 127 {{ShowArms:1b}}")
    sb(ax, G, 129, "barrel")
sb(215, G, 134, "smithing_table"); sb(217, G, 134, "anvil"); sb(219, G, 134, "grindstone")
sign(218, G + 2, 136, "north", "ARMORY")
# Restroom
sb(214, G, 140, "cauldron"); sb(217, G, 140, "cauldron"); sb(220, G, 140, "cauldron")
sb(214, G, 138, "smooth_quartz_slab[type=top]"); sb(220, G, 138, "glass")
sign(216, G + 2, 137, "south", "WC")

# ============================ EAST WING ============================
# dining hall (front) | back: kitchens + servant qtrs + storage + restroom
wallz(241, 263, 124)
opening(246, G, 124); opening(258, G, 124)
wallx(252, 125, 141)                      # kitchens | servant/storage/wc
opening(252, G, 132)
wallz(253, 263, 132); wallz(253, 263, 137)
opening(258, G, 132); opening(258, G, 137)
# Dining hall: long table + chairs + chandeliers
fill(244, 66, 101, 260, 66, 123, "spruce_planks")
fill(248, 67, 105, 256, 67, 119, "polished_blackstone")            # table top base
fill(248, 68, 105, 256, 68, 119, "dark_oak_pressure_plate")        # table surface
for tz in range(106, 119, 2):
    sb(247, 67, tz, "spruce_stairs[facing=east]"); sb(257, 67, tz, "spruce_stairs[facing=west]")
for cz in (108, 116):
    sb(252, 74, cz, "sea_lantern")
sign(251, G + 2, 124, "south", "DINING HALL")
# Kitchens
for kx in range(242, 251):
    sb(kx, G, 126, "smooth_stone_slab[type=double]")
sb(243, G + 1, 126, "smoker[facing=south]"); sb(245, G + 1, 126, "furnace[facing=south]")
sb(247, G, 126, "cauldron"); sb(249, G + 1, 126, "barrel")
sb(243, G, 139, "crafting_table"); sb(245, G, 139, "barrel"); sb(247, G, 139, "barrel")
sign(251, G + 2, 130, "west", "KITCHEN")
# Servant quarters
for sz in (127, 130):
    sb(254, G, sz, "white_bed[facing=east,part=foot]"); sb(255, G, sz, "white_bed[facing=east,part=head]")
sb(261, G, 128, "barrel")
sign(258, G + 2, 126, "south", "SERVANTS")
# Storage
fill(254, G, 134, 256, G + 2, 136, "barrel")
sb(259, G, 134, "chest"); sb(260, G, 134, "chest")
sign(258, G + 2, 133, "south", "STORAGE")
# Restroom
sb(254, G, 140, "cauldron"); sb(257, G, 140, "cauldron"); sb(260, G, 140, "cauldron")
sign(258, G + 2, 138, "south", "WC")

cmd("forceload remove all")
print("CASTLE INTERIOR DONE")
print("throne back (232,73,141) iron:", cmd("execute if block 232 73 141 minecraft:iron_block"))
print("hall->west door (224,67,118) iron-or-door:", cmd("execute if block 224 67 118 minecraft:dark_oak_door"))
print("ballroom sign:", cmd("execute if block 213 69 124 minecraft:oak_wall_sign"))
print("dining table (252,68,110):", cmd("execute if block 252 68 110 minecraft:dark_oak_pressure_plate"))
print("clerestory glass (224,78,108):", cmd("execute unless block 224 78 108 minecraft:air"))
