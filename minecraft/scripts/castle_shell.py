#!/usr/bin/env python3
"""New huge castle — SHELL (clear + structure). Interiors come next.

Layout (first floor, floor surface y66):
  central MAIN HALL (2 stories) x224..240, z100..142
  WEST WING (1 story) x200..224   |   EAST WING (1 story) x240..264
  4 corner towers; battlemented parapets; grand south entrance into the hall.
"""
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
def walls(x0, x1, z0, z1, y0, y1, bl):
    fill(x0, y0, z0, x0, y1, z1, bl); fill(x1, y0, z0, x1, y1, z1, bl)
    fill(x0, y0, z0, x1, y1, z0, bl); fill(x0, y0, z1, x1, y1, z1, bl)
def crenel(x0, x1, z0, z1, y, bl):
    # battlements: ring of blocks on top with every-other merlon a block higher
    walls(x0, x1, z0, z1, y, y, bl)
    for x in range(x0, x1 + 1, 2):
        sb(x, y + 1, z0, bl); sb(x, y + 1, z1, bl)
    for z in range(z0, z1 + 1, 2):
        sb(x0, y + 1, z, bl); sb(x1, y + 1, z, bl)

WALL = "stone_bricks"; FLOOR = "stone_bricks"; ROOF = "deepslate_tiles"
TRIM = "polished_andesite"; TOWER = "stone_bricks"
FY = 66

cmd("forceload add 193 88 266 146")

# ---- clear + level (drains the moat, erases old castle) ----
# NB: /fill caps at 32768 blocks, so the clear is tiled per Y-layer (~4366 each).
for y in range(67, 111):
    fill(193, y, 88, 266, y, 146, "air")
for y in range(63, 66):
    fill(193, y, 88, 266, y, 146, "stone")       # foundation / fill moat + pits
fill(193, 66, 88, 266, 66, 146, "grass_block")  # natural ground
fill(200, 66, 100, 264, 66, 142, FLOOR)         # castle floor slab

# ---- WEST + EAST wing outer shell (1 story, y67..74; roof y75) ----
for (wx0, wx1) in [(200, 224), (240, 264)]:
    walls(wx0, wx1, 100, 142, 67, 74, WALL)
    fill(wx0, 75, 100, wx1, 75, 142, WALL)       # wing roof / terrace floor
    fill(wx0 + 1, 75, 101, wx1 - 1, 75, 141, WALL)
    crenel(wx0, wx1, 100, 142, 76, WALL)         # parapet battlements

# ---- MAIN HALL shell (2 stories, y67..82; roof y84) ----
walls(224, 240, 100, 142, 67, 82, WALL)
fill(224, 67, 100, 224, 75, 142, WALL)           # shared wall solid below clerestory
fill(240, 67, 100, 240, 75, 142, WALL)
fill(224, 84, 100, 240, 84, 142, ROOF)           # hall roof
crenel(224, 240, 100, 142, 85, WALL)
# trim courses
fill(224, 75, 100, 240, 75, 142, TRIM)
fill(224, 82, 100, 240, 82, 142, TRIM)

# ---- 4 corner towers (7x7, taller) ----
for (tx, tz) in [(200, 100), (258, 100), (200, 136), (258, 136)]:
    fill(tx, 63, tz, tx + 6, 65, tz + 6, "stone")
    fill(tx, 66, tz, tx + 6, 66, tz + 6, FLOOR)
    walls(tx, tx + 6, tz, tz + 6, 67, 88, TOWER)
    fill(tx, 75, tz, tx + 6, 75, tz + 6, TRIM)   # mid-floor band
    fill(tx + 1, 75, tz + 1, tx + 5, 75, tz + 5, FLOOR)
    crenel(tx, tx + 6, tz, tz + 6, 89, TOWER)
    # arrow slits
    for yy in (70, 78):
        sb(tx, yy, tz + 3, "air"); sb(tx + 6, yy, tz + 3, "air")
        sb(tx + 3, yy, tz, "air"); sb(tx + 3, yy, tz + 6, "air")

# ---- grand south entrance into the hall (z100), 4 wide x 6 tall ----
fill(230, 67, 100, 233, 72, 100, "air")
fill(229, 67, 100, 229, 73, 100, TRIM)           # door jambs
fill(234, 67, 100, 234, 73, 100, TRIM)
fill(229, 73, 100, 234, 73, 100, TRIM)           # lintel

cmd("forceload remove all")
print("CASTLE SHELL DONE")
print("hall NE corner wall (240,80,142):", cmd("execute unless block 240 80 142 minecraft:air"))
print("west wing roof (212,75,120):", cmd("execute unless block 212 75 120 minecraft:air"))
print("tower top (203,88,103):", cmd("execute unless block 203 88 103 minecraft:air"))
print("entrance open (231,69,100):", cmd("execute if block 231 69 100 minecraft:air"))
print("floor (232,66,120):", cmd("execute if block 232 66 120 minecraft:stone_bricks"))
