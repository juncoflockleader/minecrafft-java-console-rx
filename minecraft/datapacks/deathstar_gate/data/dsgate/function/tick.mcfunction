scoreboard players set #present dsgate 0
execute if entity @a[x=161,dx=7,y=118,dy=3,z=101,dz=22] run scoreboard players set #present dsgate 1
execute if score #present dsgate matches 1 run scoreboard players set #target dsgate 12
execute if score #present dsgate matches 1 run scoreboard players set #close dsgate 0
execute if score #present dsgate matches 0 run scoreboard players add #close dsgate 1
execute if score #close dsgate matches 100.. run scoreboard players set #target dsgate 0
scoreboard players add #t dsgate 1
execute if score #t dsgate matches 2.. run function dsgate:do_step
