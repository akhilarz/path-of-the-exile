"""
PATH OF THE EXILE - Main Game
Multi-room dungeon with locked doors, proper movement & combat
"""
import pygame
import random
import math

# =============================================================================
# SETTINGS
# =============================================================================
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 40, 40)
DARK_RED = (139, 0, 0)
GREEN = (40, 220, 40)
DARK_GREEN = (0, 100, 0)
BLUE = (60, 60, 220)
YELLOW = (220, 220, 40)
ORANGE = (255, 165, 0)
GOLD = (255, 215, 0)
PURPLE = (160, 50, 220)
GRAY = (128, 128, 128)
DARK_GRAY = (30, 30, 30)
BROWN = (101, 67, 33)
DARK_BROWN = (60, 40, 20)
LIGHT_GRAY = (180, 180, 180)
CYAN = (0, 200, 200)

PLAYER_SPEED = 250
PLAYER_SIZE = 16
TILE_SIZE = 40
ROOM_MIN_SIZE = 300
ROOM_MAX_SIZE = 500

ENEMY_TYPES = {
    "skeleton": {"hp": 30, "damage": 8, "speed": 100, "xp": 20, "color": (200, 200, 200), "size": 14},
    "zombie": {"hp": 60, "damage": 12, "speed": 50, "xp": 30, "color": (100, 150, 80), "size": 18},
    "archer": {"hp": 25, "damage": 10, "speed": 80, "xp": 25, "color": (180, 160, 200), "size": 12},
    "mage": {"hp": 35, "damage": 15, "speed": 70, "xp": 35, "color": (150, 50, 200), "size": 13},
    "boss": {"hp": 300, "damage": 30, "speed": 60, "xp": 200, "color": (220, 20, 20), "size": 28},
}

SKILLS = {
    'cleave': {'name': 'Cleave', 'mult': 1.8, 'mana': 12, 'cd': 0.8, 'type': 'aoe', 'radius': 100},
    'heavy_strike': {'name': 'Heavy Strike', 'mult': 3.0, 'mana': 18, 'cd': 1.5, 'type': 'single'},
    'fireball': {'name': 'Fireball', 'mult': 2.0, 'mana': 22, 'cd': 1.2, 'type': 'projectile'},
}

