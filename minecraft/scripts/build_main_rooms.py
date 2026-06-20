import socket, struct, math
HOST, PORT, PW = "127.0.0.1", 25575, "GU+bvxeYn7dnS7qY"
s = socket.create_connection((HOST, PORT), timeout=20); _id=0
def raw(t,b):
    global _id; _id+=1; rid=_id
    d=struct.pack('<ii',rid,t)+b.encode()+b'\x00\x00'; s.sendall(struct.pack('<i',len(d))+d); buf=b''
    while True:
        while len(buf)<4: buf+=s.recv(8192)
        ln=struct.unpack('<i',buf[:4])[0]
        while len(buf)<4+ln: buf+=s.recv(8192)
        pid=struct.unpack('<i',buf[4:8])[0]; body=buf[12:4+ln-2].decode('utf8','replace'); buf=buf[4+ln:]
        if pid==rid: return body
raw(3,PW)
def cmd(c): return raw(2,c)
def fill(a,b,c,d,e,f,bl): return cmd(f"fill {a} {b} {c} {d} {e} {f} {bl}")
def sb(x,y,z,bl): return cmd(f"setblock {x} {y} {z} {bl}")
def sign(x,y,z,face,txt): sb(x,y,z,f"oak_wall_sign[facing={face}]{{front_text:{{messages:['\"{txt}\"','\"\"','\"\"','\"\"']}}}}")

DECKS=[(104,110,"ARMORY"),(110,118,"BARRACKS"),(118,126,"OFFICES"),
       (126,134,"CONTROL"),(134,142,"CONFERENCE"),(142,148,"AMENITIES")]
WALL="light_gray_concrete"
cmd("gamerule logAdminCommands false"); cmd("gamerule sendCommandFeedback false")
cmd("forceload add 70 62 170 162")

def furnish(name, x, y, z):   # x=west interior wall+3-ish, simple props near (x,z)
    if name=="ARMORY":
        sb(x,y,z,"anvil"); sb(x+1,y,z,"smithing_table"); sb(x,y,z+2,"chest"); sb(x+2,y,z+2,"barrel[facing=up]")
        cmd(f"summon armor_stand {x+1} {y} {z+2} {{ShowArms:1b}}")
    elif name=="BARRACKS":
        for bz in (z, z+3):
            sb(x,y,bz,"red_bed[facing=east,part=foot]"); sb(x+1,y,bz,"red_bed[facing=east,part=head]")
    elif name=="OFFICES":
        sb(x,y,z,"barrel[facing=up]"); sb(x,y+1,z,"smooth_quartz_slab[type=bottom]"); sb(x,y,z+1,"spruce_stairs[facing=south]"); sb(x,y+1,z+2,"black_concrete")
    elif name=="CONTROL":
        for cz in range(z,z+5,2): sb(x,y,cz,"redstone_lamp[lit=true]"); sb(x,y,cz,"lever[face=floor]")
        fill(x+3,y+1,z,x+3,y+3,z+4,"black_concrete"); sb(x+3,y+2,z+2,"light_blue_concrete")
    elif name=="CONFERENCE":
        fill(x,y,z,x+4,y,z+1,"polished_blackstone");
        for cx in range(x,x+5,2): sb(cx,y,z-1,"dark_oak_stairs[facing=south]"); sb(cx,y,z+2,"dark_oak_stairs[facing=north]")
        fill(x,y+1,z+3,x+4,y+3,z+3,"black_concrete"); sb(x+2,y+2,z+3,"light_blue_concrete")
    elif name=="AMENITIES":
        fill(x,y-1,z,x+3,y-1,z+3,"water"); fill(x,y,z,x+3,y,z,"prismarine_brick_slab[type=top]")
        sb(x-1,y,z,"smoker")

for fy,cy,name in DECKS:
    ylo,yhi=fy+1,cy-1
    x0,x1,z0,z1=102,114,106,118
    # room interior (clear out the maze here)
    fill(x0+1,ylo,z0+1,x1,yhi,z1-1,"air")
    # clean facility floor + walls
    fill(x0+1,fy,z0+1,x1,fy,z1-1,WALL)
    fill(x0,ylo,z0,x0,yhi,z1,WALL)            # west
    fill(x0,ylo,z0,x1,yhi,z0,WALL)            # north
    fill(x0,ylo,z1,x1,yhi,z1,WALL)            # south
    # ensure foyer west door opens into the room
    fill(114,ylo,111,115,ylo+1,113,"air")
    sb(115,ylo,112,"iron_door[facing=west,half=lower]"); sb(115,ylo+1,112,"iron_door[facing=west,half=upper]")
    sb(116,ylo,112,"stone_pressure_plate"); sb(114,ylo,112,"stone_pressure_plate")
    # room -> maze auto door (west wall) + stub
    fill(x0,ylo,112,x0,ylo+1,112,"air")
    sb(x0,ylo,112,"iron_door[facing=east,half=lower]"); sb(x0,ylo+1,112,"iron_door[facing=east,half=upper]")
    sb(x0+1,ylo,112,"stone_pressure_plate"); sb(x0-1,ylo,112,"stone_pressure_plate")
    fill(x0-4,ylo,111,x0-1,yhi,112,"air")     # stub into maze
    # signage + light
    sign(113,ylo+2,112,"east",name)
    for lx in (105,110):
        for lz in (109,115): sb(lx,cy,lz,"sea_lantern")
    furnish(name,105,ylo,109)
    print(f"{name} y{fy}: main room off the foyer built")

cmd("forceload remove all")
cmd("gamerule logAdminCommands true"); cmd("gamerule sendCommandFeedback true")
print("MAIN ROOMS DONE")
print("control foyer door:", cmd("execute if block 115 127 112 minecraft:iron_door"))
print("control room interior air:", cmd("execute if block 108 128 112 minecraft:air"))
print("control room sign:", cmd("execute if block 113 129 112 minecraft:oak_wall_sign"))
