#!/usr/bin/env python3
"""Castle 2nd floor (master bedrooms + hall balcony) + wall-torch lighting
throughout. Run after castle_shell.py + castle_interior.py.
2nd-floor sits on the wing roofs: floor y75, walk y76, walls y76-82, roof y83."""
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
def torch_walls(x0, x1, z0, z1, y, step=5):
    for z in range(z0 + 2, z1 - 1, step):
        sb(x0 + 1, y, z, "wall_torch[facing=east]"); sb(x1 - 1, y, z, "wall_torch[facing=west]")
    for x in range(x0 + 2, x1 - 1, step):
        sb(x, y, z0 + 1, "wall_torch[facing=south]"); sb(x, y, z1 - 1, "wall_torch[facing=north]")
G, G2 = 67, 76
cmd("forceload add 198 98 266 144")

# ===================== SECOND FLOOR STRUCTURE =====================
for (wx0, wx1) in [(200, 224), (240, 264)]:
    fill(wx0, 75, 100, wx1, 75, 142, "stone_bricks")            # floor (solid roof of 1st floor)
    # outer walls y76-82 (perimeter planes only)
    fill(wx0, 76, 100, wx0, 82, 142, "stone_bricks"); fill(wx1, 76, 100, wx1, 82, 142, "stone_bricks")
    fill(wx0, 76, 100, wx1, 82, 100, "stone_bricks"); fill(wx0, 76, 142, wx1, 82, 142, "stone_bricks")
    fill(wx0 + 1, 76, 101, wx1 - 1, 82, 141, "air")            # hollow the room (AFTER walls)
    fill(wx0, 83, 100, wx1, 83, 142, "deepslate_tiles")        # roof
    # crenellated parapet on the new roof edge
    for x in range(wx0, wx1 + 1, 2):
        sb(x, 84, 100, "stone_bricks"); sb(x, 84, 142, "stone_bricks")
    for z in range(100, 143, 2):
        sb(wx0, 84, z, "stone_bricks"); sb(wx1, 84, z, "stone_bricks")
    # windows (glass) in the long outer walls
    for z in range(106, 138, 6):
        fill(wx0, 78, z, wx0, 80, z + 1, "glass_pane")
        fill(wx1, 78, z, wx1, 80, z + 1, "glass_pane")

# ----- hall balconies (over the great hall) + railings -----
for bx, rail in [(225, 227), (238, 237)]:                       # west balcony x225-226, east x238-239
    fill(bx, 75, 101, bx + 1, 75, 141, "stone_bricks")
    fill(rail, 76, 101, rail, 76, 141, "iron_bars")            # railing overlooking the hall
# carve doors from balconies into the bedrooms (through hall walls x224 / x240)
fill(224, G2, 119, 224, G2 + 1, 120, "air"); door(224, G2, 119, "spruce_door", "east")
fill(240, G2, 119, 240, G2 + 1, 120, "air"); door(240, G2, 119, "spruce_door", "west")

# ===================== MASTER BEDROOMS =====================
def master(x0, x1, name, faceq):
    fill(x0, 75, 101, x1, 75, 141, "spruce_planks")             # warm wood floor
    fill(x0, 75, 125, x1, 75, 141, "stone_bricks")             # keep a stone hearth strip at the back
    cx = (x0 + x1) // 2
    # four-poster king bed against the back wall
    sb(cx - 1, G2, 139, "red_bed[facing=south,part=head]"); sb(cx - 1, G2, 138, "red_bed[facing=south,part=foot]")
    sb(cx + 1, G2, 139, "red_bed[facing=south,part=head]"); sb(cx + 1, G2, 138, "red_bed[facing=south,part=foot]")
    for px, pz in [(cx - 2, 137), (cx + 2, 137), (cx - 2, 140), (cx + 2, 140)]:
        fill(px, G2, pz, px, G2 + 2, pz, "dark_oak_fence")
    fill(cx - 2, G2 + 3, 137, cx + 2, G2 + 3, 140, "red_wool")  # canopy
    # fireplace on the far side wall
    fx = x0 + 2 if faceq == "east" else x1 - 2
    fill(fx, G2, 131, fx, G2 + 4, 133, "bricks")
    fill(fx, G2, 132, fx, G2 + 2, 132, "air"); sb(fx, G2, 132, "campfire")
    sb(fx, G2 + 3, 131, "brick_stairs[facing=north]"); sb(fx, G2 + 3, 133, "brick_stairs[facing=south]")
    # wardrobe + desk + seating + rug
    sb(x0 + 2, G2, 103, "barrel"); sb(x0 + 2, G2 + 1, 103, "barrel"); sb(x1 - 2, G2, 103, "bookshelf")
    sb(cx, G2, 108, "crafting_table"); sb(cx - 1, G2, 108, "spruce_stairs[facing=east]")
    fill(cx - 2, 75, 110, cx + 2, 75, 120, "red_carpet")
    sb(cx, G2 + 6, 130, "chain"); sb(cx, G2 + 5, 130, "lantern")  # chandelier
    sign(cx, G2 + 2, 141, "north", name)
    torch_walls(x0, x1, 101, 141, G2 + 2, 6)

master(200, 224, "LORDS CHAMBER", "east")   # no apostrophe: it breaks single-quoted SNBT
master(240, 264, "LADYS CHAMBER", "west")

# ===================== LIGHTING (wall torches) — 1st floor =====================
# main hall (tall — torch low + high)
torch_walls(224, 240, 100, 142, G + 2, 5); torch_walls(224, 240, 100, 142, G + 9, 6)
# west wing rooms
torch_walls(200, 224, 101, 124, G + 2, 5)        # ballroom
torch_walls(200, 212, 124, 142, G + 2, 5)        # barracks
torch_walls(212, 224, 124, 136, G + 2, 4)        # armory
torch_walls(212, 224, 135, 142, G + 2, 4)        # WC
# east wing rooms
torch_walls(240, 264, 101, 124, G + 2, 5)        # dining
torch_walls(240, 252, 124, 142, G + 2, 5)        # kitchen
torch_walls(252, 264, 124, 133, G + 2, 4)        # servants
torch_walls(252, 264, 132, 138, G + 2, 4)        # storage
torch_walls(252, 264, 137, 142, G + 2, 4)        # WC
# corner towers (a few levels)
for (tx, tz) in [(200, 100), (258, 100), (200, 136), (258, 136)]:
    for ty in (69, 78, 86):
        torch_walls(tx, tx + 6, tz, tz + 6, ty, 3)

cmd("forceload remove all")
print("CASTLE 2ND FLOOR + LIGHTING DONE")
print("lord bed (211,76,139) red_bed:", cmd("execute if block 211 76 139 minecraft:red_bed"))
print("rooms hollow (212,79,120)=air:", cmd("execute if block 212 79 120 minecraft:air"))
print("lord sign (212,78,141):", cmd("execute if block 212 78 141 minecraft:oak_wall_sign"))
print("balcony floor (225,75,120):", cmd("execute unless block 225 75 120 minecraft:air"))
print("balcony door (224,76,119):", cmd("execute if block 224 76 119 minecraft:spruce_door"))
print("hall torch (225,69,107):", cmd("execute if block 225 69 107 minecraft:wall_torch"))
print("bedroom torch (201,78,103):", cmd("execute if block 201 78 103 minecraft:wall_torch"))
