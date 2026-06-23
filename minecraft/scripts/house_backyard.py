#!/usr/bin/env python3
"""Fenced BACKYARD north of the Family House (back wall z178) + a curbside
MAILBOX by the front gate. Backyard x199-215 / z165-177: back door + patio &
BBQ, fire pit, kids' play corner (sandbox + swing), doghouse + dog, garden
shed, tree, flowers, lamps. North gate opens onto a leveled lawn strip."""
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
cmd("forceload add 194 158 218 213")

BX0, BX1, BZ0, BZ1 = 199, 215, 165, 177
# ---- level the yard + a lawn strip back to the castle wall (keeps it off the z160 wall) ----
for y in range(67, 73):
    fill(197, y, 161, 217, y, 178, "air")
fill(197, 61, 161, 217, 65, 178, "stone")
fill(197, 66, 161, 217, 66, 178, "grass_block")

# ---- back door through the house north wall ----
fill(206, 67, 178, 207, 69, 178, "air"); door(206, 67, 178, "spruce_door", "north"); door(207, 67, 178, "spruce_door", "north")
fill(205, 66, 177, 208, 66, 177, "stone_bricks")          # back step

# ---- perimeter fence (south side is the house) + north gate ----
fill(BX0, 67, BZ0, BX0, 67, BZ1, "spruce_fence")          # west
fill(BX1, 67, BZ0, BX1, 67, BZ1, "spruce_fence")          # east
fill(BX0, 67, BZ0, BX1, 67, BZ0, "spruce_fence")          # north
sb(206, 67, BZ0, "spruce_fence_gate[facing=north]"); sb(207, 67, BZ0, "spruce_fence_gate[facing=north]")

# ---- patio + table + BBQ (by the back door) ----
fill(203, 66, 174, 211, 66, 176, "polished_andesite")
sb(206, 67, 175, "spruce_fence"); sb(206, 68, 175, "oak_pressure_plate")          # table
sb(205, 67, 175, "spruce_stairs[facing=east]"); sb(207, 67, 175, "spruce_stairs[facing=west]")
sb(206, 67, 174, "spruce_stairs[facing=south]"); sb(206, 67, 176, "spruce_stairs[facing=north]")
sb(210, 67, 175, "smoker[facing=west]"); sb(210, 67, 174, "smooth_stone_slab[type=double]"); sb(210, 68, 174, "cauldron")  # BBQ
fill(204, 67, 176, 204, 68, 176, "spruce_fence"); sb(204, 69, 176, "lantern")     # patio lamp post (NB: this server has no 'chain' block)

# ---- fire pit with log-stump seats ----
for (rx, rz) in [(205, 170), (207, 170), (205, 172), (207, 172)]:
    sb(rx, 66, rz, "cobblestone")
sb(206, 67, 171, "campfire")
for (sx, sz) in [(204, 171), (208, 171), (206, 169), (206, 173)]:
    sb(sx, 67, sz, "spruce_log")

# ---- kids' play corner (west): sandbox + swing ----
fill(200, 67, 167, 202, 67, 169, "sand")                  # sandbox
for (cx, cz) in [(199, 166), (203, 166), (199, 170), (203, 170)]:
    sb(cx, 67, cz, "oak_log") if False else None
sb(201, 68, 168, "sandstone"); sb(201, 67, 167, "smooth_sandstone")               # little sand castle
# swing (A-frame + hanging chains + plank seat)
fill(200, 67, 172, 200, 69, 172, "stripped_oak_log"); fill(202, 67, 172, 202, 69, 172, "stripped_oak_log")
fill(200, 69, 172, 202, 69, 172, "stripped_oak_log")
sb(201, 68, 172, "iron_bars"); sb(201, 67, 172, "oak_trapdoor[facing=north,half=bottom,open=false]")   # rope (no 'chain' block on this server)

