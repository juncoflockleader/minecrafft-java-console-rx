#!/usr/bin/env python3
"""A 3-story family house (+ attic + big basement) at the player's location
(~202,66,191). 17x17 footprint, Tudor style (white walls + dark timber).
  Basement (y60): random TREASURES (loot-table chests + gem blocks + wine cellar)
  1F (y66): LIVING ROOM (sofas, fireplace, dining, kitchen nook)
  2F (y72): 4 BEDROOMS — parents / boy / girl / guest
  3F (y78): STUDY (library + desks)
  Attic (y84): random junk under a gabled roof
A 2-wide spruce staircase links every level (down to basement, up to attic)."""
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
def sign(x, y, z, face, txt):
    sb(x, y, z, f"oak_wall_sign[facing={face}]{{front_text:{{messages:['\"{txt}\"','\"\"','\"\"','\"\"']}}}}")
def ringy(x0, x1, z0, z1, y0, y1, bl):
    fill(x0, y0, z0, x0, y1, z1, bl); fill(x1, y0, z0, x1, y1, z1, bl)
    fill(x0, y0, z0, x1, y1, z0, bl); fill(x0, y0, z1, x1, y1, z1, bl)
def chest(x, y, z, face, table):
    sb(x, y, z, f'chest[facing={face}]{{LootTable:"minecraft:chests/{table}"}}')

X0, X1, Z0, Z1 = 199, 215, 178, 194           # outer walls
WALL, FRAME, PLANK, ROOF = "white_terracotta", "spruce_log", "spruce_planks", "dark_oak_stairs"
FOUND, GLASS, BEAM = "cobblestone", "glass_pane", "stripped_spruce_log"
cmd("forceload add 196 175 218 197")

# ====== windows helper: glass band in a wall with timber mullions ======
def winrow(x0, x1, z0, z1, y):                 # 2-tall glass band with timber mullions every 4
    fill(x0, y, z0, x1, y, z1, GLASS); fill(x0, y + 1, z0, x1, y + 1, z1, GLASS)
    if x0 == x1:                               # wall runs along z
        for z in range(z0, z1 + 1, 4):
            fill(x0, y, z, x0, y + 1, z, FRAME)
    else:                                      # wall runs along x
        for x in range(x0, x1 + 1, 4):
            fill(x, y, z0, x, y + 1, z0, FRAME)

# ============================ STAIRS (down to basement, up through attic) ============================
def flight_up(ybot):                           # 2-wide flight x200-201, climbs +z z179..z184
    for i in range(6):
        z, yy = 179 + i, ybot + 1 + i
        sb(200, yy, z, "spruce_stairs[facing=south]"); sb(201, yy, z, "spruce_stairs[facing=south]")
        if i > 0:
            fill(200, ybot + 1, z, 201, yy - 1, z, PLANK)
def flight_down(ytop):                          # x213-214, descends +z from 1F to basement
    for i in range(6):
        z, yy = 179 + i, ytop - 1 - i
        sb(213, yy, z, "spruce_stairs[facing=south]"); sb(214, yy, z, "spruce_stairs[facing=south]")

# ============================ BASEMENT (y60 floor) — random treasures ============================
fill(200, 61, 179, 214, 65, 193, "air")
fill(X0, 60, Z0, X1, 60, Z1, FOUND)            # basement floor
ringy(X0, X1, Z0, Z1, 61, 65, FOUND)
fill(200, 65, 179, 214, 65, 193, PLANK)        # basement ceiling underside = 1F slab support (replaced below)
for (lx, lz) in [(202, 181), (212, 181), (202, 191), (212, 191), (207, 186)]:
    sb(lx, 64, lz, "lantern[hanging=true]")
