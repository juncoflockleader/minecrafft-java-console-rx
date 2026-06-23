# Stop the guard loop and remove existing guards.
schedule clear guards:patrol
kill @e[type=iron_golem,tag=castle_guard]
tellraw @a {"text":"[Castle Guards] disabled.","color":"red"}
