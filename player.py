"""
Player character - movement, combat, stats, equipment
"""
import random
import pygame
from settings import *
from items import Item

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x - PLAYER_SIZE, y - PLAYER_SIZE, PLAYER_SIZE*2, PLAYER_SIZE*2)
        self.speed = PLAYER_SPEED
        self.vx = 0
        self.vy = 0
        
        # Stats
        self.level = 1
        self.xp = 0
        self.xp_to_level = 100
        self.max_hp = PLAYER_MAX_HP
        self.hp = PLAYER_MAX_HP
        self.max_mana = PLAYER_MAX_MANA
        self.mana = PLAYER_MAX_MANA
        self.base_damage = PLAYER_BASE_DAMAGE
        self.armor = PLAYER_BASE_ARMOR
        self.crit_chance = PLAYER_BASE_CRIT
        self.attack_speed = 1.0
        self.skill_points = 0
        
        # Equipment
        self.equipment = {
            'weapon': Item("Rusty Sword", 'weapon', 'Normal', damage=5),
            'armor': None,
            'helmet': None,
            'boots': None,
            'ring': None,
        }
        self.inventory = []
        
        # Combat
        self.attack_timer = 0
        self.skill_cooldowns = {}
        self.alive = True
        
        # Skills
        self.unlocked_skills = ['cleave', 'heavy_strike', 'fireball']
        self.current_skill = 0
        
        self.recalculate_stats()
    
    def recalculate_stats(self):
        self.max_hp = PLAYER_MAX_HP + self.level * 20
        self.max_mana = PLAYER_MAX_MANA + self.level * 10
        self.base_damage = PLAYER_BASE_DAMAGE + self.level * 3
        self.armor = PLAYER_BASE_ARMOR
        self.crit_chance = PLAYER_BASE_CRIT
        self.speed = PLAYER_SPEED
        
        for item in self.equipment.values():
            if item:
                self.base_damage += item.damage
                self.armor += item.armor
                self.max_hp += item.health
                self.crit_chance += item.crit
                if item.speed:
                    self.speed = PLAYER_SPEED * (1 + item.speed / 100)
        
        self.hp = min(self.hp, self.max_hp)
        self.mana = min(self.mana, self.max_mana)
    
    def equip_item(self, item):
        old = self.equipment.get(item.item_type)
        if old:
            self.inventory.append(old)
        self.equipment[item.item_type] = item
        self.recalculate_stats()
    
    def get_damage(self, skill_mult=1.0):
        dmg = self.base_damage * skill_mult
        is_crit = random.random() * 100 < self.crit_chance
        if is_crit:
            dmg *= 1.8
        return random.randint(int(dmg * 0.85), int(dmg * 1.15)), is_crit
    
    def take_damage(self, damage):
        reduction = self.armor / (self.armor + 60)
        actual = max(1, int(damage * (1 - reduction)))
        self.hp -= actual
        if self.hp <= 0:
            self.alive = False
        return actual
    
    def basic_attack(self):
        if self.attack_timer > 0:
            return None
        self.attack_timer = 0.5 / self.attack_speed
        return self.get_damage()
    
    def use_skill(self, skill_name):
        if skill_name not in SKILLS:
            return None
        skill = SKILLS[skill_name]
        if skill_name in self.skill_cooldowns:
            return None
        if self.mana < skill['mana']:
            return None
        
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
        if leveled:
            self.recalculate_stats()
        return leveled
    
    def update(self, dt, keys, walls):
        if not self.alive:
            return
        
        self.vx = 0
        self.vy = 0
        
        if keys[pygame.K_w] or keys[pygame.K_UP]: self.vy = -self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: self.vy = self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: self.vx = -self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.vx = self.speed
        
        if self.vx != 0 and self.vy != 0:
            self.vx *= 0.707
            self.vy *= 0.707
        
        new_x = self.x + self.vx * dt
        new_y = self.y + self.vy * dt
        
        test_rect = pygame.Rect(new_x - PLAYER_SIZE, self.y - PLAYER_SIZE, PLAYER_SIZE*2, PLAYER_SIZE*2)
        if not any(test_rect.colliderect(w) for w in walls):
            self.x = new_x
        
        test_rect = pygame.Rect(self.x - PLAYER_SIZE, new_y - PLAYER_SIZE, PLAYER_SIZE*2, PLAYER_SIZE*2)
        if not any(test_rect.colliderect(w) for w in walls):
            self.y = new_y
        
        self.rect.x = self.x - PLAYER_SIZE
        self.rect.y = self.y - PLAYER_SIZE
        
        self.mana = min(self.max_mana, self.mana + 8 * dt)
        self.attack_timer = max(0, self.attack_timer - dt)
        
        for skill in list(self.skill_cooldowns.keys()):
            self.skill_cooldowns[skill] -= dt
            if self.skill_cooldowns[skill] <= 0:
                del self.skill_cooldowns[skill]
    
    def draw(self, screen, camera):
        if not self.alive:
            return
        
        screen_pos = camera.apply_point(self.x, self.y)
        x, y = int(screen_pos[0]), int(screen_pos[1])
        
        pygame.draw.ellipse(screen, BLACK, (x-14, y+12, 28, 10))
        pygame.draw.circle(screen, (60, 100, 220), (x, y), PLAYER_SIZE)
        pygame.draw.circle(screen, WHITE, (x, y), PLAYER_SIZE, 2)
        pygame.draw.circle(screen, WHITE, (x-5, y-3), 4)
        pygame.draw.circle(screen, WHITE, (x+5, y-3), 4)
        pygame.draw.circle(screen, BLACK, (x-5, y-3), 2)
        pygame.draw.circle(screen, BLACK, (x+5, y-3), 2)