# loot chests (auto-fill random treasure when opened)
chest(201, 61, 180, "east", "buried_treasure"); chest(201, 61, 181, "east", "simple_dungeon")
chest(202, 61, 180, "east", "end_city_treasure"); chest(213, 61, 180, "west", "woodland_mansion")
chest(213, 61, 192, "west", "stronghold_corridor"); chest(201, 61, 192, "east", "simple_dungeon")
# treasure hoard + vault decor
fill(206, 61, 191, 209, 61, 192, "gold_block"); sb(206, 62, 191, "emerald_block"); sb(208, 62, 192, "diamond_block")
sb(207, 62, 191, "gold_block"); sb(209, 61, 190, "amethyst_block")
sb(204, 61, 186, "enchanting_table"); fill(203, 61, 185, 205, 61, 187, "bookshelf"); sb(204, 61, 186, "enchanting_table")
sb(210, 61, 186, "anvil"); sb(211, 61, 186, "brewing_stand"); sb(212, 61, 186, "decorated_pot")
# wine cellar (barrels) + cobwebs for atmosphere
for bz in range(180, 193, 2):
    sb(207, 61, bz, "barrel"); sb(207, 62, bz, "barrel")
for (cx, cy, cz) in [(200, 65, 179), (214, 65, 179), (200, 65, 193), (214, 65, 193), (203, 64, 192)]:
    sb(cx, cy, cz, "cobweb")
sign(207, 63, 179, "south", "TREASURE VAULT")

# ============================ 1F (y66) — living room ============================
fill(X0, 66, Z0, X1, 66, Z1, PLANK)            # 1F floor / basement ceiling
fill(200, 66, 179, 214, 66, 193, PLANK)
fill(213, 66, 179, 214, 66, 180, "air")        # basement stair hole
ringy(X0, X1, Z0, Z1, 67, 71, WALL)
for (cx, cz) in [(X0, Z0), (X1, Z0), (X0, Z1), (X1, Z1)]:
    fill(cx, 67, cz, cx, 71, cz, FRAME)        # corner timbers
fill(X0, 67, Z0, X1, 67, Z1, FRAME) if False else None
winrow(200, 206, Z0, Z0, 68); winrow(208, 214, Z0, Z0, 68)   # front windows (z178) flanking door
winrow(X0, X0, 180, 192, 68); winrow(X1, X1, 180, 192, 68)   # side windows
# front door (south wall z194, center)
fill(206, 67, Z1, 207, 68, Z1, "air"); door(206, 67, Z1, "spruce_door", "north"); door(207, 67, Z1, "spruce_door", "north")
sign(205, 69, Z1, "south", "THE HOME")
fill(204, 67, Z1, 209, 67, Z1, "air") if False else None
fill(205, 66, 195, 208, 66, 196, "stone_bricks")            # little stoop
# fireplace on the east wall
fill(213, 67, 184, 213, 70, 186, "bricks"); sb(213, 67, 185, "campfire"); fill(213, 71, 185, 213, 82, 185, "bricks")  # chimney up
sb(212, 67, 185, "air")
# sofas (wool + stairs) facing the fireplace, rug, coffee table
fill(208, 67, 184, 210, 67, 184, "red_wool"); fill(208, 68, 184, 210, 68, 184, "red_wool")
for sx in range(208, 211): sb(sx, 68, 185, "spruce_stairs[facing=east]")
fill(208, 67, 186, 211, 67, 188, "brown_carpet"); sb(209, 67, 187, "spruce_slab[type=top]")
# bookshelves + lamps
fill(200, 67, 180, 200, 70, 180, "bookshelf"); sb(202, 71, 186, "chain"); sb(202, 70, 186, "lantern")
sb(208, 71, 187, "chain"); sb(208, 70, 187, "lantern")
# dining nook (NW) + kitchen counter (SW)
fill(201, 67, 190, 203, 67, 191, "spruce_planks"); fill(201, 68, 190, 203, 68, 191, "dark_oak_pressure_plate")
sb(200, 67, 190, "spruce_stairs[facing=east]"); sb(204, 67, 191, "spruce_stairs[facing=west]")
fill(200, 67, 184, 200, 67, 188, "smooth_stone_slab[type=double]")
sb(200, 68, 184, "furnace[facing=east]"); sb(200, 68, 185, "smoker[facing=east]"); sb(200, 67, 187, "barrel"); sb(200, 68, 188, "cauldron")
flight_up(66); flight_down(66)

# ============================ 2F (y72) — 4 bedrooms ============================
fill(X0, 72, Z0, X1, 72, Z1, PLANK)
fill(200, 72, 179, 202, 72, 186, "air")        # stairwell hole (up from 1F)
ringy(X0, X1, Z0, Z1, 73, 77, WALL)
for (cx, cz) in [(X0, Z0), (X1, Z0), (X0, Z1), (X1, Z1)]:
    fill(cx, 73, cz, cx, 77, cz, FRAME)
