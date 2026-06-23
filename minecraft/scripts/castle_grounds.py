#!/usr/bin/env python3
"""Castle GROUNDS: expand+level the land, curtain walls (6-thick, 4-wide
walkway + battlements), 4 corner watchtowers (ground + wall-level entrances),
a gatehouse on the castle axis, a courtyard (paved approach, training yard of
dummies, oak trees) and a GIANT marble king statue centerpiece.

Castle footprint x200-264 z100-142, floor y66. Enclosure outer faces:
S z70, N z160, W x170, E x294; wall solid y67-73, walkway y74, battlement y74-75."""
import socket, struct
HOST, PORT, PW = "127.0.0.1", 25575, "GU+bvxeYn7dnS7qY"
s = socket.create_connection((HOST, PORT), timeout=60); _id = 0
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
SB = "stone_bricks"
cmd("forceload add 165 60 299 170")

# ============================ 1. EXPAND + LEVEL LAND ============================
# margins around the castle (never touch castle x200-264 z100-142). Solid ground
# is ~y60; raise to y66 grass and clear the air above so the plot is flat.
MARGINS = [(165, 299, 65, 99), (165, 299, 143, 165), (165, 199, 100, 142), (265, 299, 100, 142)]
for (x0, x1, z0, z1) in MARGINS:
    for y in range(67, 91):
        fill(x0, y, z0, x1, y, z1, "air")
    fill(x0, 61, z0, x1, 65, z1, "stone")
    fill(x0, 66, z0, x1, 66, z1, "grass_block")

# ============================ 2. CURTAIN WALLS ============================
fill(170, 67, 70, 294, 73, 75, SB)        # south band
fill(170, 67, 155, 294, 73, 160, SB)      # north band
fill(170, 67, 70, 175, 73, 160, SB)       # west band
fill(289, 67, 70, 294, 73, 160, SB)       # east band
fill(229, 67, 70, 235, 72, 75, "air")     # gate passage (ceiling y73 stays = bridge)

def battle_x(x0, x1, z_out, z_in):        # wall running E-W: merlons on z_out, parapet on z_in
    for x in range(x0, x1 + 1):
        sb(x, 74, z_out, SB)
        if x % 2 == 0: sb(x, 75, z_out, SB)
        sb(x, 74, z_in, SB)
def battle_z(z0, z1, x_out, x_in):        # wall running N-S
    for z in range(z0, z1 + 1):
        sb(x_out, 74, z, SB)
        if z % 2 == 0: sb(x_out, 75, z, SB)
        sb(x_in, 74, z, SB)
battle_x(179, 223, 70, 75); battle_x(241, 285, 70, 75)   # south (skip gate + tower ends)
battle_x(179, 285, 160, 155)                              # north
battle_z(79, 151, 170, 175)                               # west
battle_z(79, 151, 294, 289)                               # east

# ============================ 3. GATEHOUSE (south, on castle axis) ============================
for (gx0, gx1) in [(224, 228), (236, 240)]:               # two gate piers, taller
    fill(gx0, 67, 70, gx1, 81, 75, SB)
    fill(gx0 + 1, 74, 71, gx1 - 1, 76, 74, "air")         # walk passes through pier
    sb(gx0, 71, 72, "air"); sb(gx1, 78, 72, "air")        # arrow slits
    for x in range(gx0, gx1 + 1, 2):                      # pier battlements
        sb(x, 82, 70, SB); sb(x, 82, 75, SB)
    fill(gx0, 82, 70, gx0, 82, 75, SB); fill(gx1, 82, 70, gx1, 82, 75, SB)
# bridge over the gate: walk on y74 across the passage, with battlements
for x in range(229, 236):
    sb(x, 74, 70, SB);
    if x % 2 == 0: sb(x, 75, 70, SB)
    sb(x, 74, 75, SB)
fill(229, 71, 70, 235, 72, 70, "iron_bars")               # raised portcullis grille (passage clear y67-70)
sb(232, 73, 72, "lantern")                                # gate passage light

# ============================ 4. WATCHTOWERS (4 corners) ============================
# tower 9x9 sits on the inner wall corner and pokes into the courtyard.
def crenel9(x0, z0, y):
    for x in range(x0, x0 + 9):
        sb(x, y, z0, SB); sb(x, y, z0 + 8, SB)
        if x % 2 == 0: sb(x, y + 1, z0, SB); sb(x, y + 1, z0 + 8, SB)
    for z in range(z0, z0 + 9):
        sb(x0, y, z, SB); sb(x0 + 8, y, z, SB)
        if z % 2 == 0: sb(x0, y + 1, z, SB); sb(x0 + 8, y + 1, z, SB)