# =============================================================================
# CAMERA
# =============================================================================
class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
    
    def apply(self, rect):
        return pygame.Rect(rect.x - self.x, rect.y - self.y, rect.width, rect.height)
    
    def apply_point(self, x, y):
        return (x - self.x, y - self.y)
    
    def world_to_screen(self, screen_x, screen_y):
        return (screen_x + self.x, screen_y + self.y)
    
    def update(self, target_x, target_y):
        self.x += (target_x - SCREEN_WIDTH // 2 - self.x) * 0.1
        self.y += (target_y - SCREEN_HEIGHT // 2 - self.y) * 0.1

# =============================================================================
# ITEM
# =============================================================================
class Item:
    def __init__(self, name, item_type, rarity="Normal", damage=0, armor=0, 
                 health=0, speed=0, crit=0):
        self.name = name
        self.item_type = item_type
        self.rarity = rarity
        self.damage = damage
        self.armor = armor
        self.health = health
        self.speed = speed
        self.crit = crit
    
    @property
    def color(self):
        colors = {"Magic": BLUE, "Rare": YELLOW, "Unique": ORANGE}
        return colors.get(self.rarity, WHITE)

def generate_loot(level):
    roll = random.random()
    if roll < 0.45: rarity = "Normal"
    elif roll < 0.80: rarity = "Magic"
    elif roll < 0.96: rarity = "Rare"
    else: rarity = "Unique"
    
    item_type = random.choice(['weapon', 'armor', 'helmet', 'boots', 'ring'])
    
    if item_type == 'weapon':
        names = ["Rusty Sword", "Iron Blade", "Steel Sword", "War Axe"]
        dmg = random.randint(3, 8) + level * 2
        if rarity == "Rare": dmg = int(dmg * 2)
        if rarity == "Unique": dmg = int(dmg * 3)
        return Item(random.choice(names), 'weapon', rarity, damage=dmg)
    elif item_type == 'armor':
        names = ["Leather Armor", "Chainmail", "Iron Plate"]
        arm = random.randint(5, 15) + level * 3
        hp = random.randint(10, 30) + level * 5
        if rarity == "Rare": arm = int(arm * 2); hp = int(hp * 2)
        return Item(random.choice(names), 'armor', rarity, armor=arm, health=hp)
    elif item_type == 'helmet':
        names = ["Leather Cap", "Iron Helm", "Steel Crown"]
        arm = random.randint(3, 10) + level * 2
        hp = random.randint(5, 20) + level * 3
        return Item(random.choice(names), 'helmet', rarity, armor=arm, health=hp)
    elif item_type == 'boots':
        names = ["Leather Boots", "Iron Greaves", "Wind Walkers"]
        spd = random.randint(5, 20) + level * 2
        return Item(random.choice(names), 'boots', rarity, speed=spd)
    else:
        names = ["Bone Ring", "Silver Band", "Ruby Ring"]
        crit = random.randint(2, 10) + level
        dmg = random.randint(2, 6) + level
        return Item(random.choice(names), 'ring', rarity, damage=dmg, crit=crit)

# =============================================================================
# PARTICLE & EFFECTS
# =============================================================================
class Particle:
    def __init__(self, x, y, color, velocity, lifetime=0.5):
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = random.randint(2, 5)
    
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        return self.lifetime > 0
    
    def draw(self, screen, camera):
        alpha = self.lifetime / self.max_lifetime
        pos = camera.apply_point(self.x, self.y)
        pygame.draw.circle(screen, self.color, (int(pos[0]), int(pos[1])), int(self.size * alpha))

class FloatingText:
    def __init__(self, x, y, text, color, size="normal"):
        self.x = x
        self.y = y
        self.text = str(text)
        self.color = color
        self.lifetime = 1.0
        self.max_lifetime = 1.0
        self.size = size
    
    def update(self, dt):
        self.y -= 60 * dt
        self.lifetime -= dt
        return self.lifetime > 0
    
    def draw(self, screen, camera, font_small, font_large):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        font = font_large if self.size == "large" else font_small
        text_surface = font.render(self.text, True, self.color)
        text_surface.set_alpha(alpha)
        pos = camera.apply_point(self.x, self.y)
        screen.blit(text_surface, (pos[0] - text_surface.get_width()//2, pos[1]))

class Projectile:
    def __init__(self, x, y, target_x, target_y, damage, is_crit=False):
        self.x = x
        self.y = y
        self.damage = damage
        self.is_crit = is_crit
        self.speed = 500
        self.radius = 6
        self.lifetime = 2.0
        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx**2 + dy**2)
        if dist > 0:
            self.vx = (dx / dist) * self.speed
            self.vy = (dy / dist) * self.speed
        else:
            self.vx = 0
            self.vy = -self.speed
    
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        return self.lifetime > 0
    
    def draw(self, screen, camera):
        pos = camera.apply_point(self.x, self.y)
        color = GOLD if self.is_crit else YELLOW
        pygame.draw.circle(screen, color, (int(pos[0]), int(pos[1])), self.radius)

# =============================================================================
# ENEMY
# =============================================================================
class Enemy:
    def __init__(self, x, y, enemy_type, level):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.level = level
        stats = ENEMY_TYPES.get(enemy_type, ENEMY_TYPES["skeleton"])
        self.max_hp = stats["hp"] + level * 12
        self.damage = stats["damage"] + level * 2
        self.speed = stats["speed"] + level * 3
        self.xp = stats["xp"] + level * 5
        self.color = stats["color"]
        self.size = stats["size"]
        self.hp = self.max_hp
        self.rect = pygame.Rect(x - self.size, y - self.size, self.size*2, self.size*2)
        self.attack_timer = 0
        self.alive = True
    
    def update(self, dt, player, walls):
        if not self.alive: return None
        self.attack_timer -= dt
        
        dx = player.rect.centerx - self.x
        dy = player.rect.centery - self.y
        dist = math.sqrt(dx**2 + dy**2)
        
        if 30 < dist < 500 and dist > 0:
            move_x = (dx / dist) * self.speed * dt
            move_y = (dy / dist) * self.speed * dt
            new_x = self.x + move_x
            new_y = self.y + move_y
            test_rect = pygame.Rect(new_x - self.size, self.y - self.size, self.size*2, self.size*2)
            if not any(test_rect.colliderect(w) for w in walls):
                self.x = new_x
            test_rect = pygame.Rect(self.x - self.size, new_y - self.size, self.size*2, self.size*2)
            if not any(test_rect.colliderect(w) for w in walls):
                self.y = new_y
            self.rect.x = self.x - self.size
            self.rect.y = self.y - self.size
        
        if dist < 40 and self.attack_timer <= 0:
            self.attack_timer = 1.2
            return self.damage
        return None
    
    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False
            return True, self.xp
        return False, 0
    
    def draw(self, screen, camera):
        if not self.alive: return
        pos = camera.apply_point(self.x, self.y)
        x, y = int(pos[0]), int(pos[1])
        pygame.draw.circle(screen, BLACK, (x, y+2), self.size)
        pygame.draw.circle(screen, self.color, (x, y), self.size)
        pygame.draw.circle(screen, WHITE, (x, y), self.size, 2)
        eye = self.size // 3
        pygame.draw.circle(screen, RED, (x - eye, y - eye), 3)
        pygame.draw.circle(screen, RED, (x + eye, y - eye), 3)
        bar_w = self.size * 2
        bar_h = 4
        bar_x = x - bar_w // 2
        bar_y = y - self.size - 10
        hp_pct = self.hp / self.max_hp
        pygame.draw.rect(screen, DARK_RED, (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, int(bar_w * hp_pct), bar_h))

# =============================================================================
# PLAYER
# =============================================================================
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x - PLAYER_SIZE, y - PLAYER_SIZE, PLAYER_SIZE*2, PLAYER_SIZE*2)
        self.speed = PLAYER_SPEED
        self.level = 1
        self.xp = 0
        self.xp_to_level = 100
        self.max_hp = 150
        self.hp = 150
        self.max_mana = 80
        self.mana = 80
        self.base_damage = 15
        self.armor = 10
        self.crit_chance = 8
        self.attack_speed = 1.0
        self.skill_points = 0
        self.equipment = {
            'weapon': Item("Rusty Sword", 'weapon', 'Normal', damage=5),
            'armor': None, 'helmet': None, 'boots': None, 'ring': None,
        }
        self.inventory = []
        self.attack_timer = 0
        self.skill_cooldowns = {}
        self.alive = True
        self.unlocked_skills = ['cleave', 'heavy_strike', 'fireball']
        self.current_skill = 0
        self.recalculate_stats()
    
    def recalculate_stats(self):
        self.max_hp = 150 + self.level * 20
        self.max_mana = 80 + self.level * 10
        self.base_damage = 15 + self.level * 3
        self.armor = 10
        self.crit_chance = 8
        self.speed = PLAYER_SPEED
        for item in self.equipment.values():
            if item:
                self.base_damage += item.damage
                self.armor += item.armor
                self.max_hp += item.health
                self.crit_chance += item.crit
                if item.speed: self.speed = PLAYER_SPEED * (1 + item.speed / 100)
        self.hp = min(self.hp, self.max_hp)
        self.mana = min(self.mana, self.max_mana)
    
    def equip_item(self, item):
        old = self.equipment.get(item.item_type)
        if old: self.inventory.append(old)
        self.equipment[item.item_type] = item
        self.recalculate_stats()
    
    def get_damage(self, skill_mult=1.0):
        dmg = self.base_damage * skill_mult
        is_crit = random.random() * 100 < self.crit_chance
        if is_crit: dmg *= 1.8
        return random.randint(int(dmg * 0.85), int(dmg * 1.15)), is_crit
    
    def take_damage(self, damage):
        reduction = self.armor / (self.armor + 60)
        actual = max(1, int(damage * (1 - reduction)))
        self.hp -= actual
        if self.hp <= 0: self.alive = False
        return actual
    
    def basic_attack(self):
        if self.attack_timer > 0: return None
        self.attack_timer = 0.5 / self.attack_speed
        return self.get_damage()
    
    def use_skill(self, skill_name):
        if skill_name not in SKILLS: return None
        skill = SKILLS[skill_name]
        if skill_name in self.skill_cooldowns: return None
        if self.mana < skill['mana']: return None
        self.mana -= skill['mana']
        self.skill_cooldowns[skill_name] = skill['cd']
        dmg, crit = self.get_damage(skill['mult'])
        return {'damage': dmg, 'crit': crit, 'type': skill['type'], 
                'radius': skill.get('radius', 0), 'skill_name': skill_name}
    
    def gain_xp(self, amount):
        self.xp += amount
        leveled = False
        while self.xp >= self.xp_to_level:
            self.xp -= self.xp_to_level
            self.xp_to_level = int(self.xp_to_level * 1.5)
            self.level += 1
            self.skill_points += 1
            self.hp = self.max_hp
            self.mana = self.max_mana
            leveled = True
        if leveled: self.recalculate_stats()
        return leveled
    
    def update(self, dt, keys, walls):
        if not self.alive: return
        
        # MOVEMENT - Fixed
        vx = 0
        vy = 0
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            vy = -self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            vy = self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            vx = -self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            vx = self.speed
        
        # Normalize diagonal
        if vx != 0 and vy != 0:
            vx *= 0.707
            vy *= 0.707
        
        # Apply movement with collision
        new_x = self.x + vx * dt
        new_y = self.y + vy * dt
        
        # Check X movement
        test_rect_x = pygame.Rect(new_x - PLAYER_SIZE, self.y - PLAYER_SIZE, PLAYER_SIZE*2, PLAYER_SIZE*2)
        can_move_x = True
        for wall in walls:
            if test_rect_x.colliderect(wall):
                can_move_x = False
                break
        
        # Check Y movement
        test_rect_y = pygame.Rect(self.x - PLAYER_SIZE, new_y - PLAYER_SIZE, PLAYER_SIZE*2, PLAYER_SIZE*2)
        can_move_y = True
        for wall in walls:
            if test_rect_y.colliderect(wall):
                can_move_y = False
                break
        
        if can_move_x:
            self.x = new_x
        if can_move_y:
            self.y = new_y
        
        self.rect.x = self.x - PLAYER_SIZE
        self.rect.y = self.y - PLAYER_SIZE
        
        # Regen
        self.mana = min(self.max_mana, self.mana + 8 * dt)
        self.attack_timer = max(0, self.attack_timer - dt)
        
        # Update cooldowns
        for skill in list(self.skill_cooldowns.keys()):
            self.skill_cooldowns[skill] -= dt
            if self.skill_cooldowns[skill] <= 0:
                del self.skill_cooldowns[skill]
    
    def draw(self, screen, camera):
        if not self.alive: return
        pos = camera.apply_point(self.x, self.y)
        x, y = int(pos[0]), int(pos[1])
        pygame.draw.ellipse(screen, BLACK, (x-14, y+12, 28, 10))
        pygame.draw.circle(screen, (60, 100, 220), (x, y), PLAYER_SIZE)
        pygame.draw.circle(screen, WHITE, (x, y), PLAYER_SIZE, 2)
        pygame.draw.circle(screen, WHITE, (x-5, y-3), 4)
        pygame.draw.circle(screen, WHITE, (x+5, y-3), 4)
        pygame.draw.circle(screen, BLACK, (x-5, y-3), 2)
        pygame.draw.circle(screen, BLACK, (x+5, y-3), 2)

# =============================================================================
# DUNGEON - Multiple separate rooms with locked doors
# =============================================================================
class Door:
    def __init__(self, x, y, width, height, room_from, room_to):
        self.rect = pygame.Rect(x, y, width, height)
        self.room_from = room_from
        self.room_to = room_to
        self.locked = True
        self.color = RED  # Locked = red, Unlocked = green
    
    def unlock(self):
        self.locked = False
        self.color = GREEN
    
    def draw(self, screen, camera):
        pos = camera.apply(self.rect)
        pygame.draw.rect(screen, self.color, pos)
        pygame.draw.rect(screen, WHITE, pos, 2)
        if self.locked:
            # Draw lock symbol
            cx, cy = pos.centerx, pos.centery
            pygame.draw.circle(screen, WHITE, (cx, cy), 8, 2)
            pygame.draw.line(screen, WHITE, (cx-4, cy+4), (cx+4, cy+4), 2)

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
                if abs(node.x - other.x) > abs(node.y - other.y): 
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
class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
    
    def draw(self, screen, font, mouse_pos):
        color = GRAY if self.rect.collidepoint(mouse_pos) else DARK_GRAY
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=5)
        text_surf = font.render(self.text, True, WHITE)
        screen.blit(text_surf, (self.rect.x + 10, self.rect.y + 8))
    
    def clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

# =============================================================================
# MAIN GAME
# =============================================================================
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Path of the Exile")
    clock = pygame.time.Clock()
    
    font_tiny = pygame.font.Font(None, 16)
    font_small = pygame.font.Font(None, 20)
    font_medium = pygame.font.Font(None, 28)
    font_large = pygame.font.Font(None, 36)
    font_huge = pygame.font.Font(None, 52)
    
    MENU, PLAYING, INVENTORY, SKILL_TREE, DEAD = 0, 1, 2, 3, 4
    game_state = MENU
    
    player = Player(600, 500)
    floor = 1
    current_room = 0  # Track which room player is in
    
    walls, enemies, ground_items, start_room, doors, rooms = generate_poe2_dungeon(floor)
    player.x = start_room.x + start_room.width // 2
    player.y = start_room.y + start_room.height // 2
    
    camera = Camera()
    particles = []
    floating_texts = []
    projectiles = []
    
    inv_btn = Button(SCREEN_WIDTH - 130, 10, 120, 35, "[I] Inventory")
    skill_btn = Button(SCREEN_WIDTH - 130, 50, 120, 35, "[P] Skills")
    
    # Track room completion
    room_enemies = {}  # room_index -> list of enemies in that room
    for enemy in enemies:
        for i, room in enumerate(rooms):
            if room.collidepoint(enemy.x, enemy.y):
                if i not in room_enemies:
                    room_enemies[i] = []
                room_enemies[i].append(enemy)
                break
    
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.05)
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        mouse_world = camera.world_to_screen(*mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state in [INVENTORY, SKILL_TREE]:
                        game_state = PLAYING
                    elif game_state == PLAYING:
                        game_state = MENU
                
                if game_state == PLAYING:
                    if event.key == pygame.K_i:
                        game_state = INVENTORY
                    elif event.key == pygame.K_p:
                        game_state = SKILL_TREE
                    elif event.key == pygame.K_q:
                        player.current_skill = (player.current_skill - 1) % len(player.unlocked_skills)
                    elif event.key == pygame.K_e:
                        player.current_skill = (player.current_skill + 1) % len(player.unlocked_skills)
                    elif event.key == pygame.K_SPACE:
                        skill_name = player.unlocked_skills[player.current_skill]
                        result = player.use_skill(skill_name)
                        if result:
                            if result['type'] == 'aoe':
                                for enemy in enemies:
                                    if enemy.alive:
                                        dist = math.sqrt((enemy.x - player.x)**2 + (enemy.y - player.y)**2)
                                        if dist < result['radius']:
                                            killed, xp = enemy.take_damage(result['damage'])
                                            crit_text = " CRIT!" if result['crit'] else ""
                                            floating_texts.append(FloatingText(
                                                enemy.x, enemy.y-20, f"{result['damage']}{crit_text}",
                                                GOLD if result['crit'] else WHITE,
                                                "large" if result['crit'] else "normal"))
                                            for _ in range(10):
                                                particles.append(Particle(enemy.x, enemy.y, enemy.color,
                                                    (random.uniform(-100,100), random.uniform(-100,100))))
                                            if killed:
                                                if player.gain_xp(xp):
                                                    floating_texts.append(FloatingText(
                                                        player.x, player.y-40, "LEVEL UP!", GOLD, "large"))
                                                if random.random() < 0.5:
                                                    ground_items.append((enemy.x + random.randint(-30,30),
                                                                       enemy.y + random.randint(-30,30),
                                                                       generate_loot(floor)))
                            elif result['type'] == 'projectile':
                                projectiles.append(Projectile(player.x, player.y,
                                    mouse_world[0], mouse_world[1],
                                    result['damage'], result['crit']))
                
                elif game_state == INVENTORY:
                    if event.key == pygame.K_i or event.key == pygame.K_ESCAPE:
                        game_state = PLAYING
                
                elif game_state == SKILL_TREE:
                    if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                        game_state = PLAYING
                
                elif game_state == MENU:
                    if event.key == pygame.K_RETURN:
                        game_state = PLAYING
                
                elif game_state == DEAD:
                    if event.key == pygame.K_RETURN:
                        player = Player(600, 500)
                        floor = 1
                        current_room = 0
                        walls, enemies, ground_items, start_room, doors, rooms = generate_poe2_dungeon(floor)
                        player.x = start_room.x + start_room.width//2
                        player.y = start_room.y + start_room.height//2
                        room_enemies = {}
                        for enemy in enemies:
                            for i, room in enumerate(rooms):
                                if room.collidepoint(enemy.x, enemy.y):
                                    if i not in room_enemies:
                                        room_enemies[i] = []
                                    room_enemies[i].append(enemy)
                                    break
                        particles.clear()
                        floating_texts.clear()
                        projectiles.clear()
                        game_state = PLAYING
        
        keys = pygame.key.get_pressed()
        
        # ===== UPDATE =====
        if game_state == PLAYING:
            player.update(dt, keys, walls)
            camera.update(player.x, player.y)
            
            # Check which room player is in
            for i, room in enumerate(rooms):
                if room.collidepoint(player.x, player.y):
                    current_room = i
                    break
            
            # Check if player walks through unlocked door
            for door in doors:
                if not door.locked and door.rect.collidepoint(player.x, player.y):
                    # Move player to center of connected room
                    if current_room == door.room_from:
                        target_room = rooms[door.room_to]
                    else:
                        target_room = rooms[door.room_from]
                    player.x = target_room.x + target_room.width // 2
                    player.y = target_room.y + target_room.height // 2
                    break
            
            # Check room completion and unlock doors
            for i, room in enumerate(rooms):
                if i not in room_enemies:
                    continue
                # Check if all enemies in this room are dead
                room_alive = [e for e in room_enemies[i] if e.alive]
                if len(room_alive) == 0 and len(room_enemies[i]) > 0:
                    # Room cleared! Unlock doors connected to this room
                    for door in doors:
                        if door.room_from == i or door.room_to == i:
                            if door.locked:
                                door.unlock()
                                floating_texts.append(FloatingText(
                                    door.rect.centerx, door.rect.centery - 20,
                                    "DOOR OPENED!", GREEN, "large"))
                    room_enemies[i] = []  # Mark as processed
            
            # Left click actions
            if mouse_clicked:
                # Check clicking on item
                clicked_item = False
                for item_data in ground_items[:]:
                    ix, iy, item = item_data
                    dist = math.sqrt((mouse_world[0] - ix)**2 + (mouse_world[1] - iy)**2)
                    if dist < 30:
                        player.inventory.append(item)
                        ground_items.remove(item_data)
                        floating_texts.append(FloatingText(ix, iy-10, item.name, item.color))
                        clicked_item = True
                        break
                
                # Attack nearest enemy to click
                if not clicked_item and player.attack_timer <= 0:
                    result = player.basic_attack()
                    if result:
                        dmg, crit = result
                        closest_enemy = None
                        closest_dist = 60
                        for enemy in enemies:
                            if enemy.alive:
                                dist = math.sqrt((enemy.x - mouse_world[0])**2 + (enemy.y - mouse_world[1])**2)
                                if dist < closest_dist:
                                    closest_dist = dist
                                    closest_enemy = enemy
                        
                        if closest_enemy:
                            killed, xp = closest_enemy.take_damage(dmg)
                            crit_text = " CRIT!" if crit else ""
                            floating_texts.append(FloatingText(closest_enemy.x, closest_enemy.y-20,
                                f"{dmg}{crit_text}", GOLD if crit else WHITE, "large" if crit else "normal"))
                            for _ in range(5):
                                particles.append(Particle(closest_enemy.x, closest_enemy.y, WHITE,
                                    (random.uniform(-80,80), random.uniform(-80,80))))
                            if killed:
                                for _ in range(15):
                                    particles.append(Particle(closest_enemy.x, closest_enemy.y, closest_enemy.color,
                                        (random.uniform(-150,150), random.uniform(-150,150))))
                                if player.gain_xp(xp):
                                    floating_texts.append(FloatingText(player.x, player.y-40, "LEVEL UP!", GOLD, "large"))
                                if random.random() < 0.5:
                                    ground_items.append((closest_enemy.x + random.randint(-30,30),
                                                       closest_enemy.y + random.randint(-30,30),
                                                       generate_loot(floor)))
            
            # Update enemies
            for enemy in enemies:
                damage = enemy.update(dt, player, walls)
                if damage:
                    actual = player.take_damage(damage)
                    floating_texts.append(FloatingText(player.x, player.y-30, str(actual), RED))
                    for _ in range(3):
                        particles.append(Particle(player.x, player.y, RED,
                            (random.uniform(-50,50), random.uniform(-50,50))))
                    if not player.alive:
                        game_state = DEAD
            
            # Update projectiles
            for proj in projectiles[:]:
                if not proj.update(dt):
                    projectiles.remove(proj)
                    continue
                for enemy in enemies:
                    if enemy.alive:
                        dist = math.sqrt((proj.x - enemy.x)**2 + (proj.y - enemy.y)**2)
                        if dist < enemy.size + proj.radius:
                            killed, xp = enemy.take_damage(proj.damage)
                            crit_text = " CRIT!" if proj.is_crit else ""
                            floating_texts.append(FloatingText(enemy.x, enemy.y-20,
                                f"{proj.damage}{crit_text}", GOLD if proj.is_crit else WHITE))
                            for _ in range(8):
                                particles.append(Particle(enemy.x, enemy.y, enemy.color,
                                    (random.uniform(-120,120), random.uniform(-120,120))))
                            if killed:
                                if player.gain_xp(xp):
                                    floating_texts.append(FloatingText(player.x, player.y-40, "LEVEL UP!", GOLD, "large"))
                                if random.random() < 0.5:
                                    ground_items.append((enemy.x + random.randint(-30,30),
                                                       enemy.y + random.randint(-30,30),
                                                       generate_loot(floor)))
                            projectiles.remove(proj)
                            break
            
            # Check if ALL rooms cleared -> next floor
            all_cleared = True
            for i in range(len(rooms)):
                if i in room_enemies and len(room_enemies[i]) > 0:
                    if any(e.alive for e in room_enemies[i]):
                        all_cleared = False
                        break
            
            if all_cleared and len(rooms) > 0:
                floor += 1
                current_room = 0
                walls, enemies, ground_items, start_room, doors, rooms = generate_poe2_dungeon(floor)
                player.x = start_room.x + start_room.width // 2
                player.y = start_room.y + start_room.height // 2
                player.hp = min(player.max_hp, player.hp + int(player.max_hp * 0.3))
                player.mana = player.max_mana
                
                room_enemies = {}
                for enemy in enemies:
                    for i, room in enumerate(rooms):
                        if room.collidepoint(enemy.x, enemy.y):
                            if i not in room_enemies:
                                room_enemies[i] = []
                            room_enemies[i].append(enemy)
                            break
                
                floating_texts.append(FloatingText(player.x, player.y-50, f"Floor {floor}!", CYAN, "large"))
            
            particles = [p for p in particles if p.update(dt)]
            floating_texts = [ft for ft in floating_texts if ft.update(dt)]
        
        # Button clicks
        if mouse_clicked:
            if inv_btn.clicked(mouse_pos):
                game_state = INVENTORY if game_state == PLAYING else (PLAYING if game_state == INVENTORY else game_state)
            elif skill_btn.clicked(mouse_pos):
                game_state = SKILL_TREE if game_state == PLAYING else (PLAYING if game_state == SKILL_TREE else game_state)
        
        # ===== RENDER =====
        screen.fill(BLACK)
        
        if game_state == MENU:
            screen.fill(DARK_GRAY)
            title = font_huge.render("PATH OF THE EXILE", True, GOLD)
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 200))
            subtitle = font_large.render("An ARPG Adventure", True, WHITE)
            screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 280))
            start_text = font_medium.render("Press ENTER to begin...", True, LIGHT_GRAY)
            screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, 400))
            controls = font_small.render("WASD: Move | Click: Attack/Pickup | Q/E: Switch Skill | SPACE: Use Skill | I: Inventory | P: Skills", True, GRAY)
            screen.blit(controls, (SCREEN_WIDTH//2 - controls.get_width()//2, 480))
        
        elif game_state in [PLAYING, INVENTORY, SKILL_TREE]:
            # Background
            bg_surf = pygame.Surface((3000, 3000))
            bg_surf.fill((25, 25, 30))
            screen.blit(bg_surf, camera.apply(pygame.Rect(0, 0, 3000, 3000)))
            
            # Draw room floors
            for room in rooms:
                room_pos = camera.apply(room)
                pygame.draw.rect(screen, (35, 35, 40), room_pos)
                pygame.draw.rect(screen, (50, 50, 55), room_pos, 2)
            
            # Walls
            for wall in walls:
                pos = camera.apply(wall)
                if -50 < pos.x < SCREEN_WIDTH + 50 and -50 < pos.y < SCREEN_HEIGHT + 50:
                    pygame.draw.rect(screen, DARK_BROWN, pos)
                    pygame.draw.rect(screen, BROWN, pos, 2)
            
            # Doors
            for door in doors:
                door.draw(screen, camera)
            
            # Ground items
            for ix, iy, item in ground_items:
                pos = camera.apply_point(ix, iy)
                if -20 < pos[0] < SCREEN_WIDTH + 20:
                    glow = 10 + int(math.sin(pygame.time.get_ticks() * 0.003) * 3)
                    pygame.draw.circle(screen, (*item.color, 100), (int(pos[0]), int(pos[1])), glow)
                    pygame.draw.circle(screen, item.color, (int(pos[0]), int(pos[1])), 6)
                    name_text = font_tiny.render(item.name, True, item.color)
                    screen.blit(name_text, (pos[0] - name_text.get_width()//2, pos[1] - 15))
            
            # Enemies
            for enemy in enemies:
                enemy.draw(screen, camera)
            
            # Projectiles
            for proj in projectiles:
                proj.draw(screen, camera)
            
            # Particles
            for p in particles:
                p.draw(screen, camera)
            
            # Floating texts
            for ft in floating_texts:
                ft.draw(screen, camera, font_small, font_large)
            
            # Player
            player.draw(screen, camera)
            
            # HUD
            hp_pct = player.hp / player.max_hp
            pygame.draw.rect(screen, DARK_GRAY, (20, SCREEN_HEIGHT-70, 300, 28), border_radius=5)
            pygame.draw.rect(screen, DARK_RED, (20, SCREEN_HEIGHT-70, 300, 28), border_radius=5)
            pygame.draw.rect(screen, RED, (20, SCREEN_HEIGHT-70, int(300*hp_pct), 28), border_radius=5)
            pygame.draw.rect(screen, WHITE, (20, SCREEN_HEIGHT-70, 300, 28), 2, border_radius=5)
            hp_text = font_small.render(f"HP: {int(player.hp)}/{player.max_hp}", True, WHITE)
            screen.blit(hp_text, (30, SCREEN_HEIGHT-66))
            
            mana_pct = player.mana / player.max_mana
            pygame.draw.rect(screen, DARK_GRAY, (20, SCREEN_HEIGHT-38, 300, 20), border_radius=5)
            pygame.draw.rect(screen, DARK_GREEN, (20, SCREEN_HEIGHT-38, 300, 20), border_radius=5)
            pygame.draw.rect(screen, BLUE, (20, SCREEN_HEIGHT-38, int(300*mana_pct), 20), border_radius=5)
            pygame.draw.rect(screen, WHITE, (20, SCREEN_HEIGHT-38, 300, 20), 2, border_radius=5)
            mana_text = font_small.render(f"Mana: {int(player.mana)}/{player.max_mana}", True, WHITE)
            screen.blit(mana_text, (30, SCREEN_HEIGHT-35))
            
            xp_pct = player.xp / player.xp_to_level
            pygame.draw.rect(screen, DARK_GRAY, (SCREEN_WIDTH//2-150, SCREEN_HEIGHT-20, 300, 12))
            pygame.draw.rect(screen, PURPLE, (SCREEN_WIDTH//2-150, SCREEN_HEIGHT-20, int(300*xp_pct), 12))
            xp_text = font_tiny.render(f"Level {player.level} - XP: {player.xp}/{player.xp_to_level}", True, WHITE)
            screen.blit(xp_text, (SCREEN_WIDTH//2 - xp_text.get_width()//2, SCREEN_HEIGHT-32))
            
            skill_name = player.unlocked_skills[player.current_skill]
            skill_text = font_small.render(f"Skill: {skill_name} (Q/E switch, SPACE use)", True, GOLD)
            screen.blit(skill_text, (SCREEN_WIDTH//2 - skill_text.get_width()//2, SCREEN_HEIGHT-50))
            
            inv_btn.draw(screen, font_small, mouse_pos)
            skill_btn.draw(screen, font_small, mouse_pos)
            
            floor_text = font_large.render(f"Floor {floor} | Room {current_room + 1}/{len(rooms)}", True, WHITE)
            screen.blit(floor_text, (20, 20))
            enemy_text = font_small.render(f"Enemies: {sum(1 for e in enemies if e.alive)}", True, RED)
            screen.blit(enemy_text, (20, 60))
            
            # Room cleared indicator
            for i, room in enumerate(rooms):
                if i in room_enemies and len(room_enemies[i]) == 0:
                    pos = camera.apply_point(room.x + room.width//2, room.y - 20)
                    cleared = font_small.render("CLEARED", True, GREEN)
                    screen.blit(cleared, (pos[0] - cleared.get_width()//2, pos[1]))
            
            # ===== INVENTORY OVERLAY =====
            if game_state == INVENTORY:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.set_alpha(200)
                overlay.fill(BLACK)
                screen.blit(overlay, (0, 0))
                
                px = SCREEN_WIDTH//2 - 300
                py = 50
                pygame.draw.rect(screen, DARK_GRAY, (px, py, 600, SCREEN_HEIGHT-100), border_radius=10)
                pygame.draw.rect(screen, GOLD, (px, py, 600, SCREEN_HEIGHT-100), 3, border_radius=10)
                
                title = font_large.render("INVENTORY (I to close)", True, GOLD)
                screen.blit(title, (px + 20, py + 15))
                
                eqx = px + 20
                eqy = py + 60
                for i, (slot, item) in enumerate(player.equipment.items()):
                    sy = eqy + i * 35
                    slot_text = font_small.render(f"{slot.title()}:", True, LIGHT_GRAY)
                    screen.blit(slot_text, (eqx, sy))
                    if item:
                        item_text = font_small.render(f"{item.name} ({item.rarity})", True, item.color)
                        screen.blit(item_text, (eqx + 100, sy))
                    else:
                        screen.blit(font_small.render("Empty", True, GRAY), (eqx + 100, sy))
                
                inv_title = font_medium.render("Backpack:", True, WHITE)
                screen.blit(inv_title, (eqx + 320, eqy))
                
                for i, item in enumerate(player.inventory[:10]):
                    iy = eqy + 30 + i * 30
                    item_text = font_small.render(f"{item.name} ({item.rarity})", True, item.color)
                    screen.blit(item_text, (eqx + 320, iy))
                    
                    equip_btn = pygame.Rect(eqx + 500, iy, 50, 22)
                    pygame.draw.rect(screen, GREEN, equip_btn, border_radius=3)
                    btn_text = font_tiny.render("Equip", True, BLACK)
                    screen.blit(btn_text, (eqx + 505, iy + 4))
                    
                    if mouse_clicked and equip_btn.collidepoint(mouse_pos):
                        if item.item_type in player.equipment:
                            player.equip_item(item)
                            player.inventory.remove(item)
                            mouse_clicked = False
            
            # ===== SKILL TREE OVERLAY =====
            if game_state == SKILL_TREE:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.set_alpha(200)
                overlay.fill(BLACK)
                screen.blit(overlay, (0, 0))
                
                title = font_large.render(f"PASSIVE SKILLS - Points: {player.skill_points} (P to close)", True, GOLD)
                screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 30))
                
                nodes = [
                    ("Vitality", f"+20 Max HP", SCREEN_WIDTH//2 - 100, 150),
                    ("Might", f"+5 Damage", SCREEN_WIDTH//2 - 100, 220),
                    ("Toughness", f"+10 Armor", SCREEN_WIDTH//2 - 100, 290),
                    ("Swiftness", f"+5% Speed", SCREEN_WIDTH//2 - 100, 360),
                    ("Precision", f"+3% Crit", SCREEN_WIDTH//2 - 100, 430),
                ]
                
                for name, desc, nx, ny in nodes:
                    node_rect = pygame.Rect(nx, ny, 200, 50)
                    color = GREEN if player.skill_points > 0 else DARK_GRAY
                    pygame.draw.rect(screen, color, node_rect, border_radius=8)
                    pygame.draw.rect(screen, WHITE, node_rect, 2, border_radius=8)
                    name_text = font_medium.render(name, True, WHITE)
                    screen.blit(name_text, (nx + 10, ny + 5))
                    desc_text = font_tiny.render(desc, True, LIGHT_GRAY)
                    screen.blit(desc_text, (nx + 10, ny + 28))
                    
                    if mouse_clicked and node_rect.collidepoint(mouse_pos) and player.skill_points > 0:
                        if name == "Vitality": player.max_hp += 20
                        elif name == "Might": player.base_damage += 5
                        elif name == "Toughness": player.armor += 10
                        elif name == "Swiftness": player.speed += int(player.speed * 0.05)
                        elif name == "Precision": player.crit_chance += 3
                        player.skill_points -= 1
                        player.recalculate_stats()
                        mouse_clicked = False
        
        elif game_state == DEAD:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(RED)
            screen.blit(overlay, (0, 0))
            death_text = font_huge.render("YOU HAVE DIED", True, RED)
            screen.blit(death_text, (SCREEN_WIDTH//2 - death_text.get_width()//2, SCREEN_HEIGHT//2 - 60))
            info_text = font_medium.render(f"Reached Floor {floor} - Level {player.level}", True, WHITE)
            screen.blit(info_text, (SCREEN_WIDTH//2 - info_text.get_width()//2, SCREEN_HEIGHT//2))
            respawn_text = font_large.render("Press ENTER to Respawn", True, WHITE)
            screen.blit(respawn_text, (SCREEN_WIDTH//2 - respawn_text.get_width()//2, SCREEN_HEIGHT//2 + 60))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()