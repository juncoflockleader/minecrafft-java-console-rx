#!/usr/bin/env python3
"""Fenced front GARDEN south of the Family House (house front wall z194, door
x206-207). Garden x199-215 / z195-209: veggie patch (west) + flower garden with
a cherry tree & pond (east), a path from a south gate to the front door, a
scarecrow, bench, lamp posts and bees."""
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
cmd("forceload add 196 192 218 212")

GX0, GX1, GZ0, GZ1 = 199, 215, 195, 209
# ---- level the yard to clean grass (covers any tower plinth), clear the air above ----
for y in range(67, 73):
    fill(GX0, y, GZ0, GX1, y, GZ1, "air")
fill(GX0, 66, GZ0, GX1, 66, GZ1, "grass_block")

# ---- perimeter fence (north side is the house wall) + gates ----
fill(GX0, 67, GZ0, GX0, 67, GZ1, "spruce_fence")          # west
fill(GX1, 67, GZ0, GX1, 67, GZ1, "spruce_fence")          # east
fill(GX0, 67, GZ1, GX1, 67, GZ1, "spruce_fence")          # south
sb(206, 67, GZ1, "spruce_fence_gate[facing=south]"); sb(207, 67, GZ1, "spruce_fence_gate[facing=south]")  # front gate

# ---- central path: front door -> gate ----
fill(206, 66, 195, 207, 66, 208, "dirt_path")
fill(205, 66, 195, 208, 66, 196, "gravel")                # little forecourt by the door

# ---- WEST: vegetable patch (x200-205, z197-207) ----
fill(200, 66, 197, 205, 66, 207, "farmland[moisture=7]")
sb(202, 66, 200, "water"); sb(203, 66, 205, "water")      # hydration
CROPS = ["wheat[age=7]", "carrots[age=7]", "potatoes[age=7]", "beetroots[age=3]"]
for z in range(197, 208):
    for x in range(200, 206):
        if (x, z) in [(202, 200), (203, 205)]:
            continue
        sb(x, 67, z, CROPS[(z - 197) // 3 % 4])
# scarecrow on a post in the patch
sb(204, 67, 199, "oak_fence")
cmd('summon armor_stand 204 68 199 {ShowArms:1b,NoGravity:1b,NoBasePlate:1b,Invulnerable:1b,'
    'ArmorItems:[{},{},{id:"minecraft:leather_chestplate",count:1},{id:"minecraft:carved_pumpkin",count:1}],'
    'HandItems:[{id:"minecraft:wheat",count:1},{id:"minecraft:stick",count:1}]}')

# ---- EAST: flower garden + cherry tree + pond (x208-214, z196-208) ----
# cherry tree
fill(212, 67, 200, 212, 71, 200, "cherry_log")
fill(210, 71, 198, 214, 72, 202, "cherry_leaves"); fill(211, 73, 199, 213, 73, 201, "cherry_leaves")
sb(212, 74, 200, "cherry_leaves")
sb(213, 70, 200, "bee_nest[honey_level=0,facing=east]")
cmd("summon bee 213 71 201"); cmd("summon bee 211 71 199")
# pond
fill(209, 66, 205, 211, 66, 207, "water")
sb(210, 67, 206, "lily_pad"); sb(209, 67, 205, "lily_pad")
sb(208, 67, 205, "sugar_cane"); sb(208, 67, 206, "sugar_cane")
# flowers scattered on the grass
FLOWERS = ["poppy", "dandelion", "blue_orchid", "allium", "azure_bluet", "red_tulip",
           "orange_tulip", "white_tulip", "pink_tulip", "oxeye_daisy", "cornflower", "lily_of_the_valley"]
spots = [(209, 197), (210, 198), (213, 197), (214, 199), (208, 199), (213, 203),
         (214, 205), (209, 203), (214, 207), (210, 203), (208, 207), (213, 205),
         (200, 196), (205, 196), (214, 196), (209, 208), (213, 208)]
for i, (fx, fz) in enumerate(spots):
    sb(fx, 67, fz, FLOWERS[i % len(FLOWERS)])
# a bench under the tree + berry bushes
sb(209, 67, 200, "spruce_stairs[facing=south]"); sb(210, 67, 200, "spruce_stairs[facing=south]")
sb(208, 67, 201, "sweet_berry_bush[age=3]"); sb(214, 67, 202, "sweet_berry_bush[age=3]")

# ---- lamp posts flanking the gate + corner ----
for (lx, lz) in [(204, 208), (209, 208), (200, 196), (214, 208)]:
    fill(lx, 67, lz, lx, 69, lz, "spruce_fence"); sb(lx, 70, lz, "lantern")
cmd("forceload remove all")
print("HOUSE GARDEN DONE")
print("west fence (199,67,202):", cmd("execute if block 199 67 202 minecraft:spruce_fence"))
print("front gate (206,67,209):", cmd("execute if block 206 67 209 minecraft:spruce_fence_gate"))
print("path (206,66,202) dirt_path:", cmd("execute if block 206 66 202 minecraft:dirt_path"))
print("farmland (201,66,198):", cmd("execute if block 201 66 198 minecraft:farmland"))
print("a wheat crop (200,67,197):", cmd("execute if block 200 67 197 minecraft:wheat"))
print("cherry log (212,69,200):", cmd("execute if block 212 69 200 minecraft:cherry_log"))
print("cherry leaves (212,72,200):", cmd("execute if block 212 72 200 minecraft:cherry_leaves"))
print("pond water (210,66,206):", cmd("execute if block 210 66 206 minecraft:water"))
print("a flower (210,67,198):", cmd("execute unless block 210 67 198 minecraft:air"))
print("lamp lantern (204,70,208):", cmd("execute if block 204 70 208 minecraft:lantern"))
print("bees in garden:", cmd("execute if entity @e[type=bee,x=208,y=66,z=196,dx=7,dy=8,dz=12]"))
print("scarecrow:", cmd("execute if entity @e[type=armor_stand,x=203,y=67,z=198,dx=2,dy=3,dz=2]"))