# (x0,z0, [(wall-opening: 'x'/'z', fixed, lo, hi)...], (ground-door x,z,facing))
TOWERS = [
    (170, 70, [('x', 178, 71, 74), ('z', 78, 171, 174)], (178, 76, "east")),    # SW
    (286, 70, [('x', 286, 71, 74), ('z', 78, 290, 293)], (286, 76, "west")),    # SE
    (170, 152, [('x', 178, 156, 159), ('z', 152, 171, 174)], (178, 154, "east")),  # NW
    (286, 152, [('x', 286, 156, 159), ('z', 152, 290, 293)], (286, 154, "west")),  # NE
]
for (x0, z0, walks, gd) in TOWERS:
    x1, z1 = x0 + 8, z0 + 8
    fill(x0, 67, z0, x1, 83, z1, SB)                      # solid block
    fill(x0 + 1, 67, z0 + 1, x1 - 1, 72, z1 - 1, "air")   # ground room
    fill(x0 + 1, 74, z0 + 1, x1 - 1, 82, z1 - 1, "air")   # upper room (y73 stays = floor)
    fill(x0 + 2, 83, z0 + 2, x1 - 2, 83, z1 - 2, SB)      # roof patch (already solid)
    fill(x0 + 2, 84, z0 + 2, x1 - 2, 85, z1 - 2, "air")
    crenel9(x0, z0, 84)
    fill(x0 + 1, 84, z0 + 1, x1 - 1, 84, z1 - 1, SB)      # roof floor under battlements
    fill(x0 + 1, 85, z0 + 1, x1 - 1, 88, z1 - 1, "air")
    sb(x0 + 1, 73, z0 + 1, "air")                         # ladder hole through mid-floor
    fill(x0 + 1, 67, z0 + 1, x0 + 1, 84, z0 + 1, f"ladder[facing=east]")
    sb(x0 + 1, 84, z0 + 1, "air")                         # exit hole onto roof
    for (ax, fx, lo, hi) in walks:                        # wall-walk entrances (y74-75)
        if ax == 'x':
            fill(fx, 74, lo, fx, 75, hi, "air")
        else:
            fill(lo, 74, fx, hi, 75, fx, "air")
    door(gd[0], 67, gd[1], "spruce_door", gd[2]); sb(gd[0], 69, gd[1], "air")   # ground entrance (3 tall)
    sb(x0 + 4, 70, z0, "air"); sb(x0, 70, z0 + 4, "air"); sb(x1, 70, z0 + 4, "air")  # arrow slits
    sb(x0 + 4, 79, z0 + 4, "lantern")                     # interior light

# ============================ 5. COURTYARD: plaza, paths, training yard, trees ============================
# paved approach framing the statue (statue pedestal x226-238 z80-90)
fill(222, 66, 76, 242, 66, 78, "polished_andesite")      # front connector (gate -> sides)
fill(222, 66, 76, 224, 66, 99, "polished_andesite")      # west path
fill(240, 66, 76, 242, 66, 99, "polished_andesite")      # east path
fill(222, 66, 95, 242, 66, 99, "stone_bricks")           # castle-entrance plaza
fill(229, 66, 76, 235, 66, 79, "polished_andesite")      # short gate->statue spur

def tree(x, z, h=5):
    fill(x, 67, z, x, 66 + h, z, "oak_log")
    fill(x - 2, 67 + h - 2, z - 2, x + 2, 67 + h - 1, z + 2, "oak_leaves")
    fill(x - 1, 67 + h, z - 1, x + 1, 67 + h, z + 1, "oak_leaves")
    sb(x, 67 + h + 1, z, "oak_leaves")
for (tx, tz) in [(183, 84), (193, 88), (183, 122), (193, 150), (255, 150), (272, 122), (283, 88), (281, 150)]:
    tree(tx, tz)

# training yard (east front courtyard), fenced, with dummies + targets
fill(252, 67, 78, 283, 67, 96, "oak_fence"); fill(253, 67, 79, 282, 67, 95, "coarse_dirt")
fill(252, 67, 86, 252, 67, 87, "air")          # yard gate gap (entrance from the plaza)
fill(253, 66, 79, 282, 66, 95, "coarse_dirt")
for (dx, dz) in [(258, 82), (264, 82), (270, 82), (276, 82), (261, 90), (273, 90)]:
    sb(dx, 67, dz, "oak_fence"); sb(dx, 68, dz, "oak_fence")
    cmd(f"summon armor_stand {dx} 69 {dz} {{ShowArms:1b,NoGravity:1b,NoBasePlate:1b,"
        f"ArmorItems:[{{}},{{}},{{id:\"minecraft:iron_chestplate\",count:1}},{{id:\"minecraft:iron_helmet\",count:1}}],"
        f"HandItems:[{{id:\"minecraft:wooden_sword\",count:1}},{{id:\"minecraft:shield\",count:1}}]}}")
