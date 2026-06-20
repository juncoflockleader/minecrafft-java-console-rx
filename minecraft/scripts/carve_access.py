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
def clearstrip(x1,y1,z1,x2,y2,z2):
    cmd(f"fill {x1} {y1} {z1} {x2} {y2} {z2} air replace yellow_terracotta")
    cmd(f"fill {x1} {y1} {z1} {x2} {y2} {z2} air replace white_concrete")
def sb(x,y,z,bl): return cmd(f"setblock {x} {y} {z} {bl}")

CX,CZ,RI=120,112,49
P=3; X0=CX-48; Z0=CZ-48
def intr(y):
    t=RI*RI-(140-y)**2; return math.sqrt(t) if t>0 else 0
def excl(x,z):
    return (114<=x<=126 and 106<=z<=118) or (114<=x<=126 and 94<=z<=106)
def room_of(fy):
    rr=int(intr(fy))-2; cells=[]
    for i in range(32):
        for j in range(32):
            ccx=X0+i*P+1; ccz=Z0+j*P+1; mx,mz=ccx+0.5,ccz+0.5
            if (mx-CX)**2+(mz-CZ)**2 <= (rr-1)**2 and not (excl(ccx,ccz) or excl(ccx+1,ccz+1)):
                cells.append((i,j))
    di,dj=cells[len(cells)//2]
    return X0+di*P-2, Z0+dj*P-2   # rx, rz (door at rx, rz+2, faces east)

DECKS=[(104,110,"ARMORY"),(110,118,"BARRACKS"),(118,126,"OFFICES"),
       (126,134,"CONTROL"),(134,142,"CONFERENCE"),(142,148,"AMENITIES")]
cmd("gamerule logAdminCommands false"); cmd("gamerule sendCommandFeedback false")
cmd("forceload add 70 62 170 162")

for fy,cy,name in DECKS:
    ylo,yhi=fy+1,cy-1
    rx,rz=room_of(fy)
    tx=rx-1                     # corridor target x (west of the door)
    tz=rz+2                     # door z
    # seg 1: x-corridor at z=111..112 from foyer (x114) to tx
    xa,xb=min(114,tx),max(114,tx)
    clearstrip(xa,ylo,111,xb,yhi,112)
    # seg 2: z-corridor at x=tx-1..tx from z=112 to tz
    za,zb=min(112,tz),max(112,tz)
    clearstrip(tx-1,ylo,za,tx,yhi,zb)
    # make sure the door front is open + the foyer west door leads here
    clearstrip(114,ylo,111,115,yhi,112)
    # corridor lights
    for x in range(xa,xb+1,6): sb(x,yhi,111,"sea_lantern")
    for z in range(za,zb+1,6): sb(tx,yhi,z,"sea_lantern")
    # signpost at the foyer pointing to the room
    sb(114,ylo+2,113,f"oak_wall_sign[facing=west]{{front_text:{{messages:['\"-> {name}\"','\"\"','\"\"','\"\"']}}}}")
    print(f"{name} y{fy}: room door ~({rx},{ylo},{tz}); carved access from foyer")

cmd("forceload remove all")
cmd("gamerule logAdminCommands true"); cmd("gamerule sendCommandFeedback true")
print("ACCESS CORRIDORS DONE")
