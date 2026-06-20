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
CX,CY,CZ,RI=120,140,112,49
cmd("gamerule logAdminCommands false"); cmd("gamerule sendCommandFeedback false")
cmd("forceload add 70 62 170 162")

# rebuild the curved bulkhead at x=132 (separates hangar from facility), above the deck
HB=132
for y in range(119, CY+48):
    t=RI*RI-(HB-CX)**2-(y-CY)**2
    if t<0: continue
    zr=int(math.floor(math.sqrt(t)))
    fill(HB,y,CZ-zr,HB,y,CZ+zr,"gray_concrete")

# cut a 2-wide FACILITY auto-door + a short stub corridor into the maze
fill(132,119,111,132,120,112,"air")
sb(132,119,111,"iron_door[facing=east,half=lower]"); sb(132,120,111,"iron_door[facing=east,half=upper]")
sb(132,119,112,"iron_door[facing=east,half=lower]"); sb(132,120,112,"iron_door[facing=east,half=upper]")
sb(133,119,111,"stone_pressure_plate"); sb(133,119,112,"stone_pressure_plate")   # hangar side
sb(131,119,111,"stone_pressure_plate"); sb(131,119,112,"stone_pressure_plate")   # facility side
# stub corridor from the door into the maze (clear walls in the way), + floor + light
fill(126,119,111,131,120,112,"air")
fill(126,118,111,131,118,112,"yellow_terracotta")
sb(128,121,111,"sea_lantern")
sb(134,122,112,f"oak_wall_sign[facing=east]{{front_text:{{messages:['\"FACILITY\"','\"\"','\"\"','\"\"']}}}}")

cmd("forceload remove all")
cmd("gamerule logAdminCommands true"); cmd("gamerule sendCommandFeedback true")
print("bulkhead+door rebuilt")
print("bulkhead:", cmd("execute if block 132 123 112 minecraft:gray_concrete"))
print("door:", cmd("execute if block 132 119 111 minecraft:iron_door"))
print("hangar open at door front (140,120,112):", cmd("execute if block 140 120 112 minecraft:air"))
print("stub into maze (129,119,112) air:", cmd("execute if block 129 119 112 minecraft:air"))
