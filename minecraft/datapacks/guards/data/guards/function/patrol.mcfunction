# Loop tick (every 5s). Only maintain guards when a player is near the castle/grounds/fair
# (so chunks are loaded, counts are accurate, and we don't over-spawn into unloaded chunks).
execute if entity @a[x=160,y=40,z=55,dx=150,dy=140,dz=125] run function guards:maintain
schedule function guards:patrol 100t replace