for tz in (80, 88):                                      # hay/target backstops
    fill(280, 67, tz, 280, 69, tz, "hay_block"); sb(281, 68, tz, "target")

# ============================ 6. GIANT KING STATUE ============================
Q = "smooth_quartz"; GOLD = "gold_block"
# pedestal (centered x232, front faces -z toward the gate)
fill(226, 67, 80, 238, 69, 90, SB)
fill(226, 70, 80, 238, 70, 90, "polished_andesite")
for x in range(226, 239, 2): sb(x, 70, 80, "chiseled_stone_bricks"); sb(x, 70, 90, "chiseled_stone_bricks")
sb(232, 69, 79, f"oak_wall_sign[facing=north]{{front_text:{{messages:['\"\"','\"THE KING\"','\"\"','\"\"']}}}}")
# robe (tapering)
fill(228, 71, 83, 236, 74, 89, Q)
fill(229, 75, 83, 235, 77, 89, Q)
fill(229, 78, 84, 235, 80, 88, Q)
fill(230, 81, 84, 234, 83, 88, Q)
for x in range(230, 235): sb(x, 81, 83, GOLD)            # belt front
sb(230, 81, 84, GOLD); sb(234, 81, 84, GOLD)
# torso + chest emblem
fill(229, 84, 84, 235, 89, 88, Q)
sb(231, 86, 83, GOLD); sb(233, 86, 83, GOLD); sb(232, 87, 83, GOLD)
# cape (down the back)
fill(229, 75, 89, 235, 89, 89, "red_wool")
fill(228, 88, 89, 236, 90, 90, "red_wool")
# arms + hands
fill(236, 84, 85, 237, 89, 87, Q); fill(237, 81, 84, 237, 83, 85, Q)   # +x arm holding scepter
fill(227, 84, 85, 228, 89, 87, Q); fill(227, 81, 84, 227, 83, 85, Q)   # -x arm holding orb
# shoulders + neck
fill(228, 89, 84, 236, 90, 88, Q); fill(231, 90, 85, 233, 90, 87, Q)
# head
fill(230, 91, 84, 234, 95, 88, Q)
sb(231, 93, 83, "black_concrete"); sb(233, 93, 83, "black_concrete")   # eyes
fill(231, 90, 83, 233, 91, 83, "white_wool")                          # beard
# crown
for x in range(230, 235): sb(x, 96, 84, GOLD); sb(x, 96, 88, GOLD)
for z in range(84, 89): sb(230, 96, z, GOLD); sb(234, 96, z, GOLD)
for x in (230, 232, 234): sb(x, 97, 84, GOLD)
sb(231, 96, 84, "red_stained_glass"); sb(233, 96, 84, "red_stained_glass")
# scepter (+x hand) + orb (-x hand)
fill(238, 82, 85, 238, 97, 85, "end_rod"); sb(238, 98, 85, "sea_lantern")
sb(227, 82, 84, "sea_lantern")

cmd("forceload remove all")
print("CASTLE GROUNDS DONE")
print("leveled far ground (168,66,80) grass:", cmd("execute if block 168 66 80 minecraft:grass_block"))
print("wall solid (200,70,72):", cmd("execute if block 200 70 72 minecraft:stone_bricks"))
print("wall walk open (200,74,72)=air:", cmd("execute if block 200 74 72 minecraft:air"))
print("south merlon (180,75,70):", cmd("execute if block 180 75 70 minecraft:stone_bricks"))
print("gate passage open (232,68,72)=air:", cmd("execute if block 232 68 72 minecraft:air"))
print("gate pier (226,80,72):", cmd("execute if block 226 80 72 minecraft:stone_bricks"))
print("SW tower wall (170,80,74):", cmd("execute if block 170 80 74 minecraft:stone_bricks"))
print("SW tower ground door (178,67,76):", cmd("execute if block 178 67 76 minecraft:spruce_door"))
print("SW tower walk opening (178,74,72)=air:", cmd("execute if block 178 74 72 minecraft:air"))
print("statue head (232,93,86) quartz:", cmd("execute if block 232 93 86 minecraft:smooth_quartz"))
print("statue crown (232,96,86) gold:", cmd("execute if block 232 96 86 minecraft:gold_block"))
print("scepter tip (238,98,85) sea_lantern:", cmd("execute if block 238 98 85 minecraft:sea_lantern"))
print("a dummy near (258,69,82) armor_stand:", cmd("execute if entity @e[type=armor_stand,x=257,y=68,z=81,dx=3,dy=3,dz=3]"))
print("a tree (183,72,84) log:", cmd("execute if block 183 72 84 minecraft:oak_log"))
