scoreboard players set #present dsgate 0
execute if entity @a[x=161,dx=7,y=118,dy=3,z=101,dz=22] run scoreboard players set #present dsgate 1
execute if score #present dsgate matches 1 run scoreboard players set #target dsgate 12
execute if score #present dsgate matches 1 run scoreboard players set #close dsgate 0
execute if score #present dsgate matches 0 run scoreboard players add #close dsgate 1
execute if score #close dsgate matches 100.. run scoreboard players set #target dsgate 0
execute if score #target dsgate matches 12 if score #wasopen dsgate matches 0 run function dsgate:klaxon_start
execute if score #target dsgate matches 12 run scoreboard players set #wasopen dsgate 1
execute if score #target dsgate matches 0 if score #wasopen dsgate matches 1 run function dsgate:klaxon_start
execute if score #target dsgate matches 0 run scoreboard players set #wasopen dsgate 0
execute if score #g dsgate matches 1.. run particle minecraft:dust{color:[0.25,0.55,1.0],scale:1.4} 164 129.5 112 0.3 11 11 0 130 force
scoreboard players add #t dsgate 1
execute if score #t dsgate matches 2.. run function dsgate:do_step
