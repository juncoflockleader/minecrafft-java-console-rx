#!/usr/bin/env python3
"""MARKET FAIR on expanded land south of the castle gate (outside the curtain
wall, z<70). Avoids the rollercoaster (x261-309, z29-61) by staying x<=258.

Main avenue from the gate lined with merchant stalls (profession villagers +
themed goods + striped awnings), a central well, livestock pen, tavern,
fortune-teller tent, performers' stage, welcome arch, lamps + bunting."""
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
def sign(x, y, z, face, txt):
    sb(x, y, z, f"oak_wall_sign[facing={face}]{{front_text:{{messages:['\"{txt}\"','\"\"','\"\"','\"\"']}}}}")
cmd("forceload add 174 36 260 71")

# ============================ 1. EXPAND + LEVEL THE FAIRGROUND ============================
FX0, FX1, FZ0, FZ1 = 176, 258, 38, 69
for y in range(67, 86):
    fill(FX0, y, FZ0, FX1, y, FZ1, "air")
fill(FX0, 61, FZ0, FX1, 65, FZ1, "stone")
fill(FX0, 66, FZ0, FX1, 66, FZ1, "grass_block")

# paths: main avenue (gate -> arch) + plaza, dirt_path & cobble
fill(227, 66, 40, 237, 66, 68, "dirt_path")
fill(226, 66, 43, 226, 66, 67, "cobblestone"); fill(238, 66, 43, 238, 66, 67, "cobblestone")
fill(228, 66, 40, 236, 66, 43, "cobblestone")          # plaza around the well
fill(205, 66, 53, 250, 66, 55, "dirt_path")            # cross lane to tent/pen/tavern/stage

# ============================ 2. MERCHANT STALLS ============================
def stall(x0, z0, facing, color, prof, name, station, goods):
    x1, z1 = x0 + 4, z0 + 4
    for px, pz in [(x0, z0), (x1, z0), (x0, z1), (x1, z1)]:
        fill(px, 67, pz, px, 69, pz, "oak_log")        # corner posts
    for i, x in enumerate(range(x0, x1 + 1)):          # striped awning + overhang
        c = color if i % 2 else "white"
        fill(x, 71, z0, x, 71, z1, f"{c}_wool")
    fxf = x1 if facing == "east" else x0               # front (avenue) x
    bxf = x0 if facing == "east" else x1               # back x
    inn = 1 if facing == "east" else -1                # step from front toward interior
    ox = fxf + (1 if facing == "east" else -1)         # overhang x
    for i, z in enumerate(range(z0, z1 + 1)):
        c = color if i % 2 else "white"
        sb(ox, 71, z, f"{c}_wool")
    fill(bxf, 67, z0, bxf, 69, z1, "spruce_planks")    # back wall
    fill(x0, 67, z0, x1, 68, z0, "spruce_planks"); fill(x0, 67, z1, x1, 68, z1, "spruce_planks")  # side rails
    fill(fxf, 67, z0 + 1, fxf, 67, z1 - 1, "smooth_stone_slab[type=double]")    # counter
    for i, gz in enumerate((z0 + 1, z0 + 2, z0 + 3)):  # goods on the counter
        sb(fxf, 68, gz, goods[i])
    sb(bxf + inn, 67, z0 + 1, station)                 # workstation (themes the merchant)
    sb(bxf + inn, 67, z0 + 3, "barrel")                # crate of stock
    sb(fxf - (1 if facing == "east" else -1) * 0, 70, z0 + 2, "lantern[hanging=true]")  # awning lantern
    sb(bxf + inn, 70, z0 + 2, f"lantern[hanging=true]")
    sign(bxf + inn, 69, z0 + 2, facing, name)          # shop sign on back wall, faces avenue
    mx, mz = bxf + inn, z0 + 2                          # merchant stands at the counter
    cmd(f'summon villager {mx} 67 {z0 + 2} {{NoAI:1b,PersistenceRequired:1b,Silent:1b,'
        f'VillagerData:{{type:"plains",profession:"minecraft:{prof}",level:5}}}}')

