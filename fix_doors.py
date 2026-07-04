import re 
with open('main.py', 'r') as f: content = f.read() 
old = "    total_w = cols * ROOM_WIDTH + (cols + 1) * ROOM_SPACING" 
new = "    total_w = cols * ROOM_WIDTH + (cols + 1) * ROOM_SPACING\n    offset_x = max(0, (3000 - total_w) // 2)\n    offset_y = max(0, (3000 - total_h) // 2)" 
content = content.replace(old, new) 
old2 = "        rx = ROOM_SPACING + col * (ROOM_WIDTH + ROOM_SPACING)" 
new2 = "        rx = offset_x + ROOM_SPACING + col * (ROOM_WIDTH + ROOM_SPACING)" 
content = content.replace(old2, new2) 
with open('main.py', 'w') as f: f.write(content) 
print("Fixed!") 
