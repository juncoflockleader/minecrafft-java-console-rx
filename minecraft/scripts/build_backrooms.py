import socket, struct, math
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
def fill(a,b,c,d,e,f,bl,extra=""): return cmd(f"fill {a} {b} {c} {d} {e} {f} {bl} {extra}".strip())
def sb(x,y,z,bl): return cmd(f"setblock {x} {y} {z} {bl}")
CX,CZ,RI=120,112,49
def intr(y):
    t=RI*RI-(y-140)**2; return math.sqrt(t) if t>0 else 0
DECKS=[(104,110),(110,118),(118,126),(126,134),(134,142),(142,148)]
WALLY="yellow_terracotta"; FLOORY="yellow_terracotta"

cmd("gamerule logAdminCommands false"); cmd("gamerule sendCommandFeedback false")
cmd("forceload add 70 62 170 162")

# ---- PART A: spiral landing rings (additive; radius-4 well edge, never touches treads at r3) ----
for fy,cy in DECKS:
    y=fy
    fill(116,y,96,124,y,96,FLOORY)    # north edge
    fill(116,y,104,124,y,104,FLOORY)  # south edge
    fill(116,y,96,116,y,104,FLOORY)   # west edge
    fill(124,y,96,124,y,104,FLOORY)   # east edge
    # ensure 2-high clearance above the ring (well interior already air; this only clears the ring cells)
    fill(116,y+1,96,124,y+2,96,"air"); fill(116,y+1,104,124,y+2,104,"air")
    fill(116,y+1,96,116,y+2,104,"air"); fill(124,y+1,96,124,y+2,104,"air")
    # connect ring south edge -> foyer band floor (z105) so spiral reaches the foyer/maze
    fill(116,y,105,124,y,105,FLOORY); fill(116,y+1,105,124,y+2,105,"air")

# ---- PART B: backrooms re-skin (replace filters = safe) ----
for fy,cy in DECKS:
    rr=int(intr(fy))-1
    # walls (white_concrete) -> mustard, layer by layer, excluding the ceiling at cy
    for y in range(fy+1, cy):
        fill(CX-rr,y,CZ-rr,CX+rr,y,CZ+rr,WALLY,"replace white_concrete")
    # floor (light_gray_concrete) -> mustard
    fill(CX-rr,fy,CZ-rr,CX+rr,fy,CZ+rr,FLOORY,"replace light_gray_concrete")
    # remove the old hanging lanterns
    fill(CX-rr,fy+1,CZ-rr,CX+rr,cy-1,CZ+rr,"air","replace lantern")
    # flush fluorescent ceiling panels (replace the white ceiling tile only)
    for x in range(CX-rr+2, CX+rr-1, 6):
        for z in range(CZ-rr+2, CZ+rr-1, 6):
            if (x-CX)**2+(z-CZ)**2 <= (rr-2)**2:
                cmd(f"fill {x} {cy} {z} {x} {cy} {z} sea_lantern replace white_concrete")

cmd("forceload remove all")
cmd("gamerule logAdminCommands true"); cmd("gamerule sendCommandFeedback true")
print("landings + backrooms reskin done")
# verify spiral intact + landings + reskin
def pos(i):
    a=math.radians(i*45); return CX+round(3*math.cos(a)), 100+round(3*math.sin(a))
for i in (0,16,32):
    x,z=pos(i); print(f" spiral step{i} ({x},{104+i},{z}):", cmd(f"execute if block {x} {104+i} {z} #minecraft:stairs"))
print(" landing (116,118,100):", cmd("execute if block 116 118 100 minecraft:yellow_terracotta"))
print(" wall recolor (108,106,112):", cmd("execute if block 108 106 112 minecraft:yellow_terracotta"))
print(" floor recolor (100,118,112):", cmd("execute if block 100 118 112 minecraft:yellow_terracotta"))