STALLS = [
    (221, 43, "east", "yellow", "farmer", "BAKERY", "composter", ["hay_block", "pumpkin", "melon"]),
    (221, 49, "east", "red", "butcher", "BUTCHERY", "smoker", ["hay_block", "barrel", "cauldron"]),
    (221, 55, "east", "light_gray", "weaponsmith", "SMITHY", "anvil", ["iron_block", "grindstone", "lantern"]),
    (221, 61, "east", "purple", "cleric", "APOTHECARY", "brewing_stand", ["cauldron", "decorated_pot", "flower_pot"]),
    (240, 43, "west", "cyan", "fisherman", "FISHMONGER", "barrel", ["dried_kelp_block", "barrel", "prismarine"]),
    (240, 49, "west", "brown", "librarian", "BOOKSELLER", "lectern", ["bookshelf", "bookshelf", "candle"]),
    (240, 55, "west", "magenta", "shepherd", "WEAVERY", "loom", ["white_wool", "lime_wool", "pink_wool"]),
    (240, 61, "west", "orange", "toolsmith", "TOOLERY", "smithing_table", ["iron_block", "barrel", "redstone_block"]),
]
for st in STALLS:
    stall(*st)

# ============================ 3. CENTRAL WELL ============================
def well(cx, cz):
    fill(cx - 1, 66, cz - 1, cx + 1, 66, cz + 1, "cobblestone")
    fill(cx - 1, 67, cz - 1, cx + 1, 68, cz + 1, "cobblestone_wall")
    sb(cx, 66, cz, "water"); sb(cx, 67, cz, "air"); sb(cx, 68, cz, "air")
    for px, pz in [(cx - 1, cz - 1), (cx + 1, cz - 1), (cx - 1, cz + 1), (cx + 1, cz + 1)]:
        fill(px, 69, pz, px, 71, pz, "oak_fence")
    fill(cx - 1, 72, cz - 1, cx + 1, 72, cz + 1, "dark_oak_slab[type=top]")   # roof
    sb(cx, 71, cz, "chain"); sb(cx, 70, cz, "lantern")
well(232, 41)

# ============================ 4. WELCOME ARCH ============================
fill(226, 67, 39, 227, 73, 39, "stripped_oak_log"); fill(237, 67, 39, 238, 73, 39, "stripped_oak_log")
fill(226, 73, 39, 238, 74, 39, "stripped_oak_log")
for i, x in enumerate(range(228, 237)):
    sb(x, 75, 39, f"{['red','yellow','blue','lime','magenta'][i % 5]}_wool")     # bunting toppers
sign(231, 72, 39, "south", "WELCOME"); sign(233, 72, 39, "south", "TO THE FAIR")
sb(227, 72, 39, "red_wall_banner[facing=south]"); sb(237, 72, 39, "blue_wall_banner[facing=south]")

# ============================ 5. LAMPS + BUNTING along the avenue ============================
for z in range(44, 68, 6):
    for x in (225, 239):
        fill(x, 67, z, x, 69, z, "oak_fence"); sb(x, 70, z, "lantern[hanging=true]")

# ============================ 6. LIVESTOCK PEN (west) ============================
fill(182, 67, 44, 204, 67, 66, "oak_fence")             # solid then hollow -> ring
fill(183, 67, 45, 203, 67, 65, "air")
fill(193, 67, 44, 194, 67, 44, "air")                   # pen gate
fill(184, 66, 45, 202, 66, 65, "grass_block")
sb(186, 67, 48, "water"); sb(187, 67, 48, "water"); sb(186, 67, 49, "hay_block"); sb(188, 67, 48, "hay_block")  # trough+feed
sign(193, 68, 44, "south", "LIVESTOCK")
for spec, n, base in [("cow", 3, 0), ("pig", 3, 0), ("chicken", 4, 0)]:
    for k in range(n):
        cmd(f"summon {spec} {188 + k * 3} 67 {52 + (base + k) % 3 * 3}")
for k, col in enumerate([0, 0, 7, 14, 12]):             # sheep (white/white/gray/red/brown-ish)
    cmd(f"summon sheep {186 + k * 3} 67 {60} {{Color:{col}b}}")