winrow(X0, X0, 180, 192, 74); winrow(X1, X1, 180, 192, 74)
winrow(200, 214, Z0, Z0, 74); winrow(200, 214, Z1, Z1, 74)
# central E-W hallway z185-187 ; partitions
fill(203, 73, 184, 214, 77, 184, WALL)         # north rooms' south wall
fill(203, 73, 188, 214, 77, 188, WALL)         # south rooms' north wall
fill(208, 73, 179, 208, 77, 184, WALL)         # N divider (parents|boy)
fill(208, 73, 188, 208, 77, 193, WALL)         # S divider (girl|guest)
fill(202, 73, 185, 202, 77, 187, "air")        # hallway opens to stairwell
for (dx, dz) in [(205, 184), (211, 184), (205, 188), (211, 188)]:
    fill(dx, 73, dz, dx, 74, dz, "air"); door(dx, 73, dz, "spruce_door", "south" if dz == 184 else "north")
def bedroom(x0, x1, z0, z1, color, label, sgx, sgz, sgf):
    sb(x0, 73, z0, f"{color}_bed[facing=east,part=foot]"); sb(x0 + 1, 73, z0, f"{color}_bed[facing=east,part=head]")
    sb(x0, 73, z0 + 1, "barrel"); sb(x0, 74, z0 + 1, "lantern"); sb(x1, 73, z1, "barrel")
    fill(x0 + 2, 73, z0 + 2, x1 - 1, 73, z1 - 1, f"{color}_carpet")
    sb(x1, 73, z0, "bookshelf"); sb((x0 + x1) // 2, 76, (z0 + z1) // 2, "lantern")
    sign(sgx, 75, sgz, sgf, label)
bedroom(203, 207, 179, 183, "blue", "PARENTS", 205, 184, "north")
bedroom(209, 213, 179, 183, "light_blue", "BOY", 211, 184, "north")
bedroom(203, 207, 189, 193, "pink", "GIRL", 205, 188, "south")
bedroom(209, 213, 189, 193, "white", "GUEST", 211, 188, "south")
flight_up(72)

# ============================ 3F (y78) — study ============================
fill(X0, 78, Z0, X1, 78, Z1, PLANK)
fill(200, 78, 179, 202, 78, 186, "air")        # stairwell hole
ringy(X0, X1, Z0, Z1, 79, 83, WALL)
for (cx, cz) in [(X0, Z0), (X1, Z0), (X0, Z1), (X1, Z1)]:
    fill(cx, 79, cz, cx, 83, cz, FRAME)
winrow(X0, X0, 180, 192, 80); winrow(X1, X1, 180, 192, 80)
winrow(200, 214, Z0, Z0, 80); winrow(200, 214, Z1, Z1, 80)
# library walls of bookshelves + desks + reading area
fill(203, 79, 193, 213, 81, 193, "bookshelf"); fill(214, 79, 180, 214, 81, 192, "bookshelf")
fill(204, 79, 180, 212, 79, 181, "spruce_planks"); fill(204, 80, 180, 212, 80, 181, "dark_oak_slab[type=top]")  # long desk
for lx in (205, 208, 211): sb(lx, 80, 181, "lectern")
for cx in (205, 208, 211): sb(cx, 79, 182, "spruce_stairs[facing=north]")          # chairs
fill(203, 79, 185, 206, 79, 188, "red_carpet"); sb(204, 79, 186, "spruce_stairs[facing=east]"); sb(204, 79, 187, "spruce_stairs[facing=east]")
sb(210, 79, 187, "globe_banner" if False else "decorated_pot"); sb(207, 82, 186, "chain"); sb(207, 81, 186, "lantern")
fill(208, 79, 191, 211, 80, 191, "cartography_table"); sb(212, 79, 185, "fletching_table")
sign(205, 81, 179, "south", "STUDY")
flight_up(78)

# ============================ ATTIC (y84) + gabled roof — random junk ============================
fill(X0, 84, Z0, X1, 84, Z1, PLANK)
fill(200, 84, 179, 202, 84, 186, "air")        # stairwell hole to attic
# gabled roof: ridge N-S at x207, slopes east/west, eaves a touch past the walls
for dx in range(0, 9):
    yr = 84 + (8 - dx)
    fill(207 - dx, yr, 177, 207 - dx, yr, 195, ROOF + "[facing=east]")
    fill(207 + dx, yr, 177, 207 + dx, yr, 195, ROOF + "[facing=west]")
fill(207, 92, 177, 207, 92, 195, "dark_oak_slab[type=bottom]")     # ridge cap
# gable end walls (triangles) at z178 and z194
for dx in range(0, 9):
    top = 84 + (8 - dx)
    for x in (207 - dx, 207 + dx):
        fill(x, 84, Z0, x, top - 1, Z0, WALL); fill(x, 84, Z1, x, top - 1, Z1, WALL)
sb(207, 88, Z0, GLASS); sb(207, 89, Z0, GLASS); sb(207, 88, Z1, GLASS); sb(207, 89, Z1, GLASS)  # gable windows
fill(213, 84, 184, 213, 91, 184, "bricks")     # chimney exits the roof
# random attic junk
chest(202, 85, 190, "east", "abandoned_mineshaft"); chest(211, 85, 181, "west", "abandoned_mineshaft")
for (bx, bz) in [(204, 181), (210, 191), (205, 190), (211, 189)]: sb(bx, 85, bz, "barrel")
sb(203, 85, 182, "white_bed[facing=south,part=foot]"); sb(203, 86, 182, "white_bed[facing=south,part=head]") if False else None
for (hx, hz) in [(206, 182), (209, 190)]: sb(hx, 85, hz, "hay_block"); sb(hx, 86, hz, "hay_block")
for (cx, cz) in [(200, 179), (214, 179), (200, 193), (214, 193), (205, 184), (209, 188)]: sb(cx, 86, cz, "cobweb")
for (px, pz, fl) in [(208, 181, "potted_dead_bush"), (204, 191, "potted_fern")]: sb(px, 85, pz, fl)
sb(207, 85, 186, "lantern[hanging=true]"); sb(204, 85, 188, "flower_pot"); sb(210, 85, 183, "cobweb")
sign(206, 86, Z0 + 1, "south", "ATTIC") if False else None

cmd("forceload remove all")
print("FAMILY HOUSE DONE")
print("basement floor (207,60,186) cobble:", cmd("execute if block 207 60 186 minecraft:cobblestone"))
print("treasure chest (201,61,180):", cmd("execute if block 201 61 180 minecraft:chest"))
print("gold hoard (207,61,191):", cmd("execute if block 207 61 191 minecraft:gold_block"))
print("1F floor (207,66,186) planks:", cmd("execute if block 207 66 186 minecraft:spruce_planks"))
print("1F wall (199,69,186) terracotta:", cmd("execute if block 199 69 186 minecraft:white_terracotta"))
print("front door (206,67,194):", cmd("execute if block 206 67 194 minecraft:spruce_door"))
print("fireplace campfire (213,67,185):", cmd("execute if block 213 67 185 minecraft:campfire"))
print("2F floor (207,72,186):", cmd("execute if block 207 72 186 minecraft:spruce_planks"))
print("parents bed (203,73,179):", cmd("execute if block 203 73 179 minecraft:blue_bed"))
print("girl bed (203,73,189) pink:", cmd("execute if block 203 73 189 minecraft:pink_bed"))
print("3F study bookshelf (214,80,186):", cmd("execute if block 214 80 186 minecraft:bookshelf"))
print("3F lectern (205,80,181):", cmd("execute if block 205 80 181 minecraft:lectern"))
print("attic floor (207,84,186):", cmd("execute if block 207 84 186 minecraft:spruce_planks"))
print("roof ridge (207,92,186) slab:", cmd("execute if block 207 92 186 minecraft:dark_oak_slab"))
print("roof slope (203,88,186) stairs:", cmd("execute if block 203 88 186 minecraft:dark_oak_stairs"))
print("attic junk chest (202,85,190):", cmd("execute if block 202 85 190 minecraft:chest"))
print("stair up step (200,67,179):", cmd("execute if block 200 67 179 minecraft:spruce_stairs"))
print("stair down step (213,65,179):", cmd("execute if block 213 65 179 minecraft:spruce_stairs"))
