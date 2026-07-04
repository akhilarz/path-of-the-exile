"""
Enemy system - types, AI, combat
"""
import pygame
from settings import *

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
        if not self.alive:
            return None
        
        self.attack_timer -= dt
        
        dx = player.rect.centerx - self.x
        dy = player.rect.centery - self.y
        dist = (dx**2 + dy**2) ** 0.5
        
        if 30 < dist < 500:
            if dist > 0:
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
        if not self.alive:
            return
        
        screen_pos = camera.apply_point(self.x, self.y)
        x, y = int(screen_pos[0]), int(screen_pos[1])
        
        pygame.draw.circle(screen, BLACK, (x, y+2), self.size)
        pygame.draw.circle(screen, self.color, (x, y), self.size)
        pygame.draw.circle(screen, WHITE, (x, y), self.size, 2)
        
        eye_offset = self.size // 3
        pygame.draw.circle(screen, RED, (x - eye_offset, y - eye_offset), 3)
        pygame.draw.circle(screen, RED, (x + eye_offset, y - eye_offset), 3)
        
        bar_width = self.size * 2
        bar_height = 4
        bar_x = x - bar_width // 2
        bar_y = y - self.size - 10
        
        hp_percent = self.hp / self.max_hp
        pygame.draw.rect(screen, DARK_RED, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, int(bar_width * hp_percent), bar_height))