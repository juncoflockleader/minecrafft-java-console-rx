# Clear all guards and reset the rotation (they will re-muster on the next patrol tick).
kill @e[type=iron_golem,tag=castle_guard]
scoreboard players set #post guards 0
tellraw @a {"text":"[Castle Guards] reset — guards will re-muster shortly.","color":"yellow"}
