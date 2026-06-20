forceload add 70 62 170 162
forceload add 570 62 670 162
clone 570 90 62 670 92 162 70 90 62 replace force
clone 570 93 62 670 95 162 70 93 62 replace force
clone 570 96 62 670 98 162 70 96 62 replace force
clone 570 99 62 670 101 162 70 99 62 replace force
clone 570 102 62 670 104 162 70 102 62 replace force
clone 570 105 62 670 107 162 70 105 62 replace force
clone 570 108 62 670 110 162 70 108 62 replace force
clone 570 111 62 670 113 162 70 111 62 replace force
clone 570 114 62 670 116 162 70 114 62 replace force
clone 570 117 62 670 119 162 70 117 62 replace force
clone 570 120 62 670 122 162 70 120 62 replace force
clone 570 123 62 670 125 162 70 123 62 replace force
clone 570 126 62 670 128 162 70 126 62 replace force
clone 570 129 62 670 131 162 70 129 62 replace force
clone 570 132 62 670 134 162 70 132 62 replace force
clone 570 135 62 670 137 162 70 135 62 replace force
clone 570 138 62 670 140 162 70 138 62 replace force
clone 570 141 62 670 143 162 70 141 62 replace force
clone 570 144 62 670 146 162 70 144 62 replace force
clone 570 147 62 670 149 162 70 147 62 replace force
clone 570 150 62 670 152 162 70 150 62 replace force
clone 570 153 62 670 155 162 70 153 62 replace force
clone 570 156 62 670 158 162 70 156 62 replace force
clone 570 159 62 670 161 162 70 159 62 replace force
clone 570 162 62 670 164 162 70 162 62 replace force
clone 570 165 62 670 167 162 70 165 62 replace force
clone 570 168 62 670 170 162 70 168 62 replace force
clone 570 171 62 670 173 162 70 171 62 replace force
clone 570 174 62 670 176 162 70 174 62 replace force
clone 570 177 62 670 179 162 70 177 62 replace force
clone 570 180 62 670 182 162 70 180 62 replace force
clone 570 183 62 670 185 162 70 183 62 replace force
clone 570 186 62 670 188 162 70 186 62 replace force
clone 570 189 62 670 190 162 70 189 62 replace force
kill @e[type=arsenal:mech,x=130,y=110,z=95,dx=50,dy=40,dz=40]
summon arsenal:mech 150 119 112 {Rotation:[-90f,0f]}
function dsgate:install
forceload remove all
say [Death Star] materialized at origin.
