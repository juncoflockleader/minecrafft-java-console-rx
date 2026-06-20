#!/usr/bin/env python3
"""Rebuild the hangar: clear the maze that capped the east bay and restore the
tall domed bay, then re-deck and furnish it. NO maze regen.

Bounded clear: x 133..163 (east of the bulkhead at x132, west of the gate at
x165), y 120..188, z within the sphere interior (radius 48 -> leaves the shell).
Leaves intact: y118 floor, y119 (gate trigger plates + FACILITY door sill),
bulkhead x132, blast-door gate at x165 and its hull tunnel beyond.
"""
import socket, struct, math
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

CX, CZ, CY = 120, 112, 140
RC = 48                     # interior clear radius (shell sits at 49-50)
X_LO, X_HI = 133, 163      # east of bulkhead, west of gate

def zr_at(x, y, r=RC):
    t = r * r - (x - CX) ** 2 - (y - CY) ** 2
    return int(math.floor(math.sqrt(t))) if t > 0 else 0

cmd("gamerule logAdminCommands false"); cmd("gamerule sendCommandFeedback false")
cmd("forceload add 130 90 168 134")

# 1) Clear the airspace (open the tall dome over the bay)
for x in range(X_LO, X_HI + 1):
    for y in range(120, 189):
        zr = zr_at(x, y)
        if zr > 0:
            fill(x, y, CZ - zr, x, y, CZ + zr, "air")
print("airspace cleared")

# 2) Clean gray-concrete deck at y118 across the bay footprint
for x in range(X_LO, X_HI + 1):
    zr = zr_at(x, 118)
    if zr > 0:
        fill(x, 118, CZ - zr, x, 118, CZ + zr, "gray_concrete")
print("deck re-laid")

# 3) Flush floor light grid
for x in range(136, X_HI, 5):
    for z in range(CZ - 18, CZ + 19, 5):
        if (x - CX) ** 2 + (z - CZ) ** 2 <= (zr_at(x, 118)) ** 2:
            sb(x, 118, z, "sea_lantern")

# 4) Two landing pads (concentric rings) on the deck
def pad(px, pz):
    for dx in range(-4, 5):
        for dz in range(-4, 5):
            d = math.hypot(dx, dz)
            if d <= 4.3:
                blk = "yellow_concrete" if 3.2 <= d <= 4.3 else ("black_concrete" if d <= 1.4 else "light_gray_concrete")
                sb(px + dx, 118, pz + dz, blk)
    for dx in (-3, 3):  # yellow guide stripes (H pad mark)
        for dz in range(-2, 3): sb(px + dx, 118, pz + dz, "yellow_concrete")
    sb(px, 118, pz, "black_concrete")
pad(148, 100)
pad(148, 124)

# 5) Dome lights — a ring high in the dome + apex
for ang in range(0, 360, 30):
    rx = CX + int(round(20 * math.cos(math.radians(ang))))
    rz = CZ + int(round(20 * math.sin(math.radians(ang))))
    if X_LO <= rx <= X_HI:
        sb(rx, 165, rz, "sea_lantern")
sb(150, 175, CZ, "sea_lantern")

# 6) Control booth at the back-left corner (glass front facing the bay)
fill(134, 119, 104, 139, 122, 110, "light_gray_concrete")     # booth shell
fill(135, 119, 105, 138, 121, 109, "air")                      # hollow
fill(135, 119, 110, 138, 121, 110, "light_blue_stained_glass") # glass front (toward +z bay)
fill(135, 121, 105, 138, 121, 109, "smooth_quartz")            # roof
sb(136, 119, 105, "lectern"); sb(137, 119, 105, "redstone_lamp[lit=true]")
for bx in (135, 137): sb(bx, 119, 106, "lever[face=floor]")
sb(135, 119, 108, "iron_door[facing=south,half=lower]"); sb(135, 120, 108, "iron_door[facing=south,half=upper]")
sb(136, 122, 107, "sea_lantern")

# 7) Park a mech on the deck, facing the gate
cmd("kill @e[type=mech:mech,x=130,y=110,z=95,dx=40,dy=40,dz=35]")
cmd("summon mech:mech 150 119 112 {Rotation:[-90f,0f]}")

cmd("forceload remove all")
cmd("gamerule logAdminCommands true"); cmd("gamerule sendCommandFeedback true")
print("HANGAR REBUILT")
print("dome open (150,170,112) air:", cmd("execute if block 150 170 112 minecraft:air"))
print("deck (150,118,112) gray:", cmd("execute if block 150 118 112 minecraft:gray_concrete"))
print("gate intact (165,130,112):", cmd("execute if block 165 130 112 minecraft:air"))
print("bulkhead intact (132,130,112):", cmd("execute unless block 132 130 112 minecraft:air"))
print("mech parked:", cmd("execute if entity @e[type=mech:mech]"))
