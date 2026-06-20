#!/usr/bin/env python3
"""Build the 6 named facility rooms off the elevator/ladder foyer on each deck.

Topology per deck (exactly what the user asked for):
    ladder room --DoorA--> facility room --DoorB--> maze
DoorA is on the east wall (toward the ladder at x120); DoorB is on the west
wall (away from the ladder, breaking into the maze). Each room is a fully
enclosed box, so it is cleanly separated from the surrounding maze.

ADDITIVE & BOUNDED: only touches the room box (x100..114, z105..119), the
short foyer strip to the ladder (x115..119), and a short west stub into the
maze. Never runs the maze generator. The ladder (x120) and spiral (z100) are
left untouched.
"""
import socket, struct
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
def sign(x, y, z, face, txt):
    sb(x, y, z, f"oak_wall_sign[facing={face}]{{front_text:{{messages:['\"{txt}\"','\"\"','\"\"','\"\"']}}}}")

# --- room box (walls inclusive); interior is x101..113, z106..118 ---
X0, X1 = 100, 114      # west wall, east wall
Z0, Z1 = 105, 119      # north wall, south wall
WALL = "white_concrete"
CEIL = "smooth_quartz"

# ---------------- per-room furnishing ----------------
def f_command(fy, cy):  # COMMAND CENTER
    g = fy + 1                                               # ground (on top of the floor)
    fill(101, fy, 106, 113, fy, 118, "polished_andesite")
    # big screen wall on the north interior wall
    fill(101, g, 106, 113, g + 2, 106, "black_concrete")
    for x in range(102, 113, 2): sb(x, g + 1, 106, "light_blue_concrete")
    sb(107, g + 1, 106, "cyan_concrete")
    # console banks facing the screen
    for cz in (109, 111):
        for cx in range(103, 112, 2):
            sb(cx, g, cz, "redstone_lamp[lit=true]"); sb(cx, g + 1, cz, "lever[face=floor]")
    # command chairs at the back
    for cx in (105, 109): sb(cx, g, 115, "polished_blackstone_stairs[facing=north]")

def f_living(fy, cy):  # LIVING ROOM
    g = fy + 1
    fill(101, fy, 106, 113, fy, 118, "brown_wool")           # carpet (the floor)
    # couch (L-shape) of stairs + wool backs
    for x in range(103, 110): sb(x, g, 116, "red_wool")
    for x in range(103, 110): sb(x, g, 115, "oak_stairs[facing=north]")
    for z in range(112, 116): sb(103, g, z, "oak_stairs[facing=west]")
    # coffee table
    sb(106, g, 113, "spruce_fence"); sb(106, g + 1, 113, "spruce_slab[type=bottom]")
    # bookshelves + a "TV" on the wall + plants
    fill(110, g, 107, 112, g + 2, 107, "bookshelf")
    fill(104, g + 1, 106, 108, g + 2, 106, "black_concrete")  # tv
    sb(106, g + 1, 106, "blue_concrete")
    sb(102, g, 117, "flower_pot"); sb(112, g, 117, "flower_pot")
    for lz in (110, 116): sb(106, cy - 1, lz, "lantern[hanging=true]")

def f_cafe(fy, cy):  # CAFE + kitchen
    g = fy + 1
    fill(101, fy, 106, 113, fy, 118, "smooth_stone")
    # kitchen counter along the north wall (waist-high) with appliances on top
    for x in range(102, 113):
        sb(x, g, 107, "smooth_stone_slab[type=double]")
    sb(103, g + 1, 107, "smoker[facing=south]"); sb(105, g + 1, 107, "furnace[facing=south]")
    sb(107, g, 107, "cauldron"); sb(109, g + 1, 107, "barrel"); sb(111, g + 1, 107, "barrel")
    # bistro tables (fence + carpet top) with chairs
    for tx in (104, 108, 112):
        for tz in (112, 116):
            sb(tx, g, tz, "oak_fence"); sb(tx, g + 1, tz, "white_carpet")
            sb(tx - 1, g, tz, "spruce_stairs[facing=east]"); sb(tx + 1, g, tz, "spruce_stairs[facing=west]")

def f_restroom(fy, cy):  # RESTROOMS
    g = fy + 1
    fill(101, fy, 106, 113, fy, 118, "white_glazed_terracotta")
    fill(101, g, 106, 113, cy - 1, 118, "air")
    # stalls along the south wall: partitions + doors
    for sx in (103, 106, 109, 112):
        fill(sx, g, 115, sx, g + 2, 118, "quartz_block")
        sb(sx, g, 117, "cauldron")  # toilet
    sb(105, g, 117, "spruce_door[facing=north,half=lower]"); sb(105, g + 1, 117, "spruce_door[facing=north,half=upper]")
    sb(108, g, 117, "spruce_door[facing=north,half=lower]"); sb(108, g + 1, 117, "spruce_door[facing=north,half=upper]")
    # sink counter + mirrors on the north wall
    for x in range(102, 113, 2):
        sb(x, g, 106, "cauldron[level=1]"); sb(x, g + 1, 106, "glass")

