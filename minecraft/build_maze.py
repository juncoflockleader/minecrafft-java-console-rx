import socket, struct, math, random
HOST, PORT, PW = "127.0.0.1", 25575, "GU+bvxeYn7dnS7qY"
s = socket.create_connection((HOST, PORT), timeout=30); _id=0
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

CX,CZ,RI = 120,112,49
WALL="white_concrete"; FLOORMAT="light_gray_concrete"
def intr(y):
    t=RI*RI-(y-140)**2; return math.sqrt(t) if t>0 else 0
def excl(x,z):   # keep elevator foyer + spiral well clear of the maze
    return (114<=x<=126 and 106<=z<=118) or (114<=x<=126 and 94<=z<=106)

DECKS=[(104,110,"ARMORY"),(110,118,"BARRACKS"),(118,126,"OFFICES"),
       (126,134,"CONTROL"),(134,142,"CONFERENCE"),(142,148,"AMENITIES")]
P=3   # cell pitch (2-wide corridor + 1 wall)

def build_floor(fy, cy, name, seed):
    random.seed(seed)
    rr=int(intr(fy))-2
    ylo, yhi = fy+1, cy-1
    X0=CX-48; Z0=CZ-48
    # which cells are usable (corridor 2x2 inside disk, not in exclusion)
    cells={}
    ni=(96)//P
    for i in range(ni):
        for j in range(ni):
            ccx=X0+i*P+1; ccz=Z0+j*P+1
            mx,mz=ccx+0.5,ccz+0.5
            if (mx-CX)**2+(mz-CZ)**2 <= (rr-1)**2 and not (excl(ccx,ccz) or excl(ccx+1,ccz+1)):
                cells[(i,j)]=set()
    if not cells: return 0
    # recursive backtracker
    start=next(iter(cells)); stack=[start]; seen={start}
    while stack:
        c=stack[-1]; i,j=c
        nbrs=[(d,(i+dx,j+dz)) for d,(dx,dz) in [('E',(1,0)),('W',(-1,0)),('S',(0,1)),('N',(0,-1))] if (i+dx,j+dz) in cells and (i+dx,j+dz) not in seen]
        if not nbrs: stack.pop(); continue
        d,n=random.choice(nbrs); cells[c].add(d)
        cells[n].add({'E':'W','W':'E','S':'N','N':'S'}[d]); seen.add(n); stack.append(n)
    # ceiling (enclose) + floor reskin
    nb=0
    for z in range(CZ-rr,CZ+rr+1):
        t=rr*rr-(z-CZ)**2
        if t<0: continue
        xo=int(math.sqrt(t))
        fill(CX-xo,cy,z,CX+xo,cy,z,WALL)            # ceiling slab
        fill(CX-xo,fy,z,CX+xo,fy,z,FLOORMAT)        # floor
        fill(CX-xo,ylo,z,CX+xo,yhi,z,"air")         # clear the room volume
    # rebuild elevator foyer access stays clear (it was inside excl, untouched by clear? clear hit it) -> re-open it
    fill(116,ylo,108,124,yhi,116,"air"); fill(116,ylo,96,124,yhi,104,"air")
    # build maze walls
    for (i,j),ps in cells.items():
        ox=X0+i*P; oz=Z0+j*P; cx1=ox+1; cz1=oz+1
        fill(ox,ylo,oz,ox,yhi,oz,WALL)                                  # NW post
        if 'W' not in ps: fill(ox,ylo,cz1,ox,yhi,cz1+1,WALL)            # west wall
        if 'N' not in ps: fill(cx1,ylo,oz,cx1+1,yhi,oz,WALL)           # north wall
        if (i+1,j) not in cells: fill(ox+P,ylo,cz1,ox+P,yhi,cz1+1,WALL)# east boundary
        if (i,j+1) not in cells: fill(cx1,ylo,oz+P,cx1+1,yhi,oz+P,WALL)# south boundary
        if (i+1,j) not in cells or (i,j+1) not in cells: fill(ox+P,ylo,oz+P,ox+P,yhi,oz+P,WALL)
        nb+=1
    # lighting: ceiling lanterns scattered
    k=0
    for (i,j) in cells:
        k+=1
        if k%4==0:
            ox=X0+i*P; sb(ox+1,yhi,Z0+j*P+1,"lantern[hanging=true]")
    # connect maze to the elevator foyer + spiral (punch openings around them)
    for zz in (107,117): fill(113,ylo,zz-1,127,yhi,zz-1,"air")  # rough openings N/S of foyer band
    # a gated room: clear a 5x5 chamber at a deep-ish cell, add a gate + sign
    deep=list(cells)[len(cells)//2]
    di,dj=deep; rx=X0+di*P-2; rz=Z0+dj*P-2
    if (rx-CX)**2+(rz-CZ)**2 < (rr-3)**2:
        fill(rx,ylo,rz,rx+5,yhi,rz+5,"air")
        # walls of chamber
        fill(rx,ylo,rz,rx+5,yhi,rz,WALL); fill(rx,ylo,rz+5,rx+5,yhi,rz+5,WALL)
        fill(rx,ylo,rz,rx,yhi,rz+5,WALL); fill(rx+5,ylo,rz,rx+5,yhi,rz+5,WALL)
        # door (auto)
        fill(rx,ylo,rz+2,rx,ylo+1,rz+3,"air")
        sb(rx,ylo,rz+2,"iron_door[facing=east,half=lower]"); sb(rx,ylo+1,rz+2,"iron_door[facing=east,half=upper]")
        sb(rx-1,ylo,rz+2,"stone_pressure_plate"); sb(rx+1,ylo,rz+2,"stone_pressure_plate")
        sb(rx+2,ylo+2,rz+1,"sea_lantern")
        sign(rx+1,ylo+2,rz,"south",name)
    return nb

import sys
sel = sys.argv[1:] or [str(x) for x in range(len(DECKS))]
cmd("gamerule logAdminCommands false"); cmd("gamerule sendCommandFeedback false")
cmd("forceload add 70 62 170 162")
for idx in [int(x) for x in sel]:
    fy,cy,name=DECKS[idx]
    n=build_floor(fy,cy,name,1000+idx)
    print(f"floor y{fy} ({name}): {n} maze cells")
cmd("forceload remove all")
cmd("gamerule logAdminCommands true"); cmd("gamerule sendCommandFeedback true")
print("MAZE DONE")