cmd('summon villager 199 67 55 {NoAI:1b,PersistenceRequired:1b,Silent:1b,VillagerData:{type:"plains",profession:"minecraft:farmer",level:3}}')

# ============================ 7. TAVERN (east) ============================
def tavern(x0, z0):
    x1, z1 = x0 + 10, z0 + 8
    fill(x0, 66, z0, x1, 66, z1, "spruce_planks")        # floor
    fill(x0, 67, z0, x0, 71, z1, "spruce_planks"); fill(x1, 67, z0, x1, 71, z1, "spruce_planks")
    fill(x0, 67, z1, x1, 71, z1, "spruce_planks")        # back + sides (front open at z0)
    for px in (x0, x1):
        for pz in (z0,):
            fill(px, 67, pz, px, 71, pz, "stripped_spruce_log")
    fill(x0, 72, z0, x1, 72, z1, "dark_oak_planks")      # roof
    fill(x0 - 1, 71, z0 - 1, x1 + 1, 71, z0 - 1, "spruce_stairs[facing=south]")  # front eave
    # bar counter + kegs along the back
    fill(x0 + 1, 67, z1 - 1, x1 - 1, 67, z1 - 1, "spruce_slab[type=double]")
    for bx in range(x0 + 1, x1, 2): sb(bx, 68, z1 - 1, "barrel")
    sb(x0 + 2, 67, z1 - 2, "barrel"); sb(x0 + 2, 68, z1 - 2, "barrel")
    # tables (fence + pressure plate) with stool slabs
    for (tx, tz) in [(x0 + 2, z0 + 2), (x0 + 6, z0 + 2), (x0 + 8, z0 + 4)]:
        sb(tx, 67, tz, "oak_fence"); sb(tx, 68, tz, "oak_pressure_plate")
        sb(tx + 1, 67, tz, "oak_stairs[facing=west]"); sb(tx - 1, 67, tz, "oak_stairs[facing=east]")
    sb(x0 + 4, 67, z1 - 1, "cauldron"); sb(x0 + 5, 71, z0 + 4, "lantern[hanging=true]")
    sb(x0 + 1, 71, z0 + 4, "lantern[hanging=true]"); sb(x1 - 1, 71, z0 + 4, "lantern[hanging=true]")
    sign(x0 + 5, 71, z0 - 1, "south", "THE TAVERN")
    cmd(f'summon villager {x0 + 5} 67 {z1 - 2} {{NoAI:1b,PersistenceRequired:1b,Silent:1b,VillagerData:{{type:"plains",profession:"minecraft:butcher",level:4}}}}')
    cmd(f'summon villager {x0 + 3} 67 {z0 + 3} {{NoAI:1b,PersistenceRequired:1b,Silent:1b,VillagerData:{{type:"plains",profession:"minecraft:nitwit",level:1}}}}')
tavern(246, 44)

# ============================ 8. FORTUNE-TELLER TENT (west of avenue) ============================
def tent(cx, z0):
    fill(cx - 3, 67, z0, cx + 3, 70, z0 + 6, "purple_wool")
    fill(cx - 2, 67, z0 + 1, cx + 2, 69, z0 + 5, "air")           # hollow
    fill(cx - 3, 67, z0, cx + 3, 67, z0, "air"); fill(cx - 2, 67, z0, cx + 2, 68, z0, "air")  # door
    fill(cx - 1, 71, z0 + 1, cx + 1, 71, z0 + 5, "magenta_wool")  # peak
    fill(cx, 72, z0 + 2, cx, 72, z0 + 4, "magenta_wool")
    sb(cx, 73, z0 + 3, "end_rod")
    sb(cx, 67, z0 + 4, "amethyst_block"); sb(cx, 68, z0 + 4, "sea_lantern"); sb(cx, 69, z0 + 4, "purple_stained_glass")  # crystal ball
    sb(cx - 2, 67, z0 + 2, "brewing_stand"); sb(cx + 2, 67, z0 + 4, "candle")
    sign(cx + 3, 68, z0 + 1, "east", "FORTUNES")
    cmd(f'summon villager {cx} 67 {z0 + 3} {{NoAI:1b,PersistenceRequired:1b,Silent:1b,VillagerData:{{type:"swamp",profession:"minecraft:cleric",level:5}}}}')
