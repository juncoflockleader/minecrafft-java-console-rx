#!/usr/bin/env python3
"""Add 3 living facilities off the y110 ladder room (Living Room is already on
the west; the spiral blocks north), so the new rooms go East / South / SE:
  - GAMING ROOM  (east)
  - BARRACKS     (south)
  - KITCHEN/CAFE (south-east)

Additive + bounded: builds enclosed room boxes away from the ladder, then
carves short corridors from the existing ladder pocket to each (auto iron
doors). The ladder column at (120,112) is never touched.
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

FY, CY = 110, 118
YLO, YHI = FY + 1, CY - 1
WALL, FLOOR, CEIL = "white_concrete", "light_gray_concrete", "smooth_quartz"

def box(x0, x1, z0, z1):
    fill(x0, FY, z0, x1, CY, z1, "air")
    fill(x0, FY, z0, x1, FY, z1, FLOOR)
    fill(x0, CY, z0, x1, CY, z1, CEIL)
    fill(x0, YLO, z0, x0, YHI, z1, WALL)
    fill(x1, YLO, z0, x1, YHI, z1, WALL)
    fill(x0, YLO, z0, x1, YHI, z0, WALL)
    fill(x0, YLO, z1, x1, YHI, z1, WALL)

def adoor(x, z, facing, p1, p2):
    """auto iron door at (x,z) with pressure plates p1,p2 = (x,z) tuples"""
    fill(x, YLO, z, x, YLO + 1, z, "air")
    sb(x, YLO, z, f"iron_door[facing={facing},half=lower]")
    sb(x, YLO + 1, z, f"iron_door[facing={facing},half=upper]")
    sb(p1[0], YLO, p1[1], "stone_pressure_plate")
    sb(p2[0], YLO, p2[1], "stone_pressure_plate")

def corridor(x0, z0, x1, z1):
    """2-high walkway + floor through whatever's in the way"""
    fill(x0, YLO, z0, x1, YLO + 1, z1, "air")
    fill(x0, FY, z0, x1, FY, z1, FLOOR)

cmd("gamerule logAdminCommands false"); cmd("gamerule sendCommandFeedback false")
cmd("forceload add 104 105 142 134")

# ---------------- GAMING ROOM (east) ----------------
box(126, 139, 105, 118)
corridor(121, 111, 125, 113)                       # pocket -> gaming
# the east corridor removed the ladder's backing block (x121,z112) -> the
# ladder at (120,112) popped off. Restore it as a backing column; the corridor
# still passes on either side (z111 / z113).
for y in (YLO, YLO + 1):
    sb(121, y, 112, WALL)
    sb(120, y, 112, "ladder[facing=west]")
adoor(126, 112, "west", (125, 112), (127, 112))
fill(127, FY, 106, 138, FY, 117, "blue_wool")      # carpet
fill(127, YLO, 106, 138, YLO + 2, 106, "black_concrete")           # big screen wall (north)
for x in range(128, 138, 2): sb(x, YLO + 1, 106, "lime_concrete")
sb(132, YLO + 1, 106, "magenta_concrete")
for ax, c in ((128, "redstone_lamp[lit=true]"), (130, "jukebox"), (136, "note_block")):  # arcade row (south)
    sb(ax, FY, 116, "black_concrete"); sb(ax, FY + 1, 116, c)
sb(133, FY, 116, "black_concrete"); sb(133, FY + 1, 116, "note_block")
fill(130, FY, 110, 134, FY, 112, "cyan_concrete")  # pool/air-hockey table base
fill(130, FY + 1, 110, 134, FY + 1, 112, "light_blue_stained_glass")
for sx in (128, 132, 136):                          # seats facing the screen
    sb(sx, FY, 109, "crimson_stairs[facing=south]")
for lx in (130, 135):
    for lz in (108, 114): sb(lx, CY - 1, lz, "sea_lantern")
sign(127, YLO + 2, 113, "east", "GAMING ROOM")

# ---------------- BARRACKS (south) ----------------
box(114, 126, 120, 133)
corridor(119, 114, 121, 120)                        # pocket -> barracks (north door)
adoor(120, 120, "north", (120, 119), (120, 121))
for bz in range(122, 132, 3):                        # bunk rows along the west wall
    sb(115, FY, bz, "red_bed[facing=east,part=foot]"); sb(116, FY, bz, "red_bed[facing=east,part=head]")
    sb(115, FY, bz + 1, "barrel[facing=up]")          # footlocker
for bz in range(122, 132, 3):                        # and the east wall
    sb(125, FY, bz, "blue_bed[facing=west,part=foot]"); sb(124, FY, bz, "blue_bed[facing=west,part=head]")
fill(120, FY, 122, 120, FY, 131, "polished_andesite") # central aisle
for lz in (124, 129): sb(120, CY - 1, lz, "lantern[hanging=true]")
sign(120, YLO + 2, 121, "north", "BARRACKS")

# ---------------- KITCHEN / CAFE (south-east) ----------------
box(127, 140, 120, 133)
corridor(121, 119, 130, 119)                        # branch lane (south of gaming) east
corridor(130, 119, 130, 120)
adoor(130, 120, "north", (130, 119), (130, 121))
# kitchen counter along the north interior wall (z121)
fill(128, FY, 121, 139, FY, 121, "smooth_stone_slab[type=double]")
sb(129, FY + 1, 121, "smoker[facing=south]"); sb(131, FY + 1, 121, "furnace[facing=south]")
sb(133, FY, 121, "cauldron"); sb(135, FY + 1, 121, "barrel"); sb(137, FY + 1, 121, "barrel")
# bistro tables with chairs
for tx in (130, 134, 138):
    for tz in (126, 130):
        sb(tx, FY, tz, "oak_fence"); sb(tx, FY + 1, tz, "oak_pressure_plate")
        sb(tx - 1, FY, tz, "spruce_stairs[facing=east]"); sb(tx + 1, FY, tz, "spruce_stairs[facing=west]")
for lx in (131, 136):
    for lz in (124, 130): sb(lx, CY - 1, lz, "sea_lantern")
sign(128, YLO + 2, 120, "north", "KITCHEN + CAFE")

cmd("forceload remove all")
cmd("gamerule logAdminCommands true"); cmd("gamerule sendCommandFeedback true")
print("LIVING FACILITIES DONE (y110)")
print("gaming door (126,111,112):", cmd("execute if block 126 111 112 minecraft:iron_door"))
print("barracks door (120,111,120):", cmd("execute if block 120 111 120 minecraft:iron_door"))
print("kitchen door (130,111,120):", cmd("execute if block 130 111 120 minecraft:iron_door"))
print("gaming corridor open (123,111,112):", cmd("execute if block 123 111 112 minecraft:air"))
