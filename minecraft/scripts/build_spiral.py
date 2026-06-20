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

SX,SZ = 120,100
R = 3
Y0,Y1 = 104,143
FLOORS=[104,110,118,126,134,142]
cmd("gamerule logAdminCommands false"); cmd("gamerule sendCommandFeedback false")
cmd("forceload add 70 62 170 162")

# open a stairwell shaft through each deck floor
for y in FLOORS:
    fill(SX-4,y,SZ-4,SX+4,y,SZ+4,"air")

# central newel column + lights
fill(SX,Y0-1,SZ,SX,Y1+1,SZ,"stone_bricks")
for y in range(Y0+4,Y1,6): sb(SX,y,SZ,"sea_lantern")

# the spiral: 8 steps / revolution, +1 y each
def pos(i):
    a=math.radians(i*45); return SX+round(R*math.cos(a)), SZ+round(R*math.sin(a))
for i in range(Y1-Y0+1):
    y=Y0+i; x,z=pos(i); nx,nz=pos(i+1)
    ddx,ddz=nx-x,nz-z
    if abs(ddx)>=abs(ddz): face="east" if ddx>0 else "west"
    else: face="south" if ddz>0 else "north"
    sb(x,y,z, f"stone_brick_stairs[facing={face}]")
    sb(x,y-1,z, "stone_bricks")                 # solid riser under each tread
    # outer railing post every other step
    if i%2==0:
        ox=SX+round((R+1)*math.cos(math.radians(i*45))); oz=SZ+round((R+1)*math.sin(math.radians(i*45)))
        sb(ox,y,oz,"iron_bars"); sb(ox,y+1,oz,"iron_bars")

cmd("forceload remove all")
cmd("gamerule logAdminCommands true"); cmd("gamerule sendCommandFeedback true")
print("spiral built", SX, SZ, "y", Y0, "-", Y1)
# verify a few treads + well + newel
for i in (0,8,16,24,32,38):
    x,z=pos(i); y=Y0+i
    print(f" step{i} ({x},{y},{z}):", cmd(f"execute if block {x} {y} {z} #minecraft:stairs"))
print(" newel light:", cmd(f"execute if block {SX} 112 {SZ} minecraft:sea_lantern"))