tent(211, 42)

# ============================ 9. PERFORMERS' STAGE (east-south) ============================
def stage(x0, z0):
    x1, z1 = x0 + 8, z0 + 5
    fill(x0, 66, z0, x1, 67, z1, "spruce_planks")        # raised platform (1 up)
    fill(x0, 68, z0, x1, 68, z1, "spruce_planks")        # top deck
    for px in (x0, x1):
        fill(px, 69, z1, px, 72, z1, "stripped_spruce_log")
    fill(x0, 72, z1, x1, 72, z1, "stripped_spruce_log")  # back banner frame
    for i, x in enumerate(range(x0 + 1, x1)):
        sb(x, 71, z1, f"{['red','yellow','blue','lime','orange','magenta','cyan'][i % 7]}_wool")
    for nx in range(x0 + 1, x1, 2): sb(nx, 69, z1 - 1, "note_block")
    sb(x0 + 1, 69, z0 + 1, "lantern"); sb(x1 - 1, 69, z0 + 1, "lantern")
    sign(x0 + 4, 69, z0, "south", "STAGE")
    cmd(f'summon villager {x0 + 4} 69 {z1 - 2} {{NoAI:1b,PersistenceRequired:1b,Silent:1b,VillagerData:{{type:"plains",profession:"minecraft:nitwit",level:1}}}}')
stage(247, 60)

# ============================ 10. DECOR: barrels, hay, flowers, crowd ============================
for (bx, bz) in [(208, 56), (216, 50), (216, 60), (245, 56), (218, 67), (244, 67)]:
    sb(bx, 67, bz, "hay_block"); sb(bx, 68, bz, "hay_block")
for (fx, fz, fl) in [(228, 44, "potted_poppy"), (236, 44, "potted_dandelion"), (228, 66, "potted_blue_orchid"), (236, 66, "potted_oxeye_daisy")]:
    sb(fx, 67, fz, fl)
for (cx, cz) in [(232, 46), (230, 52), (234, 58), (229, 63), (235, 50), (231, 60)]:   # market crowd
    cmd(f'summon villager {cx} 67 {cz} {{NoAI:1b,PersistenceRequired:1b,Silent:1b,VillagerData:{{type:"plains",profession:"minecraft:none",level:1}}}}')

cmd("forceload remove all")
print("MARKET FAIR DONE")
print("leveled fairground (200,66,50) grass:", cmd("execute if block 200 66 50 minecraft:grass_block"))
print("avenue path (232,66,55) dirt_path:", cmd("execute if block 232 66 55 minecraft:dirt_path"))
print("BAKERY awning (223,71,45) wool-ish:", cmd("execute unless block 223 71 45 minecraft:air"))
print("smithy anvil (222,67,56):", cmd("execute if block 222 67 56 minecraft:anvil"))
print("well water (232,66,41):", cmd("execute if block 232 66 41 minecraft:water"))
print("arch lintel (232,73,39):", cmd("execute if block 232 73 39 minecraft:stripped_oak_log"))
print("tent crystal (211,68,46) sea_lantern:", cmd("execute if block 211 68 46 minecraft:sea_lantern"))
print("tavern barrel back present:", cmd("execute unless block 247 68 51 minecraft:air"))
print("stage note_block (248,69,64):", cmd("execute if block 248 69 64 minecraft:note_block"))
print("merchant villagers (count near stalls):", cmd("execute if entity @e[type=villager,x=205,y=66,z=40,dx=50,dy=8,dz=30]"))
print("pen animals (count):", cmd("execute if entity @e[type=#minecraft:village_raid_extra,x=182,y=66,z=44,dx=22,dy=4,dz=22]") if False else cmd("execute if entity @e[type=cow,x=182,y=66,z=44,dx=22,dy=4,dz=22]"))
