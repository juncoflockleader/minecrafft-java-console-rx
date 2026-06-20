import socket, struct
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
cmd("gamerule logAdminCommands false"); cmd("gamerule sendCommandFeedback false")
cmd("forceload add 70 62 170 162")

FL=[(104,110),(110,118),(118,126),(126,134),(134,142),(142,150)]
# 1) rebuild elevator foyers + auto-doors
for fy,cy in FL:
    surf=fy+1
    fill(115,surf,107,115,cy-1,117,"gray_concrete"); fill(125,surf,107,125,cy-1,117,"gray_concrete")
    fill(115,surf,107,125,cy-1,107,"gray_concrete"); fill(115,surf,117,125,cy-1,117,"gray_concrete")
    fill(116,surf,108,124,cy-1,116,"air")
    fill(119,surf,111,121,cy-1,113,"air")          # shaft column clear
    fill(115,surf,111,115,surf+1,113,"air")
    sb(115,surf,112,"iron_door[facing=west,half=lower]"); sb(115,surf+1,112,"iron_door[facing=west,half=upper]")
    sb(114,surf,112,"stone_pressure_plate"); sb(116,surf,112,"stone_pressure_plate")
    sb(120,cy-1,108,"sea_lantern")
# 2) re-place ladder AFTER foyers (so the shaft-clear doesn't wipe it)
fill(121,104,112,121,148,112,"gray_concrete")
fill(120,104,112,120,148,112,"ladder[facing=west]")
# re-open floor holes for the ladder landings
for fy,cy in FL:
    fill(119,fy,111,121,fy,113,"air"); sb(121,fy,112,"gray_concrete"); sb(120,fy,112,"ladder[facing=west]")
cmd("forceload remove all")
cmd("gamerule logAdminCommands true"); cmd("gamerule sendCommandFeedback true")
print("foyers + ladder restored")
print("ladder mid:", cmd("execute if block 120 130 112 minecraft:ladder"))
print("foyer door y126:", cmd("execute if block 115 127 112 minecraft:iron_door"))
