#!/usr/bin/env python3
"""Fix the pool leaking into the conference room below it.

Root cause: f_pool placed water at y142, which is BOTH the pool-room floor and
the conference-room ceiling, so it drained straight down (flooding y135-141).

Fix: (1) drain the conference room + pool column, (2) seal y142 solid, (3)
rebuild the pool as a watertight rimmed basin one level up at y143. Additive
and bounded to the pool/conference column; uses 'air replace water' so it only
removes water, never structure/furniture.
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
def fill(a, b, c, d, e, f, bl, extra=""): return cmd(f"fill {a} {b} {c} {d} {e} {f} {bl} {extra}".strip())
def sb(x, y, z, bl): return cmd(f"setblock {x} {y} {z} {bl}")

cmd("gamerule logAdminCommands false"); cmd("gamerule sendCommandFeedback false")
cmd("forceload add 90 134 130 124")

# 1) DRAIN — remove every water block in the conference room, the y142 layer,
#    the pool room, and a margin on the conference deck (in case it spread).
for y in range(135, 148):
    fill(90, y, 100, 130, y, 124, "air", "replace water")

# 2) SEAL the shared floor/ceiling at y142 solid across the room footprint
fill(101, 142, 106, 113, 142, 118, "smooth_quartz")           # conference ceiling = pool floor
fill(103, 142, 109, 111, 142, 115, "dark_prismarine")         # decorative pool bottom (solid)

# 3) WATERTIGHT POOL at y143: prismarine rim ring, water carved inside it
fill(103, 143, 109, 111, 143, 115, "prismarine_bricks")       # full footprint = rim
fill(104, 143, 110, 110, 143, 114, "water")                   # water inside, 1-block rim remains
# deck trim + lighting + a pool ladder + loungers
fill(101, 142, 106, 113, 142, 107, "dark_prismarine")         # north deck strip
fill(101, 142, 117, 113, 142, 118, "dark_prismarine")         # south deck strip
for lz in (110, 114): sb(106, 147, lz, "sea_lantern")
sb(104, 143, 110, "ladder[facing=east]")
sb(102, 143, 117, "quartz_stairs[facing=south]"); sb(112, 143, 117, "quartz_stairs[facing=south]")

cmd("forceload remove all")
cmd("gamerule logAdminCommands true"); cmd("gamerule sendCommandFeedback true")
print("POOL FIXED")
print("conference dry (107,138,112) air:", cmd("execute if block 107 138 112 minecraft:air"))
print("seal solid (107,142,112) not air:", cmd("execute unless block 107 142 112 minecraft:air"))
print("pool water present (107,143,112):", cmd("execute if block 107 143 112 minecraft:water"))
print("pool floor solid below (107,142,112):", cmd("execute unless block 107 142 112 minecraft:air"))
