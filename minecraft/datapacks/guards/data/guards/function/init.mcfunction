# Set up the guard system. Runs on world load / datapack reload (#minecraft:load).
scoreboard objectives add guards dummy
scoreboard players set #cap guards 6
scoreboard players set #post guards 0
schedule function guards:patrol 40t replace
tellraw @a {"text":"[Castle Guards] online — up to 6 iron golems will defend the castle.","color":"gold"}
