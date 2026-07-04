"""
Dungeon generation - rooms, corridors, walls, enemy placement
"""
import random
import pygame
from settings import *
from enemy import Enemy
from items import generate_loot

def generate_dungeon(floor_num):
    walls = []
    enemies = []
    items = []
    
    # Border walls
    for x in range(0, DUNGEON_WIDTH, TILE_SIZE):
        walls.append(pygame.Rect(x, 0, TILE_SIZE, TILE_SIZE))
        walls.append(pygame.Rect(x, DUNGEON_HEIGHT - TILE_SIZE, TILE_SIZE, TILE_SIZE))
    for y in range(0, DUNGEON_HEIGHT, TILE_SIZE):
        walls.append(pygame.Rect(0, y, TILE_SIZE, TILE_SIZE))
        walls.append(pygame.Rect(DUNGEON_WIDTH - TILE_SIZE, y, TILE_SIZE, TILE_SIZE))
    
    # Generate rooms
    num_rooms = 6 + floor_num
    rooms = []
    max_attempts = 100
    
    for _ in range(max_attempts):
        if len(rooms) >= num_rooms:
            break
            
        w = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        x = random.randint(100, DUNGEON_WIDTH - w - 100)
        y = random.randint(100, DUNGEON_HEIGHT - h - 100)
        
        new_room = pygame.Rect(x, y, w, h)
        
        # Check overlap with existing rooms
        overlap = False
        for room in rooms:
            if new_room.inflate(80, 80).colliderect(room):
                overlap = True
                break
        
        if not overlap:
            rooms.append(new_room)
    
    # Sort rooms by x position for corridor generation
    rooms.sort(key=lambda r: r.centerx)
    
    # Create corridors between rooms
    corridors = []
    for i in range(len(rooms) - 1):
        room1 = rooms[i]
        room2 = rooms[i + 1]
        
        # Create L-shaped corridor
        x1, y1 = room1.centerx, room1.centery
        x2, y2 = room2.centerx, room2.centery
        
        # Horizontal then vertical
        corridor1 = pygame.Rect(min(x1, x2) - TILE_SIZE//2, y1 - TILE_SIZE//2, 
                                abs(x2 - x1) + TILE_SIZE, TILE_SIZE)
        corridor2 = pygame.Rect(x2 - TILE_SIZE//2, min(y1, y2) - TILE_SIZE//2,
                                TILE_SIZE, abs(y2 - y1) + TILE_SIZE)
        
        corridors.append(corridor1)
        corridors.append(corridor2)
    
    # Build wall list (everything is wall by default, then we carve)
    # Fill entire dungeon with wall grid
    all_walls = set()
    for gx in range(0, DUNGEON_WIDTH, TILE_SIZE):
        for gy in range(0, DUNGEON_HEIGHT, TILE_SIZE):
            all_walls.add((gx, gy))
    
    # Remove tiles that are inside rooms
    for room in rooms:
        for gx in range(room.x, room.x + room.width, TILE_SIZE):
            for gy in range(room.y, room.y + room.height, TILE_SIZE):
                all_walls.discard((gx, gy))
    
    # Remove tiles that are part of corridors
    for corridor in corridors:
        for gx in range(corridor.x, corridor.x + corridor.width, TILE_SIZE):
            for gy in range(corridor.y, corridor.y + corridor.height, TILE_SIZE):
                all_walls.discard((gx, gy))
    
    # Convert remaining tiles to wall rects
    walls = [pygame.Rect(x, y, TILE_SIZE, TILE_SIZE) for (x, y) in all_walls]
    
    # Add border walls back
    for x in range(0, DUNGEON_WIDTH, TILE_SIZE):
        walls.append(pygame.Rect(x, 0, TILE_SIZE, TILE_SIZE))
        walls.append(pygame.Rect(x, DUNGEON_HEIGHT - TILE_SIZE, TILE_SIZE, TILE_SIZE))
    for y in range(0, DUNGEON_HEIGHT, TILE_SIZE):
        walls.append(pygame.Rect(0, y, TILE_SIZE, TILE_SIZE))
        walls.append(pygame.Rect(DUNGEON_WIDTH - TILE_SIZE, y, TILE_SIZE, TILE_SIZE))
    
    # Spawn enemies in each room
    for i, room in enumerate(rooms):
        if i == len(rooms) - 1:
            # Boss room (last room)
            num_enemies = 1
            enemy_types_list = ['boss']
        else:
            num_enemies = random.randint(2, 5) + floor_num // 2
            enemy_types_list = ['skeleton', 'zombie', 'archer', 'mage']
        
        for _ in range(num_enemies):
            ex = room.x + random.randint(60, room.width - 60)
            ey = room.y + random.randint(60, room.height - 60)
            enemy_type = random.choice(enemy_types_list)
            enemies.append(Enemy(ex, ey, enemy_type, floor_num))
        
        # Spawn loot
        loot_count = random.randint(1, 3)
        if i == len(rooms) - 1:
            loot_count = 3  # Boss room has more loot
        for _ in range(loot_count):
            ix = room.x + random.randint(60, room.width - 60)
            iy = room.y + random.randint(60, room.height - 60)
            items.append((ix, iy, generate_loot(floor_num)))
    
    # Also spawn some enemies in corridors
    for _ in range(floor_num):
        if corridors:
            corridor = random.choice(corridors)
            ex = corridor.x + random.randint(20, corridor.width - 20)
            ey = corridor.y + random.randint(20, corridor.height - 20)
            enemy_type = random.choice(['skeleton', 'archer'])
            enemies.append(Enemy(ex, ey, enemy_type, floor_num))
    
    # Start room is the first room
    start_room = rooms[0] if rooms else pygame.Rect(100, 100, 400, 400)
    
    return walls, enemies, items, start_room