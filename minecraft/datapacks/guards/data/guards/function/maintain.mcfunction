# Count our living guards in the castle region; if below the cap, muster one.
execute store result score #cur guards run execute if entity @e[type=iron_golem,tag=castle_guard,x=160,y=40,z=55,dx=150,dy=140,dz=125]
execute if score #cur guards < #cap guards run function guards:muster
