# Summon one guard at the next courtyard post (rotates through 4 posts).
execute if score #post guards matches 0 run summon iron_golem 216 67 88 {Tags:["castle_guard"],PersistenceRequired:1b,CustomName:'{"text":"Castle Guard"}'}
execute if score #post guards matches 1 run summon iron_golem 248 67 88 {Tags:["castle_guard"],PersistenceRequired:1b,CustomName:'{"text":"Castle Guard"}'}
execute if score #post guards matches 2 run summon iron_golem 232 67 150 {Tags:["castle_guard"],PersistenceRequired:1b,CustomName:'{"text":"Castle Guard"}'}
execute if score #post guards matches 3 run summon iron_golem 196 67 120 {Tags:["castle_guard"],PersistenceRequired:1b,CustomName:'{"text":"Castle Guard"}'}
scoreboard players add #post guards 1
execute if score #post guards matches 4.. run scoreboard players set #post guards 0