def f_conf(fy, cy):  # CONFERENCE ROOM
    g = fy + 1
    fill(101, fy, 106, 113, fy, 118, "polished_andesite")
    # long boardroom table down the middle (waist-high)
    fill(104, g, 110, 110, g, 114, "polished_blackstone")
    fill(104, g + 1, 110, 110, g + 1, 114, "polished_blackstone_slab[type=bottom]")
    # chairs both sides + head chair
    for tx in range(104, 111, 2):
        sb(tx, g, 109, "dark_oak_stairs[facing=south]")
        sb(tx, g, 115, "dark_oak_stairs[facing=north]")
    sb(107, g, 117, "dark_oak_stairs[facing=north]")  # head of table (Vader chair)
    # holo screen wall (north)
    fill(101, g, 106, 113, g + 2, 106, "black_concrete")
    for x in range(102, 113, 2): sb(x, g + 1, 106, "light_blue_concrete")

def f_pool(fy, cy):  # SWIMMING POOL  (basin handled by ds_pool_fix.py; deck trim here)
    g = fy + 1
    # prismarine deck edge + lanterns
    fill(101, fy, 106, 113, fy, 107, "dark_prismarine")
    fill(101, fy, 117, 113, fy, 118, "dark_prismarine")
    for lz in (110, 114): sb(106, cy - 1, lz, "sea_lantern")
    # loungers on the deck
    sb(102, g, 117, "quartz_stairs[facing=south]"); sb(112, g, 117, "quartz_stairs[facing=south]")

DECKS = [
    (104, 110, "COMMAND CENTER", f_command),
    (110, 118, "LIVING ROOM",    f_living),
    (118, 126, "CAFE",           f_cafe),
    (126, 134, "RESTROOMS",      f_restroom),
    (134, 142, "CONFERENCE",     f_conf),
    (142, 148, "SWIMMING POOL",  f_pool),
]

cmd("gamerule logAdminCommands false"); cmd("gamerule sendCommandFeedback false")
cmd("forceload add 92 104 122 120")

for fy, cy, name, furnish in DECKS:
    ylo, yhi = fy + 1, cy - 1
    # 1) clear the box, then build floor / ceiling / 4 walls (encloses the room)
    fill(X0, fy, Z0, X1, cy, Z1, "air")
    fill(X0, fy, Z0, X1, fy, Z1, "light_gray_concrete")          # floor
    fill(X0, cy, Z0, X1, cy, Z1, CEIL)                            # ceiling
    fill(X0, ylo, Z0, X0, yhi, Z1, WALL)                          # west wall
    fill(X1, ylo, Z0, X1, yhi, Z1, WALL)                          # east wall
    fill(X0, ylo, Z0, X1, yhi, Z0, WALL)                          # north wall
    fill(X0, ylo, Z1, X1, yhi, Z1, WALL)                          # south wall
    # 2) DOOR A: east wall -> foyer -> ladder
    fill(X1, ylo, 112, X1, ylo + 1, 112, "air")
    sb(X1, ylo, 112, "iron_door[facing=east,half=lower]"); sb(X1, ylo + 1, 112, "iron_door[facing=east,half=upper]")
    sb(X1 - 1, ylo, 112, "stone_pressure_plate"); sb(X1 + 1, ylo, 112, "stone_pressure_plate")
    fill(115, ylo, 111, 119, yhi, 113, "air")                    # foyer to the ladder
    fill(115, fy, 111, 119, fy, 113, "light_gray_concrete")      # foyer floor
    # 3) DOOR B: west wall -> short stub into the maze
    fill(X0, ylo, 112, X0, ylo + 1, 112, "air")
    sb(X0, ylo, 112, "iron_door[facing=west,half=lower]"); sb(X0, ylo + 1, 112, "iron_door[facing=west,half=upper]")
    sb(X0 + 1, ylo, 112, "stone_pressure_plate"); sb(X0 - 1, ylo, 112, "stone_pressure_plate")
    fill(96, ylo, 111, 99, yhi, 112, "air")                      # stub breaks into the maze
    fill(96, fy, 111, 99, fy, 112, "light_gray_concrete")
    # 4) ceiling lights + signage
    for lx in (104, 110):
        for lz in (109, 115): sb(lx, cy - 1, lz, "sea_lantern")
    sign(115, ylo + 2, 113, "east", name)          # name, read from the foyer
    sign(X0 - 1, ylo + 2, 111, "west", "-> MAZE")  # at the maze stub
    # 5) furnish
    furnish(fy, cy)
    print(f"{name} (y{fy}): room + DoorA(foyer/ladder) + DoorB(maze) built")

cmd("forceload remove all")
cmd("gamerule logAdminCommands true"); cmd("gamerule sendCommandFeedback true")
print("ALL ROOMS DONE")
# spot-checks
print("conf doorA (114,135,112) iron_door:", cmd("execute if block 114 135 112 minecraft:iron_door"))
print("conf doorB (100,135,112) iron_door:", cmd("execute if block 100 135 112 minecraft:iron_door"))
print("pool water (107,143,112):", cmd("execute if block 107 143 112 minecraft:water"))
print("cmd screen (107,106,106):", cmd("execute if block 107 106 106 minecraft:cyan_concrete"))
