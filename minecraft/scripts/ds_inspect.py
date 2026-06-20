#!/usr/bin/env python3
"""Top-down ASCII inspector for the Death Star interior. Samples blocks over
RCON and prints a map at a given Y. Read-only — never modifies the world.

Usage: ds_inspect.py <y> <x0> <x1> <z0> <z1>
Legend: . air   # solid   H ladder   D iron_door   = pressure_plate
        s stairs (spiral)  ~ water  L light (sea_lantern)  ? other
"""
import socket, struct, sys
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
def isblk(x, y, z, blk): return "passed" in cmd(f"execute if block {x} {y} {z} {blk}")

y = int(sys.argv[1]); x0, x1, z0, z1 = map(int, sys.argv[2:6])
cmd(f"forceload add {x0} {z0} {x1} {z1}")
print(f"  y={y}  x:{x0}..{x1}  z:{z0}..{z1}")
# x header (tens)
hdr = "    " + "".join(str((x // 10) % 10) if x % 10 == 0 else " " for x in range(x0, x1 + 1))
print(hdr)
for z in range(z0, z1 + 1):
    row = []
    for x in range(x0, x1 + 1):
        if isblk(x, y, z, "minecraft:air"): row.append('.')
        elif isblk(x, y, z, "minecraft:ladder"): row.append('H')
        elif isblk(x, y, z, "minecraft:iron_door"): row.append('D')
        elif isblk(x, y, z, "#minecraft:pressure_plates"): row.append('=')
        elif isblk(x, y, z, "#minecraft:stairs"): row.append('s')
        elif isblk(x, y, z, "minecraft:water"): row.append('~')
        elif isblk(x, y, z, "minecraft:sea_lantern"): row.append('L')
        else: row.append('#')
    print(f"z{z:>3} " + "".join(row))
cmd("forceload remove all")
