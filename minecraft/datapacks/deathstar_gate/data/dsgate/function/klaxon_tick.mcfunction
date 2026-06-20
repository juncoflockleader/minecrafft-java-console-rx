execute if score #kl dsgate matches 5 run playsound minecraft:block.note_block.bass block @a[x=110,dx=60,y=80,dy=120,z=52,dz=120] 164 130 112 8 0.5
execute if score #kl dsgate matches 4 run playsound minecraft:block.note_block.bass block @a[x=110,dx=60,y=80,dy=120,z=52,dz=120] 164 130 112 8 0.9
execute if score #kl dsgate matches 3 run playsound minecraft:block.note_block.bass block @a[x=110,dx=60,y=80,dy=120,z=52,dz=120] 164 130 112 8 0.5
execute if score #kl dsgate matches 2 run playsound minecraft:block.note_block.bass block @a[x=110,dx=60,y=80,dy=120,z=52,dz=120] 164 130 112 8 0.9
execute if score #kl dsgate matches 1 run playsound minecraft:block.note_block.bass block @a[x=110,dx=60,y=80,dy=120,z=52,dz=120] 164 130 112 8 0.5
scoreboard players remove #kl dsgate 1
execute if score #kl dsgate matches 1.. run schedule function dsgate:klaxon_tick 5t
