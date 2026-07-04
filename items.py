"""
Item system - generation, stats, loot tables
"""
import random
from settings import BLUE, YELLOW, ORANGE, WHITE

class Item:
    def __init__(self, name, item_type, rarity="Normal", damage=0, armor=0, 
                 health=0, speed=0, crit=0, value=0):
        self.name = name
        self.item_type = item_type
        self.rarity = rarity
        self.damage = damage
        self.armor = armor
        self.health = health
        self.speed = speed
        self.crit = crit
        self.value = value
    
    @property
    def color(self):
        colors = {"Magic": BLUE, "Rare": YELLOW, "Unique": ORANGE}
        return colors.get(self.rarity, WHITE)
    
    def get_description(self):
        desc = f"{self.name} ({self.rarity})"
        stats = []
        if self.damage: stats.append(f"+{self.damage} Damage")
        if self.armor: stats.append(f"+{self.armor} Armor")
        if self.health: stats.append(f"+{self.health} HP")
        if self.speed: stats.append(f"+{self.speed}% Speed")
        if self.crit: stats.append(f"+{self.crit}% Crit")
        return desc, stats

def generate_loot(level):
    """Generate random loot based on level"""
    roll = random.random()
    
    if roll < 0.45:
        rarity = "Normal"
    elif roll < 0.80:
        rarity = "Magic"
    elif roll < 0.96:
        rarity = "Rare"
    else:
        rarity = "Unique"
    
    item_type = random.choice(['weapon', 'armor', 'helmet', 'boots', 'ring'])
    
    if item_type == 'weapon':
        names = ["Rusty Sword", "Iron Blade", "Steel Sword", "War Axe", "Shadow Dagger"]
        dmg = random.randint(3, 8) + level * 2
        if rarity == "Rare": dmg = int(dmg * 2)
        if rarity == "Unique": dmg = int(dmg * 3)
        return Item(random.choice(names), 'weapon', rarity, damage=dmg, value=level*10)
    
    elif item_type == 'armor':
        names = ["Leather Armor", "Chainmail", "Iron Plate", "Dragon Scale"]
        arm = random.randint(5, 15) + level * 3
        hp = random.randint(10, 30) + level * 5
        if rarity == "Rare": arm = int(arm * 2); hp = int(hp * 2)
        if rarity == "Unique": arm = int(arm * 3); hp = int(hp * 3)
        return Item(random.choice(names), 'armor', rarity, armor=arm, health=hp, value=level*10)
    
    elif item_type == 'helmet':
        names = ["Leather Cap", "Iron Helm", "Steel Crown", "War Helm"]
        arm = random.randint(3, 10) + level * 2
        hp = random.randint(5, 20) + level * 3
        return Item(random.choice(names), 'helmet', rarity, armor=arm, health=hp, value=level*10)
    
    elif item_type == 'boots':
        names = ["Leather Boots", "Iron Greaves", "Wind Walkers", "Shadow Steps"]
        spd = random.randint(5, 20) + level * 2
        return Item(random.choice(names), 'boots', rarity, speed=spd, value=level*10)
    
    else:
        names = ["Bone Ring", "Silver Band", "Ruby Ring", "Diamond Circle"]
        crit = random.randint(2, 10) + level
        dmg = random.randint(2, 6) + level
        return Item(random.choice(names), 'ring', rarity, damage=dmg, crit=crit, value=level*10)