# ---- doghouse + dog (east) ----
fill(211, 67, 170, 213, 68, 172, "oak_planks"); fill(212, 67, 171, 212, 67, 171, "air")
fill(211, 67, 172, 213, 68, 172, "oak_planks"); sb(212, 67, 172, "air"); sb(212, 68, 172, "air")  # doorway
fill(211, 69, 170, 213, 69, 172, "oak_stairs[facing=north]")
sb(212, 67, 171, "red_carpet")
cmd('summon wolf 212 67 173 {PersistenceRequired:1b,CustomName:\'{"text":"Rex"}\'}')

# ---- garden shed (NE corner) ----
fill(212, 67, 166, 214, 69, 168, "spruce_planks")
fill(213, 67, 166, 213, 68, 166, "air"); door(213, 67, 166, "spruce_door", "north")
fill(212, 70, 166, 214, 70, 168, "spruce_slab[type=bottom]")
sb(212, 67, 168, "chest"); sb(214, 67, 168, "crafting_table"); sb(214, 67, 167, "barrel")

# ---- tree + flowers + lamp posts ----
fill(201, 67, 174, 201, 70, 174, "oak_log"); fill(199, 70, 172, 203, 71, 176, "oak_leaves"); sb(201, 71, 174, "oak_leaves")
for (fx, fz, fl) in [(214, 174, "rose_bush"), (199, 168, "peony"), (208, 167, "lilac"), (214, 172, "allium"), (204, 169, "cornflower")]:
    sb(fx, 67, fz, fl)
for (lx, lz) in [(200, 166), (214, 166), (209, 167)]:
    fill(lx, 67, lz, lx, 69, lz, "spruce_fence"); sb(lx, 70, lz, "lantern")

# ============================ CURBSIDE MAILBOX (front, by the gate at z209) ============================
fill(208, 67, 210, 208, 68, 210, "spruce_fence")
sb(208, 69, 210, "barrel[facing=south]")                  # the mailbox bin
sb(207, 69, 210, "red_wall_banner[facing=west]")          # the little red flag
sb(208, 68, 211, 'oak_wall_sign[facing=south]{front_text:{messages:[\'""\',\'"THE HOME"\',\'""\',\'""\']}}') if False else \
    cmd('setblock 209 68 210 oak_wall_sign[facing=east]{front_text:{messages:["\\"\\"","\\"THE HOME\\"","\\"\\"","\\"\\""]}}')
fill(205, 66, 210, 209, 66, 211, "gravel")                # curb under the mailbox

cmd("forceload remove all")
print("BACKYARD + MAILBOX DONE")
print("back door (206,67,178):", cmd("execute if block 206 67 178 minecraft:spruce_door"))
print("backyard west fence (199,67,170):", cmd("execute if block 199 67 170 minecraft:spruce_fence"))
print("north gate (206,67,165):", cmd("execute if block 206 67 165 minecraft:spruce_fence_gate"))
print("patio (206,66,175) andesite:", cmd("execute if block 206 66 175 minecraft:polished_andesite"))
print("fire pit campfire (206,67,171):", cmd("execute if block 206 67 171 minecraft:campfire"))
print("sandbox sand (201,67,168):", cmd("execute if block 201 67 168 minecraft:sand"))
print("swing chain (201,68,172):", cmd("execute if block 201 68 172 minecraft:chain"))
print("doghouse roof (212,69,171) stairs:", cmd("execute if block 212 69 171 minecraft:oak_stairs"))
print("dog 'Rex':", cmd("execute if entity @e[type=wolf,x=210,y=66,z=169,dx=5,dy=4,dz=6]"))
print("shed chest (212,67,168):", cmd("execute if block 212 67 168 minecraft:chest"))
print("tree leaves (201,71,174):", cmd("execute if block 201 71 174 minecraft:oak_leaves"))
print("MAILBOX barrel (208,69,210):", cmd("execute if block 208 69 210 minecraft:barrel"))
print("mailbox flag (207,69,210):", cmd("execute if block 207 69 210 minecraft:red_wall_banner"))
print("mailbox sign (209,68,210):", cmd("execute if block 209 68 210 minecraft:oak_wall_sign"))
