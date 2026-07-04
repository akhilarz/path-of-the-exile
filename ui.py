"""
UI system - HUD, inventory, skill tree, buttons
"""
import pygame
from settings import *

class Button:
    def __init__(self, x, y, width, height, text, color=DARK_GRAY, hover_color=GRAY):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
    
    def draw(self, screen, mouse_pos):
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=5)
        text_surf = FONT_SMALL.render(self.text, True, WHITE)
        screen.blit(text_surf, (self.rect.x + 10, self.rect.y + 8))
    
    def clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

def draw_hud(screen, player, skill_name):
    """Draw health, mana, XP bars and skill info"""
    # Health bar
    hp_percent = player.hp / player.max_hp
    pygame.draw.rect(screen, DARK_GRAY, (20, SCREEN_HEIGHT - 70, 300, 28), border_radius=5)
    pygame.draw.rect(screen, DARK_RED, (20, SCREEN_HEIGHT - 70, 300, 28), border_radius=5)
    pygame.draw.rect(screen, RED, (20, SCREEN_HEIGHT - 70, int(300 * hp_percent), 28), border_radius=5)
    pygame.draw.rect(screen, WHITE, (20, SCREEN_HEIGHT - 70, 300, 28), 2, border_radius=5)
    hp_text = FONT_SMALL.render(f"HP: {int(player.hp)}/{player.max_hp}", True, WHITE)
    screen.blit(hp_text, (30, SCREEN_HEIGHT - 66))
    
    # Mana bar
    mana_percent = player.mana / player.max_mana
    pygame.draw.rect(screen, DARK_GRAY, (20, SCREEN_HEIGHT - 38, 300, 20), border_radius=5)
    pygame.draw.rect(screen, DARK_GREEN, (20, SCREEN_HEIGHT - 38, 300, 20), border_radius=5)
    pygame.draw.rect(screen, BLUE, (20, SCREEN_HEIGHT - 38, int(300 * mana_percent), 20), border_radius=5)
    pygame.draw.rect(screen, WHITE, (20, SCREEN_HEIGHT - 38, 300, 20), 2, border_radius=5)
    mana_text = FONT_SMALL.render(f"Mana: {int(player.mana)}/{player.max_mana}", True, WHITE)
    screen.blit(mana_text, (30, SCREEN_HEIGHT - 35))
    
    # XP bar
    xp_percent = player.xp / player.xp_to_level
    pygame.draw.rect(screen, DARK_GRAY, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT - 20, 300, 12))
    pygame.draw.rect(screen, PURPLE, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT - 20, int(300 * xp_percent), 12))
    xp_text = FONT_TINY.render(f"Level {player.level} - XP: {player.xp}/{player.xp_to_level}", True, WHITE)
    screen.blit(xp_text, (SCREEN_WIDTH//2 - xp_text.get_width()//2, SCREEN_HEIGHT - 32))
    
    # Current skill
    skill_text = FONT_SMALL.render(f"Skill: {skill_name} (Q/E switch, SPACE use)", True, GOLD)
    screen.blit(skill_text, (SCREEN_WIDTH//2 - skill_text.get_width()//2, SCREEN_HEIGHT - 50))

def draw_minimap(screen, player, enemies, walls):
    """Draw minimap in bottom-right corner"""
    minimap_size = 150
    mx = SCREEN_WIDTH - minimap_size - 20
    my = SCREEN_HEIGHT - minimap_size - 80
    
    pygame.draw.rect(screen, DARK_GRAY, (mx, my, minimap_size, minimap_size))
    pygame.draw.rect(screen, WHITE, (mx, my, minimap_size, minimap_size), 2)
    
    scale = minimap_size / DUNGEON_WIDTH
    
    for wall in walls:
        wx = mx + wall.x * scale
        wy = my + wall.y * scale
        pygame.draw.rect(screen, BROWN, (wx, wy, max(1, wall.width*scale), max(1, wall.height*scale)))
    
    px = mx + player.x * scale
    py = my + player.y * scale
    pygame.draw.circle(screen, BLUE, (int(px), int(py)), 3)
    
    for enemy in enemies:
        if enemy.alive:
            ex = mx + enemy.x * scale
            ey = my + enemy.y * scale
            pygame.draw.circle(screen, RED, (int(ex), int(ey)), 2)

def draw_inventory(screen, player, mouse_pos, mouse_clicked):
    """Draw inventory overlay"""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    panel_x = SCREEN_WIDTH//2 - 300
    panel_y = 50
    pygame.draw.rect(screen, DARK_GRAY, (panel_x, panel_y, 600, SCREEN_HEIGHT-100), border_radius=10)
    pygame.draw.rect(screen, GOLD, (panel_x, panel_y, 600, SCREEN_HEIGHT-100), 3, border_radius=10)
    
    title = FONT_LARGE.render("INVENTORY", True, GOLD)
    screen.blit(title, (panel_x + 20, panel_y + 15))
    
    eq_x = panel_x + 20
    eq_y = panel_y + 60
    
    for i, (slot, item) in enumerate(player.equipment.items()):
        sy = eq_y + i * 35
        slot_text = FONT_SMALL.render(f"{slot.title()}:", True, LIGHT_GRAY)
        screen.blit(slot_text, (eq_x, sy))
        
        if item:
            item_text = FONT_SMALL.render(f"{item.name} ({item.rarity})", True, item.color)
            screen.blit(item_text, (eq_x + 100, sy))
        else:
            empty_text = FONT_SMALL.render("Empty", True, GRAY)
            screen.blit(empty_text, (eq_x + 100, sy))
    
    inv_title = FONT_MEDIUM.render("Backpack:", True, WHITE)
    screen.blit(inv_title, (eq_x + 320, eq_y))
    
    for i, item in enumerate(player.inventory[:10]):
        iy = eq_y + 30 + i * 30
        item_text = FONT_SMALL.render(f"{item.name} ({item.rarity})", True, item.color)
        screen.blit(item_text, (eq_x + 320, iy))
        
        equip_btn = pygame.Rect(eq_x + 500, iy, 50, 22)
        pygame.draw.rect(screen, GREEN, equip_btn, border_radius=3)
        btn_text = FONT_TINY.render("Equip", True, BLACK)
        screen.blit(btn_text, (eq_x + 505, iy + 4))
        
        if mouse_clicked and equip_btn.collidepoint(mouse_pos):
            if item.item_type in player.equipment:
                player.equip_item(item)
                player.inventory.remove(item)
                return True
    return False

def draw_skill_tree(screen, player, mouse_pos, mouse_clicked):
    """Draw passive skill tree overlay"""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    title = FONT_LARGE.render(f"PASSIVE SKILLS - Points: {player.skill_points}", True, GOLD)
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
        
        name_text = FONT_MEDIUM.render(name, True, WHITE)
        screen.blit(name_text, (nx + 10, ny + 5))
        desc_text = FONT_TINY.render(desc, True, LIGHT_GRAY)
        screen.blit(desc_text, (nx + 10, ny + 28))
        
        if mouse_clicked and node_rect.collidepoint(mouse_pos) and player.skill_points > 0:
            if name == "Vitality": player.max_hp += 20
            elif name == "Might": player.base_damage += 5
            elif name == "Toughness": player.armor += 10
            elif name == "Swiftness": player.speed += int(player.speed * 0.05)
            elif name == "Precision": player.crit_chance += 3
            player.skill_points -= 1
            player.recalculate_stats()
            return True
    return False

def draw_death_screen(screen, floor, level):
    """Draw death screen"""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill(RED)
    screen.blit(overlay, (0, 0))
    
    death_text = FONT_HUGE.render("YOU HAVE DIED", True, RED)
    screen.blit(death_text, (SCREEN_WIDTH//2 - death_text.get_width()//2, SCREEN_HEIGHT//2 - 60))
    
    info_text = FONT_MEDIUM.render(f"Reached Floor {floor} - Level {level}", True, WHITE)
    screen.blit(info_text, (SCREEN_WIDTH//2 - info_text.get_width()//2, SCREEN_HEIGHT//2))
    
    respawn_text = FONT_LARGE.render("Press ENTER to Respawn", True, WHITE)
    screen.blit(respawn_text, (SCREEN_WIDTH//2 - respawn_text.get_width()//2, SCREEN_HEIGHT//2 + 60))