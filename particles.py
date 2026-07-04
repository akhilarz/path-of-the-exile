"""
Particle and floating text effects
"""
import random
import pygame
from settings import *

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
        screen_pos = camera.apply_point(self.x, self.y)
        size = int(self.size * alpha)
        if size > 0:
            pygame.draw.circle(screen, self.color, (int(screen_pos[0]), int(screen_pos[1])), size)

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
    
    def draw(self, screen, camera):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        font = FONT_LARGE if self.size == "large" else FONT_SMALL
        text_surface = font.render(self.text, True, self.color)
        text_surface.set_alpha(alpha)
        screen_pos = camera.apply_point(self.x, self.y)
        screen.blit(text_surface, (screen_pos[0] - text_surface.get_width()//2, screen_pos[1]))

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
        dist = (dx**2 + dy**2) ** 0.5
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
        screen_pos = camera.apply_point(self.x, self.y)
        color = GOLD if self.is_crit else YELLOW
        pygame.draw.circle(screen, color, (int(screen_pos[0]), int(screen_pos[1])), self.radius)
        trail_color = ORANGE if self.is_crit else color
        pygame.draw.circle(screen, trail_color, 
                          (int(screen_pos[0] - self.vx*0.02), int(screen_pos[1] - self.vy*0.02)), 
                          self.radius-2)