"""
Camera system for smooth scrolling
"""
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
    
    def apply(self, rect):
        """Convert world coordinates to screen coordinates"""
        return pygame.Rect(rect.x - self.x, rect.y - self.y, rect.width, rect.height)
    
    def apply_point(self, x, y):
        """Convert a point from world to screen"""
        return (x - self.x, y - self.y)
    
    def update(self, target_x, target_y):
        """Smoothly follow target"""
        target_cam_x = target_x - SCREEN_WIDTH // 2
        target_cam_y = target_y - SCREEN_HEIGHT // 2
        
        self.x += (target_cam_x - self.x) * 0.1
        self.y += (target_cam_y - self.y) * 0.1
    
    def world_to_screen(self, screen_x, screen_y):
        """Convert screen coordinates to world coordinates"""
        return (screen_x + self.x, screen_y + self.y)