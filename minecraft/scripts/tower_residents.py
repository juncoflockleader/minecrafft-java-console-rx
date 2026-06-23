#!/usr/bin/env python3
"""Add-on to the Grand Tower: (1) a glowing FLOOR-number sign by the elevator on
every floor, and (2) randomly populate apartments with residents (villagers of
assorted professions/biome types) + the occasional cat. Residents are NoAI so
they stay in their rooms (and never wander into the open elevator shaft).
Idempotent: clears existing tower villagers/cats first."""
import socket, struct, random
HOST, PORT, PW = "127.0.0.1", 25575, "GU+bvxeYn7dnS7qY"
s = socket.create_connection((HOST, PORT), timeout=120); _id = 0
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

BASE, FH, NFLOORS = 66, 5, 50
QUAD = [(217, 200), (233, 200), (217, 218), (233, 218)]   # apartment interior origins
PROF = ["farmer", "librarian", "cleric", "armorer", "weaponsmith", "toolsmith", "fisherman",
        "fletcher", "shepherd", "butcher", "leatherworker", "cartographer", "mason", "nitwit", "none"]
VTYPE = ["plains", "taiga", "snow", "desert", "jungle", "savanna", "swamp"]
CATV = ["tabby", "black", "red", "siamese", "british_shorthair", "calico", "persian",
        "ragdoll", "white", "jellie", "all_black"]
random.seed(1337)

cmd("forceload add 216 199 248 231")
cmd("kill @e[type=villager,x=216,y=66,z=199,dx=32,dy=255,dz=32]")
cmd("kill @e[type=cat,x=216,y=66,z=199,dx=32,dy=255,dz=32]")

def fsign(x, y, z, face, n):
    cmd('setblock %d %d %d oak_wall_sign[facing=%s]{front_text:{has_glowing_text:1b,color:"yellow",'
        'messages:[\'""\',\'"FLOOR %d"\',\'""\',\'""\']}}' % (x, y, z, face, n))

def villager(x, y, z):
    cmd('summon villager %d %d %d {NoAI:1b,PersistenceRequired:1b,Silent:1b,VillagerData:{type:"%s",'
        'profession:"minecraft:%s",level:%d}}' % (x, y, z, random.choice(VTYPE), random.choice(PROF), random.randint(1, 5)))

def cat(x, y, z):
    cmd('summon cat %d %d %d {NoAI:1b,PersistenceRequired:1b,variant:"minecraft:%s"}' % (x, y, z, random.choice(CATV)))

resi = pets = 0
for f in range(NFLOORS):
    y = BASE + f * FH
    fsign(231, y + 2, 214, "south", f + 1)
    fsign(234, y + 2, 216, "north", f + 1)
    for (qx, qz) in QUAD:
        if random.random() < 0.55:                       # ~55% of apartments are occupied
            villager(qx + random.randint(5, 10), y + 1, qz + random.randint(6, 10)); resi += 1
            if random.random() < 0.40:                   # sometimes a roommate
                villager(qx + random.randint(5, 10), y + 1, qz + random.randint(6, 10)); resi += 1
            if random.random() < 0.30:                   # sometimes a pet cat
                cat(qx + random.randint(6, 9), y + 1, qz + random.randint(6, 9)); pets += 1

cmd("forceload remove all")
print("TOWER RESIDENTS + FLOOR NUMBERS DONE")
print("placed residents:", resi, " cats:", pets)
print("F1 sign placed (231,69,214):", cmd("execute if block 231 69 214 minecraft:oak_wall_sign"))
print("F1 sign text:", cmd("data get block 231 69 214 front_text.messages[1]"))
print("F50 sign placed (234,314,216):", cmd("execute if block 234 314 216 minecraft:oak_wall_sign"))
print("F50 sign text:", cmd("data get block 234 314 216 front_text.messages[1]"))
print("total villagers in tower:", cmd("execute if entity @e[type=villager,x=216,y=66,z=199,dx=32,dy=255,dz=32]"))
print("total cats in tower:", cmd("execute if entity @e[type=cat,x=216,y=66,z=199,dx=32,dy=255,dz=32]"))
print("sample villager profession (low floor):", cmd("execute as @e[type=villager,x=216,y=66,z=199,dx=32,dy=20,dz=32,limit=1] run data get entity @s VillagerData.profession"))
