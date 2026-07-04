import os 
 
# POE2 Style Dungeon Generator 
# Creates connected room nodes like POE2's Atlas map 
 
dungeon_code = ''' 
import random 
import pygame 
 
TILE_SIZE = 40 
ROOM_SIZE = 400 
 
class DungeonNode: 
    def __init__(self, x, y, node_type="normal"): 
        self.x = x 
        self.y = y 
        self.rect = pygame.Rect(x, y, ROOM_SIZE, ROOM_SIZE) 
        self.node_type = node_type  # "start", "normal", "elite", "boss" 
        self.connections = [] 
        self.cleared = False 
        self.doors = []  # [(door_rect, connected_node_index)] 
 
def generate_poe2_dungeon(floor_num): 
    """Generate POE2-style node map""" 
    nodes = [] 
    walls = [] 
    enemies = [] 
    items = [] 
    doors = []  # [(rect, node_a, node_b)] 
 
    num_nodes = min(3 + floor_num, 8) 
 
    # Center positions 
    spacing = ROOM_SIZE + 120 
    cols = 3 
    rows = (num_nodes + 2) // 3 
    start_x = 200 
    start_y = 100 
 
    # Generate nodes in a connected grid 
    positions = [] 
    for row in range(rows): 
        for col in range(cols): 
            if len(positions) 
                break 
            x = start_x + col * spacing + random.randint(-30, 30) 
            y = start_y + row * spacing + random.randint(-30, 30) 
            positions.append((x, y)) 
 
    # Create nodes 
    for i, (x, y) in enumerate(positions): 
        if i == 0: 
            ntype = "start" 
        elif i == len(positions) - 1: 
            ntype = "boss" 
            ntype = "elite" 
        else: 
            ntype = "normal" 
        nodes.append(DungeonNode(x, y, ntype)) 
 
    # Connect nodes (grid connections + random extras) 
    for i, node in enumerate(nodes): 
        # Connect right 
        right_idx = i + 1 
            node.connections.append(right_idx) 
            nodes[right_idx].connections.append(i) 
 
        # Connect down 
        down_idx = i + cols 
            node.connections.append(down_idx) 
            nodes[down_idx].connections.append(i) 
 
    # Build walls and doors for each node 
    for i, node in enumerate(nodes): 
        # Room walls 
        for wx in range(node.x, node.x + ROOM_SIZE, TILE_SIZE): 
            if wx not in [node.x + ROOM_SIZE//2 - TILE_SIZE]:  # Leave gap for doors 
                walls.append(pygame.Rect(wx, node.y, TILE_SIZE, TILE_SIZE)) 
                walls.append(pygame.Rect(wx, node.y + ROOM_SIZE - TILE_SIZE, TILE_SIZE, TILE_SIZE)) 
        for wy in range(node.y, node.y + ROOM_SIZE, TILE_SIZE): 
            walls.append(pygame.Rect(node.x, wy, TILE_SIZE, TILE_SIZE)) 
            walls.append(pygame.Rect(node.x + ROOM_SIZE - TILE_SIZE, wy, TILE_SIZE, TILE_SIZE)) 
 
        # Create doors for connections (only once per pair) 
        for conn in node.connections: 
            if conn   # Only process each connection once 
                other = nodes[conn] 
                # Determine door position (between the two nodes) 
                mid_x = (node.x + ROOM_SIZE//2 + other.x + ROOM_SIZE//2) // 2 
                mid_y = (node.y + ROOM_SIZE//2 + other.y + ROOM_SIZE//2) // 2 
 
                # Create door rect 
                if abs(node.x - other.x)  - other.y): 
                    # Horizontal connection 
                    door_x = max(node.x, other.x) + ROOM_SIZE - TILE_SIZE 
                    door_y = mid_y - 25 
                    door_rect = pygame.Rect(door_x, door_y, TILE_SIZE, 50) 
                    # Remove wall at door position 
                else: 
                    # Vertical connection 
                    door_x = mid_x - 25 
                    door_y = max(node.y, other.y) + ROOM_SIZE - TILE_SIZE 
                    door_rect = pygame.Rect(door_x, door_y, 50, TILE_SIZE) 
 
                doors.append({"rect": door_rect, "node_a": i, "node_b": conn, "locked": True}) 
 
        # Spawn enemies 
        if node.node_type == "start": 
            continue  # No enemies in start 
        elif node.node_type == "boss": 
            from enemy import Enemy 
            enemies.append(Enemy(node.x + ROOM_SIZE//2, node.y + ROOM_SIZE//2, "boss", floor_num)) 
        elif node.node_type == "elite": 
            from enemy import Enemy 
            for _ in range(random.randint(4, 6)): 
                ex = node.x + random.randint(60, ROOM_SIZE - 60) 
                ey = node.y + random.randint(60, ROOM_SIZE - 60) 
                etype = random.choice(["skeleton", "zombie", "mage"]) 
                enemies.append(Enemy(ex, ey, etype, floor_num)) 
        else: 
            from enemy import Enemy 
            for _ in range(random.randint(2, 4)): 
                ex = node.x + random.randint(60, ROOM_SIZE - 60) 
                ey = node.y + random.randint(60, ROOM_SIZE - 60) 
                etype = random.choice(["skeleton", "zombie", "archer", "mage"]) 
                enemies.append(Enemy(ex, ey, etype, floor_num)) 
 
        # Spawn loot 
        from items import generate_loot 
        loot_count = 3 if node.node_type == "boss" else random.randint(1, 2) 
        for _ in range(loot_count): 
            ix = node.x + random.randint(60, ROOM_SIZE - 60) 
            iy = node.y + random.randint(60, ROOM_SIZE - 60) 
            items.append((ix, iy, generate_loot(floor_num))) 
 
    start_node = nodes[0] 
    return walls, enemies, items, doors, nodes, start_node 
''' 
 
# Now patch main.py 
with open("main.py", "r", encoding="utf-8") as f: 
    content = f.read() 
 
# Find and replace the old generate_dungeon function 
import re 
old_func = r"def generate_dungeon\(floor_num\):.*?(?=\ndef|\nclass|\Z)" 
content = re.sub(old_func, dungeon_code.strip(), content, flags=re.DOTALL) 
 
# Update the main function to use new dungeon 
content = content.replace("from dungeon import generate_dungeon", "") 
content = content.replace("generate_dungeon(floor)", "generate_poe2_dungeon(floor)") 
content = content.replace("generate_dungeon(floor_num)", "generate_poe2_dungeon(floor_num)") 
 
with open("main.py", "w", encoding="utf-8") as f: 
    f.write(content) 
 
print("POE2 dungeon system installed!") 
