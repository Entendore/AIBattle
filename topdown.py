import sys
import math
import random
import heapq
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QSlider, QLabel, QGraphicsView, 
                               QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, 
                               QCheckBox, QGraphicsLineItem, QProgressBar)
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF, QLineF
from PySide6.QtGui import QBrush, QColor, QPen, QFont

# --- Configuration ---
SCENE_WIDTH = 800
SCENE_HEIGHT = 600
TILE_SIZE = 40
GRID_W = SCENE_WIDTH // TILE_SIZE
GRID_H = SCENE_HEIGHT // TILE_SIZE
ATTACK_COOLDOWN = 800 # milliseconds

# --- Constants for AI logic ---
RANGED_KITERS = {"archer", "mage", "necromancer", "druid", "vampire", "tinkerer", "alchemist"}
SQUISHY_TYPES = RANGED_KITERS | {"healer", "commander"}
PROTECTOR_TYPES = {"tank", "commander", "paladin"}

# --- Terrain Definitions ---
TERRAIN_TYPES = {
    "grass": {"emojis": ["🌿", "🌼", "🌾"], "walkable": True, "speed_mod": 1.0, "defense_mod": 0.0, "bg_color": QColor(34, 139, 34, 150), "hp": 0},
    "road": {"emojis": ["🟫", "🟧"], "walkable": True, "speed_mod": 1.5, "defense_mod": 0.0, "bg_color": QColor(139, 69, 19, 150), "hp": 0},
    "bush": {"emojis": ["🍃", "🍁"], "walkable": True, "speed_mod": 1.0, "defense_mod": 0.2, "bg_color": QColor(0, 100, 0, 150), "evasion_mod": 0.4, "hp": 20},
    "water": {"emojis": ["🌊", "💧"], "walkable": False, "speed_mod": 0.0, "defense_mod": 0.0, "bg_color": QColor(0, 0, 139, 180), "hp": 0},
    "forest": {"emojis": ["🌳", "🌲"], "walkable": False, "speed_mod": 0.0, "defense_mod": 0.0, "bg_color": QColor(0, 51, 0, 180), "hp": 50},
    "rock": {"emojis": ["🪨", "⛰️"], "walkable": False, "speed_mod": 0.0, "defense_mod": 0.0, "bg_color": QColor(105, 105, 105, 180), "hp": 100},
    "lava": {"emojis": ["🔥", "🌋"], "walkable": True, "speed_mod": 0.8, "defense_mod": 0.0, "bg_color": QColor(178, 34, 34, 180), "dps": 8.0, "hp": 0},
    "high_ground": {"emojis": ["⬆️", "🏔️"], "walkable": True, "speed_mod": 1.0, "defense_mod": 0.2, "bg_color": QColor(210, 180, 140, 150), "range_mod": 1.3, "hp": 0},
    "capture_point": {"emojis": ["🌀", "♻️"], "walkable": True, "speed_mod": 1.0, "defense_mod": 0.0, "bg_color": QColor(128, 0, 128, 150), "energy_mod": 1.5, "hp": 0},
    "ice": {"emojis": ["🧊", "❄️"], "walkable": True, "speed_mod": 1.3, "defense_mod": -0.1, "bg_color": QColor(173, 216, 230, 150), "hp": 0},
    "swamp": {"emojis": ["🦟", "🍄"], "walkable": True, "speed_mod": 0.6, "defense_mod": 0.3, "bg_color": QColor(85, 107, 47, 180), "hp": 0},
    "sanctuary": {"emojis": ["⛲", "🏥"], "walkable": True, "speed_mod": 1.0, "defense_mod": 0.0, "bg_color": QColor(255, 255, 224, 150), "dps": -10.0, "hp": 0}
}

# --- Unit Definitions ---
UNIT_TYPES = {
    "tank": {"emoji_red": "🐉", "emoji_blue": "🦏", "health": 350, "speed": 0.7, "damage": 15, "attack_range": 35, "ranged": False, "ult_cost": 100},
    "warrior": {"emoji_red": "🐺", "emoji_blue": "🐗", "health": 130, "speed": 1.6, "damage": 10, "attack_range": 22, "ranged": False, "ult_cost": 80},
    "archer": {"emoji_red": "🏹", "emoji_blue": "🦅", "health": 75, "speed": 1.2, "damage": 12, "attack_range": 130, "ranged": True, "ult_cost": 90},
    "mage": {"emoji_red": "🔮", "emoji_blue": "🧙‍♀️", "health": 90, "speed": 1.0, "damage": 16, "attack_range": 90, "ranged": True, "ult_cost": 85, "splash": 0.5},
    "assassin": {"emoji_red": "🥷", "emoji_blue": "🕷️", "health": 85, "speed": 2.0, "damage": 25, "attack_range": 25, "ranged": False, "ult_cost": 70, "evasion": 0.2},
    "berserker": {"emoji_red": "🪓", "emoji_blue": "🦍", "health": 180, "speed": 1.3, "damage": 12, "attack_range": 25, "ranged": False, "ult_cost": 75},
    "commander": {"emoji_red": "👑", "emoji_blue": "🚩", "health": 250, "speed": 0.9, "damage": 8, "attack_range": 40, "ranged": True, "ult_cost": 90},
    "necromancer": {"emoji_red": "🧟", "emoji_blue": "💀", "health": 100, "speed": 0.9, "damage": 6, "attack_range": 80, "ranged": True, "ult_cost": 80},
    "paladin": {"emoji_red": "🤴", "emoji_blue": "🦾", "health": 220, "speed": 1.0, "damage": 14, "attack_range": 25, "ranged": False, "ult_cost": 90},
    "druid": {"emoji_red": "🌳", "emoji_blue": "🦉", "health": 130, "speed": 1.1, "damage": 8, "attack_range": 70, "ranged": True, "ult_cost": 80},
    "vampire": {"emoji_red": "🧛‍♂️", "emoji_blue": "🦇", "health": 110, "speed": 1.1, "damage": 14, "attack_range": 80, "ranged": True, "ult_cost": 80, "lifesteal": 0.5},
    "tinkerer": {"emoji_red": "🤖", "emoji_blue": "⚙️", "health": 110, "speed": 1.0, "damage": 8, "attack_range": 80, "ranged": True, "ult_cost": 85},
    "alchemist": {"emoji_red": "⚗️", "emoji_blue": "🧪", "health": 95, "speed": 1.1, "damage": 10, "attack_range": 75, "ranged": True, "ult_cost": 80, "splash": 0.3},
    "healer": {"emoji_red": "🧙", "emoji_blue": "🧝", "health": 85, "speed": 1.4, "damage": -15, "attack_range": 60, "ranged": True, "healer": True, "ult_cost": 70},
    "minion": {"emoji_red": "👻", "emoji_blue": "🦴", "health": 50, "speed": 1.8, "damage": 8, "attack_range": 20, "ranged": False, "is_minion": True},
    "bat": {"emoji_red": "🦇", "emoji_blue": "蝠", "health": 30, "speed": 2.5, "damage": 6, "attack_range": 15, "ranged": False, "is_minion": True},
    "turret": {"emoji_red": "🔫", "emoji_blue": "🎯", "health": 120, "speed": 0.0, "damage": 12, "attack_range": 100, "ranged": True, "is_minion": True},
    "ward": {"emoji_red": "🏥", "emoji_blue": "⛺", "health": 100, "speed": 0.0, "damage": 0, "attack_range": 0, "ranged": False, "is_minion": True},
    "nexus": {"emoji_red": "🏯", "emoji_blue": "🏰", "health": 1500, "speed": 0.0, "damage": 0, "attack_range": 0, "ranged": False, "is_minion": True}
}

ACTION_ICONS = {"ATTACK": "⚔️", "FLEE": "🏃", "CAPTURE": "🚩", "GROUP": "🤝", "HEAL": "✨", "DEFEND": "🛡️", "PEEL": "🛑", "CLEANSE": "🌊", "DANGER": "⚠️", "GATHER": "📦", "IDLE": "💤"}
STATUS_ICONS = {"STUN": "⚡", "POISON": "☠️", "ARMOR_BREAK": "🔻", "BURN": "🔥", "SHIELD": "🛡️", "BEAR": "🐻", "CHARM": "🖤", "OVERCLOCK": "⚙️", "RAGE": "😡", "CRATE": "📦"}

class CustomScene(QGraphicsScene):
    def __init__(self, simulator=None):
        super().__init__()
        self._simulator = simulator
        self.show_debug = False
        self.combat_texts = []
        self.effects = []
        self.hazards = []
        self.crates = []
        self.cp_coords = []
        self.commander_in_danger = False
        self.team_red_routing = False
        self.team_blue_routing = False
        self.team_red_initial_size = 0
        self.team_blue_initial_size = 0
        self.weather = "CLEAR"
        self.weather_timer = 30000
        self.meteor_timer = 0
        self.terrain_health = {}
        self.is_night = False
        self.time_of_day = 0.0
        self.nexus_red = None
        self.nexus_blue = None
        
        self.team_red_ult = 0
        self.team_blue_ult = 0
        self.team_red_ult_active_timer = 0
        self.team_blue_ult_active_timer = 0
        
        self.projectiles = []
        self.terrain = []
        self.team_red = []
        self.team_blue = []

    def add_combat_text(self, x, y, text, color):
        if len(self.combat_texts) > 80: return # Cap text to prevent lag
        txt = CombatText(x, y, text, color)
        txt.setZValue(10)
        self.addItem(txt)
        self.combat_texts.append(txt)

    def add_effect(self, x, y, emoji, lifespan=400, size=16):
        eff = Effect(x, y, emoji, lifespan, size)
        eff.setZValue(6)
        self.addItem(eff)
        self.effects.append(eff)

    def damage_terrain(self, world_x, world_y, amount):
        gx, gy = int(world_x // TILE_SIZE), int(world_y // TILE_SIZE)
        if not (0 <= gx < GRID_W and 0 <= gy < GRID_H):
            return
        if (gx, gy) not in self.terrain_health:
            return
        self.terrain_health[(gx, gy)] -= amount
        if self.terrain_health[(gx, gy)] <= 0:
            old_t = self.terrain[gy][gx]
            if self._simulator is not None:
                self._simulator.set_terrain(gx, gy, "grass")
                debris = {"forest": "🪵", "bush": "🍂", "rock": "🪨"}.get(old_t, "💥")
                self.add_effect(gx * TILE_SIZE + TILE_SIZE/2,
                                gy * TILE_SIZE + TILE_SIZE/2,
                                debris, lifespan=500, size=20)

class DStar:
    """A* Pathfinder with LOS smoothing (replaces broken D* implementation)"""
    def __init__(self, grid_w, grid_h, is_walkable_func):
        self.w = grid_w
        self.h = grid_h
        self.is_walkable = is_walkable_func
        
    def get_neighbors(self, s):
        x, y = s; res = []
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < self.w and 0 <= ny < self.h:
                res.append((nx, ny))
        return res
        
    def _h(self, a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])
        
    def has_los(self, p1, p2):
        x0, y0 = p1; x1, y1 = p2; dx = abs(x1 - x0); dy = abs(y1 - y0)
        x, y = x0, y0; sx = -1 if x0 > x1 else 1; sy = -1 if y0 > y1 else 1
        if dx > dy:
            err = dx / 2.0
            while x != x1:
                if not self.is_walkable(x, y): return False
                err -= dy
                if err < 0:
                    y += sy; err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y1:
                if not self.is_walkable(x, y): return False
                err -= dx
                if err < 0:
                    x += sx; err += dy
                y += sy
        return self.is_walkable(x1, y1) # Check final cell
        
    def smooth_path(self, grid_path):
        if len(grid_path) <= 2: return grid_path
        smoothed = [grid_path[0]]; i = 0
        while i < len(grid_path) - 1:
            j = len(grid_path) - 1
            while j > i + 1:
                if self.has_los(grid_path[i], grid_path[j]): break
                j -= 1
            smoothed.append(grid_path[j]); i = j
        return smoothed
        
    def find_path(self, start_world, goal_world):
        start = (int(start_world[0] // TILE_SIZE), int(start_world[1] // TILE_SIZE))
        goal = (int(goal_world[0] // TILE_SIZE), int(goal_world[1] // TILE_SIZE))
        
        if not self.is_walkable(goal[0], goal[1]) or not self.is_walkable(start[0], start[1]):
            return []
            
        open_heap = [(0, start)]
        came_from = {}; g = {start: 0}
        
        while open_heap:
            _, cur = heapq.heappop(open_heap)
            if cur == goal: break
            for n in self.get_neighbors(cur):
                if not self.is_walkable(n[0], n[1]): continue
                ng = g[cur] + 1.0
                if ng < g.get(n, float('inf')):
                    g[n] = ng
                    came_from[n] = cur
                    heapq.heappush(open_heap, (ng + self._h(n, goal), n))
                    
        if goal not in came_from and start != goal: return []
            
        path = [goal]
        while path[-1] != start: path.append(came_from[path[-1]])
        path.reverse()
        
        smoothed = self.smooth_path(path)
        return [(c[0] * TILE_SIZE + TILE_SIZE/2, c[1] * TILE_SIZE + TILE_SIZE/2) for c in smoothed]

class Crate(QGraphicsTextItem):
    def __init__(self, x, y):
        super().__init__("📦")
        self.setPos(x, y); self.setFont(QFont("Arial", 16))
        self.life = 30000 
        self.max_life = 30000
        
    def tick(self, dt):
        self.life -= dt
        if self.life <= 5000:
            self.setOpacity(self.life / 5000) # Fade out warning
        if self.life <= 0:
            if self.scene(): self.scene().removeItem(self)
            return False
        return True

class Meteor(QGraphicsTextItem):
    def __init__(self, x, y):
        super().__init__("☄️")
        self.setPos(x, y); self.setFont(QFont("Arial", 24))
        self.life = 1500; self.max_life = 1500
        self.exploded = False
        self.fuse_done = False
        
    def tick(self, dt):
        self.life -= dt
        if self.life <= 800 and not self.fuse_done:
            self.fuse_done = True
            self.exploded = True
            self.scene().add_effect(self.x(), self.y(), "💥", lifespan=500, size=32)
            for u in self.scene().team_red + self.scene().team_blue:
                if not u.is_dead() and math.hypot(u.x() - self.x(), u.y() - self.y()) < 60:
                    u.take_damage(60, is_env=True)
            self.scene().damage_terrain(self.x(), self.y(), 100)
        if self.life <= 0:
            self.scene().removeItem(self)
            return False
        return True

class Projectile(QGraphicsTextItem):
    def __init__(self, start_x, start_y, target, damage, emoji="✨", is_crit=False, applies_slow=False, splash=0.0, all_enemies=None, applies_poly=False, applies_poison=False, applies_stun=False, attacker=None, scene_ref=None):
        super().__init__(emoji)
        self.setPos(start_x, start_y); self.setFont(QFont("Arial", 12))
        self.target = target; self.damage = damage; self.speed = 8.0
        self.is_crit = is_crit; self.applies_slow = applies_slow; self.splash = splash
        self.all_enemies = all_enemies if all_enemies else []
        self.applies_poly = applies_poly; self.applies_poison = applies_poison; self.applies_stun = applies_stun
        self.attacker = attacker; self.scene_ref = scene_ref
        
    def tick(self):
        if not self.target or self.target.health <= 0:
            self.scene().removeItem(self); return False
        dx = self.target.x() - self.x(); dy = self.target.y() - self.y(); dist = math.hypot(dx, dy)
        if dist < self.speed:
            self.target.take_damage(self.damage, is_crit=self.is_crit, attacker=self.attacker)
            if self.applies_slow: self.target.slow_timer = 3000
            if self.applies_poly: self.target.polymorph_timer = 1500
            if self.applies_poison: self.target.poison_timer = 4000
            if self.applies_stun: self.target.stun_timer = 1000
            if self.splash > 0:
                for e in self.all_enemies:
                    if e != self.target and not e.is_dead():
                        if math.hypot(e.x() - self.target.x(), e.y() - self.target.y()) < 40:
                            e.take_damage(self.damage * self.splash, attacker=self.attacker)
                if self.scene_ref: self.scene_ref.damage_terrain(self.target.x(), self.target.y(), self.damage * self.splash)
            self.scene().removeItem(self); return False
        else:
            self.moveBy(dx/dist * self.speed, dy/dist * self.speed); return True

class CombatText(QGraphicsTextItem):
    def __init__(self, x, y, text, color):
        super().__init__(text)
        self.setPos(x + random.uniform(-10, 10), y)
        self.setFont(QFont("Arial", 10, QFont.Weight.Bold)); self.setDefaultTextColor(color)
        self.life = 600; self.speed = 1.0
        
    def tick(self, dt):
        self.moveBy(0, -self.speed); self.speed *= 0.95; self.life -= dt
        self.setOpacity(max(0, self.life / 600))
        if self.life <= 0:
            self.scene().removeItem(self); return False
        return True

class Effect(QGraphicsTextItem):
    def __init__(self, x, y, emoji, lifespan=400, size=16):
        super().__init__(emoji)
        self.setPos(x, y); self.setFont(QFont("Arial", size))
        self.life = lifespan; self.max_life = lifespan
        
    def tick(self, dt):
        self.life -= dt; self.setOpacity(max(0, self.life / self.max_life))
        if self.life <= 0:
            self.scene().removeItem(self); return False
        return True

class Unit(QGraphicsRectItem):
    def __init__(self, x, y, team, unit_type, pathfinder, scene_ref, kill_feed_callback, spawn_callback):
        super().__init__(-15, -15, 30, 30)
        self.setPos(x, y); self.setPen(Qt.PenStyle.NoPen); self.setZValue(1)
        self.team = team; self.unit_type = unit_type; self.pathfinder = pathfinder
        self.scene_ref = scene_ref; self.kill_feed_cb = kill_feed_callback; self.spawn_cb = spawn_callback
        stats = UNIT_TYPES[unit_type]
        
        self.max_health = stats["health"]; self.health = stats["health"]
        self.base_speed = stats["speed"]; self.base_damage = stats["damage"]
        self.base_attack_range = stats["attack_range"]
        self.is_ranged = stats.get("ranged", False); self.is_healer = stats.get("healer", False)
        self.is_minion = stats.get("is_minion", False)
        self.splash = stats.get("splash", 0.0)
        self.lifesteal = stats.get("lifesteal", 0.0)
        self.base_evasion = stats.get("evasion", 0.0)
        self.vision_range = 250 if not self.is_minion else 150
        
        self.energy = 0 if not self.is_minion else 9999 
        self.max_energy = stats.get("ult_cost", 0)
        self.emoji = stats[f"emoji_{team}"]
        self.kills = 0 
        
        self.text_item = QGraphicsTextItem(self.emoji, self)
        font = QFont(); font.setPointSize(16 if not self.is_minion else 12); self.text_item.setFont(font)
        text_rect = self.text_item.boundingRect()
        self.text_item.setPos(-text_rect.width()/2, -text_rect.height()/2)
        
        self.action_icon = QGraphicsTextItem("", self)
        icon_font = QFont("Arial", 8); self.action_icon.setFont(icon_font)
        self.action_icon.setPos(-5, -22)
        
        self.status_icon = QGraphicsTextItem("", self)
        self.status_icon.setFont(icon_font)
        self.status_icon.setPos(5, -22)
        
        self.health_bar_bg = QGraphicsRectItem(-15, 12, 30, 4, self)
        self.health_bar_bg.setBrush(QBrush(QColor(80, 80, 80))); self.health_bar_bg.setPen(Qt.PenStyle.NoPen)
        self.health_bar = QGraphicsRectItem(-15, 12, 30, 4, self)
        self.health_bar.setBrush(QBrush(QColor(0, 200, 0))); self.health_bar.setPen(Qt.PenStyle.NoPen)
        
        self.aura_visual = QGraphicsRectItem(-20, -20, 40, 40, self)
        self.aura_visual.setPen(QPen(Qt.PenStyle.NoPen)); self.aura_visual.setBrush(QBrush(QColor(255, 215, 0, 0)))
        
        self.target = None; self.path = []; self.last_attack_time = 0; self.repath_timer = 0
        self._target_line = None
        self.knockback_x = 0; self.knockback_y = 0; self.hit_flash_timer = 0
        
        self.slow_timer = 0; self.buff_timer = 0; self.shield_hp = 0; self.death_timer = 0
        self.env_tick_timer = 0; self.is_hidden = False; self.stealth_timer = 0
        self.tank_aura_timer = 0; self.commander_aura_timer = 0; self.druid_aura_timer = 0
        self.taunt_target = None; self.taunt_timer = 0; self.rampage_timer = 0
        self.polymorph_timer = 0; self.target_lock_timer = 0
        self.necro_summon_timer = 8000; self.tinkerer_turret_timer = 10000
        self.nexus_spawn_timer = 15000
        
        self.stun_timer = 0
        self.poison_timer = 0; self.poison_tick_timer = 0
        self.armor_break_timer = 0
        self.burn_timer = 0; self.burn_tick_timer = 0
        
        self.is_bear = False; self.bear_timer = 0
        self.divine_shield_timer = 0
        self.charm_timer = 0
        self.overclock_timer = 0
        self.rage_timer = 0 
        
        self.aggro_table = {}

    def get_current_terrain(self):
        gx, gy = int(self.x() // TILE_SIZE), int(self.y() // TILE_SIZE)
        if 0 <= gx < GRID_W and 0 <= gy < GRID_H:
            return self.scene_ref.terrain[gy][gx]
        return "grass"

    def add_threat(self, target, amount):
        if target.is_dead(): return
        self.aggro_table[target] = min(self.aggro_table.get(target, 0) + amount, 500)

    def evaluate_utility(self, enemies, allies):
        scores = {"ATTACK": 0, "FLEE": 0, "CAPTURE": 0, "GROUP": 0, "HEAL": 0, "DEFEND": 0, "PEEL": 0, "CLEANSE": 0, "DANGER": 0, "GATHER": 0}
        hp_pct = self.health / self.max_health
        
        if self.polymorph_timer > 0 or self.stun_timer > 0: return "IDLE", None
        if self.taunt_target and not self.taunt_target.is_dead(): return "ATTACK", self.taunt_target

        if self.is_minion and self.unit_type != "nexus":
            return "ATTACK", self.find_strategic_target(enemies, allies)
            
        if self.unit_type == "nexus": return "IDLE", None

        if self.get_current_terrain() == "lava" or self.burn_timer > 0: scores["DANGER"] = 250
        for hz in self.scene_ref.hazards:
            if hz.exploded: continue
            if math.hypot(hz.x()-self.x(), hz.y()-self.y()) < 60:
                scores["DANGER"] = 250; break

        is_routing = (self.team == "red" and self.scene_ref.team_red_routing) or \
                     (self.team == "blue" and self.scene_ref.team_blue_routing)
        if is_routing and self.unit_type in SQUISHY_TYPES:
            nearby_allies = sum(1 for a in allies if not a.is_dead() and math.hypot(a.x()-self.x(), a.y()-self.y()) < 100)
            if nearby_allies >= 3: self.buff_timer = 3000 
            else: return "FLEE", None

        if self.unit_type != "berserker" and self.divine_shield_timer <= 0:
            if hp_pct < 0.4:
                flee_threshold = 0.4 if self.unit_type in SQUISHY_TYPES else 0.2
                if hp_pct < flee_threshold: scores["FLEE"] = ((1.0 - hp_pct) ** 2) * 150

        if self.scene_ref.crates and not self.is_minion:
            nearest_crate = min(self.scene_ref.crates, key=lambda c: math.hypot(c.x()-self.x(), c.y()-self.y()))
            dist_to_crate = math.hypot(nearest_crate.x()-self.x(), nearest_crate.y()-self.y())
            if dist_to_crate < 300:
                crate_score = 100 - (dist_to_crate * 0.2)
                if hp_pct < 0.6 or self.energy < self.max_energy * 0.5: crate_score += 50
                scores["GATHER"] = crate_score

        if self.unit_type in ["healer", "paladin", "druid"]:
            cc_allies = [a for a in allies if (a.stun_timer > 0 or a.polymorph_timer > 0 or a.charm_timer > 0) and not a.is_dead()]
            if cc_allies:
                closest_cc = min(cc_allies, key=lambda a: math.hypot(a.x()-self.x(), a.y()-self.y()))
                dist = math.hypot(closest_cc.x()-self.x(), closest_cc.y()-self.y())
                scores["CLEANSE"] = 150 - dist 
                    
        if self.scene_ref.commander_in_danger and self.unit_type in ["tank", "warrior", "berserker", "paladin"]:
            commander = next((a for a in allies if a.unit_type == "commander" and not a.is_dead()), None)
            if commander:
                dist_to_comm = math.hypot(commander.x()-self.x(), commander.y()-self.y())
                scores["DEFEND"] = 120 if dist_to_comm > 40 else 60
                    
        if self.scene_ref.cp_coords and self.get_current_terrain() != "capture_point" and self.base_speed > 0:
            nearest_cp = min(self.scene_ref.cp_coords, key=lambda c: math.hypot(c[0]-self.x(), c[1]-self.y()))
            dist_to_cp = math.hypot(nearest_cp[0]-self.x(), nearest_cp[1]-self.y())
            scores["CAPTURE"] = max(0, 80 - dist_to_cp * 0.2)
            
        if self.unit_type in SQUISHY_TYPES:
            protectors = [a for a in allies if a.unit_type in PROTECTOR_TYPES and not a.is_dead()]
            if protectors:
                closest_prot = min(protectors, key=lambda p: math.hypot(p.x()-self.x(), p.y()-self.y()))
                dist_to_prot = math.hypot(closest_prot.x()-self.x(), closest_prot.y()-self.y())
                scores["GROUP"] = 60 if dist_to_prot > 100 else 20
            else: scores["GROUP"] = 0
                
        if self.is_healer:
            injured = [a for a in allies if a.health < a.max_health * 0.8 and not a.is_dead()]
            if injured:
                most_injured = max(injured, key=lambda a: a.max_health - a.health)
                scores["HEAL"] = min(100, (most_injured.max_health - most_injured.health) * 1.5)

        if self.unit_type in ["tank", "paladin"]:
            squishies = [a for a in allies if a.unit_type in SQUISHY_TYPES and not a.is_dead()]
            for s in squishies:
                for e in enemies:
                    if e.is_dead() or e.is_minion: continue
                    if math.hypot(e.x()-s.x(), e.y()-s.y()) < 40:
                        scores["PEEL"] = 110 
                        
        target = self.find_strategic_target(enemies, allies)
        if target:
            dist = math.hypot(target.x()-self.x(), target.y()-self.y())
            scores["ATTACK"] = 70 - (dist * 0.1) + self.aggro_table.get(target, 0)
            if target.health < target.max_health * 0.3: scores["ATTACK"] += 30
            
            if self.unit_type in RANGED_KITERS:
                if target.stun_timer > 0 or target.armor_break_timer > 0: scores["ATTACK"] += 60
                
            if self.unit_type == "assassin":
                cluster_count = sum(1 for en in enemies if math.hypot(en.x()-target.x(), en.y()-target.y()) < 80)
                scores["ATTACK"] += 50 if cluster_count <= 1 else -30
            if self.is_healer: scores["ATTACK"] = 0
            
        best_action = max(scores, key=scores.get)
        if self.is_healer and scores["HEAL"] > 30: best_action = "HEAL"
        if scores["FLEE"] > 80: best_action = "FLEE"
        if scores["DEFEND"] > 100: best_action = "DEFEND"
        if scores["PEEL"] > 100: best_action = "PEEL"
        if scores["CLEANSE"] > 100: best_action = "CLEANSE"
        if scores["DANGER"] > 200: best_action = "DANGER"
        if scores["GATHER"] > 120: best_action = "GATHER"
        
        return best_action, target

    def update_ai(self, enemies, allies, current_time, dt):
        if self.health <= 0:
            self.death_timer += dt; return

        if self.unit_type == "nexus":
            self.nexus_spawn_timer -= dt
            if self.nexus_spawn_timer <= 0:
                self.nexus_spawn_timer = 15000
                self.spawn_cb(self.x() + random.uniform(-20, 20), self.y() + random.uniform(-20, 20), self.team, "minion")
            return

        if self.charm_timer > 0:
            self.charm_timer -= dt
            enemies, allies = allies, enemies 

        if self.slow_timer > 0: self.slow_timer -= dt
        if self.buff_timer > 0: self.buff_timer -= dt
        if self.tank_aura_timer > 0: self.tank_aura_timer -= dt
        if self.commander_aura_timer > 0: self.commander_aura_timer -= dt
        if self.druid_aura_timer > 0: self.druid_aura_timer -= dt
        if self.taunt_timer > 0: self.taunt_timer -= dt
        if self.taunt_timer <= 0: self.taunt_target = None
        if self.rampage_timer > 0: self.rampage_timer -= dt
        if self.polymorph_timer > 0: self.polymorph_timer -= dt
        if self.target_lock_timer > 0: self.target_lock_timer -= dt
        if self.divine_shield_timer > 0: self.divine_shield_timer -= dt
        if self.armor_break_timer > 0: self.armor_break_timer -= dt
        if self.stun_timer > 0: self.stun_timer -= dt
        if self.overclock_timer > 0: self.overclock_timer -= dt
        if self.rage_timer > 0: self.rage_timer -= dt
        if self.bear_timer > 0:
            self.bear_timer -= dt
            if self.bear_timer <= 0: self.is_bear = False; self.text_item.setPlainText(self.emoji)
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt
            if self.hit_flash_timer <= 0: self.text_item.setDefaultTextColor(QColor(0, 0, 0))
            
        if self.poison_timer > 0:
            self.poison_timer -= dt; self.poison_tick_timer += dt
            if self.poison_tick_timer >= 1000:
                self.poison_tick_timer = 0; self.take_damage(5, is_env=True)
                self.scene_ref.add_effect(self.x(), self.y(), "☠️", lifespan=300, size=10)
        if self.burn_timer > 0:
            self.burn_timer -= dt; self.burn_tick_timer += dt
            if self.burn_tick_timer >= 1000:
                self.burn_tick_timer = 0; self.take_damage(8, is_env=True)
                self.scene_ref.add_effect(self.x(), self.y(), "🔥", lifespan=300, size=10)

        if self.polymorph_timer > 0:
            self.text_item.setPlainText("🐑"); return 
        if self.stun_timer > 0:
            self.text_item.setPlainText("⚡"); return 

        if self.is_minion and self.unit_type != "nexus":
            self.death_timer += dt 
            if self.death_timer > 15000: self.take_damage(999)

        if self.unit_type == "necromancer":
            self.necro_summon_timer -= dt
            if self.necro_summon_timer <= 0:
                self.necro_summon_timer = 8000
                dead_enemies = [e for e in enemies if e.is_dead() and e.death_timer < 4000 and not e.is_minion]
                if dead_enemies and len([a for a in allies if a.is_minion]) < 4:
                    closest_dead = min(dead_enemies, key=lambda e: math.hypot(e.x()-self.x(), e.y()-self.y()))
                    self.spawn_cb(closest_dead.x(), closest_dead.y(), self.team, "minion")
                    closest_dead.death_timer = 9999 
                    self.scene_ref.add_effect(closest_dead.x(), closest_dead.y(), "👻", size=16)
                    
        if self.unit_type == "tinkerer":
            self.tinkerer_turret_timer -= dt
            if self.tinkerer_turret_timer <= 0:
                self.tinkerer_turret_timer = 12000
                if len([a for a in allies if a.unit_type == "turret"]) < 2:
                    self.spawn_cb(self.x()+30, self.y(), self.team, "turret")

        if self.unit_type == "tank":
            for a in allies:
                if a == self or a.is_dead(): continue
                if math.hypot(a.x() - self.x(), a.y() - self.y()) < 60: a.tank_aura_timer = 100
                for e in enemies:
                    if not e.is_dead() and math.hypot(e.x()-self.x(), e.y()-self.y()) < 250:
                        e.add_threat(self, 0.5)
        elif self.unit_type == "commander":
            for a in allies:
                if a == self or a.is_dead(): continue
                if math.hypot(a.x() - self.x(), a.y() - self.y()) < 80: a.commander_aura_timer = 100
        elif self.unit_type == "druid" and not self.is_bear:
            for a in allies:
                if a == self or a.is_dead(): continue
                if math.hypot(a.x() - self.x(), a.y() - self.y()) < 70:
                    a.druid_aura_timer = 100
                    a.health = min(a.max_health, a.health + 0.1 * (dt / 16.0))
        elif self.unit_type == "ward":
            for a in allies:
                if a == self or a.is_dead(): continue
                if math.hypot(a.x() - self.x(), a.y() - self.y()) < 80:
                    a.health = min(a.max_health, a.health + 0.2 * (dt / 16.0))

        curr_terrain = self.get_current_terrain(); t_data = TERRAIN_TYPES[curr_terrain]
        if curr_terrain == "bush" and current_time - self.last_attack_time > 2000 and self.stealth_timer <= 0:
            if not self.is_hidden: self.is_hidden = True; self.setOpacity(0.4)
        else:
            if self.is_hidden and self.stealth_timer <= 0: self.is_hidden = False; self.setOpacity(1.0)

        if "dps" in t_data:
            self.env_tick_timer += dt
            if self.env_tick_timer >= 1000:
                self.env_tick_timer = 0; env_val = t_data["dps"]
                if env_val > 0:
                    self.take_damage(env_val, attacker=None, is_env=True)
                    self.burn_timer = 3000 
                    self.scene_ref.add_effect(self.x(), self.y(), "🔥", lifespan=300, size=12)
                    if self.health <= 0: return
                elif env_val < 0 and self.health < self.max_health:
                    heal_amt = -env_val; self.health = min(self.max_health, self.health + heal_amt)
                    self.scene_ref.add_combat_text(self.x(), self.y(), f"+{int(heal_amt)}", QColor(0, 255, 0))
        
        energy_mod = t_data.get("energy_mod", 1.0)
        self.energy = min(self.max_energy, self.energy + (0.5 * energy_mod * dt / 16.0))

        terrain_speed_mod = t_data["speed_mod"]
        eff_speed = self.base_speed * (0.5 if self.slow_timer > 0 else 1.0) * (1.5 if self.buff_timer > 0 else 1.0) * terrain_speed_mod
        eff_damage = self.base_damage * (1.5 if self.buff_timer > 0 else 1.0)
        eff_range = self.base_attack_range * t_data.get("range_mod", 1.0)
        is_ranged = self.is_ranged
        eff_evasion = self.base_evasion + t_data.get("evasion_mod", 0.0)
        
        if self.commander_aura_timer > 0: eff_speed *= 1.25; eff_damage *= 1.25
        if self.overclock_timer > 0: eff_speed *= 1.3; eff_damage *= 1.5
        if self.rage_timer > 0: eff_speed *= 1.5; eff_damage *= 2.0
            
        eff_vision = self.vision_range
        if self.scene_ref.weather == "RAIN":
            if self.unit_type == "druid": self.health = min(self.max_health, self.health + 0.05 * (dt / 16.0))
            else: eff_speed *= 0.9
            self.burn_timer = 0 
        elif self.scene_ref.weather == "FOG":
            eff_vision *= 0.5
            
        if self.scene_ref.is_night:
            eff_vision *= 0.7
            if self.unit_type in ["assassin", "vampire"]:
                eff_damage *= 1.3; eff_evasion += 0.2
                
        self._eff_vision = eff_vision # Cache for find_strategic_target

        is_routing = (self.team == "red" and self.scene_ref.team_red_routing) or \
                     (self.team == "blue" and self.scene_ref.team_blue_routing)
        if is_routing:
            if self.unit_type in SQUISHY_TYPES: eff_speed *= 1.5
            elif self.unit_type == "berserker": eff_damage *= 1.5
            
        if self.unit_type == "berserker":
            hp_pct = self.health / self.max_health
            passive_mod = 1.0 + (1.0 - hp_pct) * 0.5 
            eff_speed *= passive_mod; eff_damage *= passive_mod
            if self.rampage_timer > 0: eff_damage *= 2.0; eff_speed *= 1.2
            
        if self.is_bear:
            eff_speed *= 1.2; eff_damage *= 2.5; eff_range = 25; is_ranged = False

        if self.kills >= 6:
            eff_damage *= 1.5; self.lifesteal = max(self.lifesteal, 0.5)
            self.aura_visual.setBrush(QBrush(QColor(255, 0, 0, 120)))
        elif self.kills >= 3:
            eff_damage *= 1.25; self.aura_visual.setBrush(QBrush(QColor(255, 100, 0, 120)))

        if self.target_lock_timer > 0 and self.target and not self.target.is_dead() and not self.taunt_target:
            action = "ATTACK" if not self.is_healer else "HEAL"
            if self.is_healer and self.target.health >= self.target.max_health:
                action, attack_target = self.evaluate_utility(enemies, allies)
            else:
                attack_target = self.target
        else:
            action, attack_target = self.evaluate_utility(enemies, allies)
            if attack_target and attack_target != self.target:
                self.target_lock_timer = 1500
                
        self.current_action = action
        self.action_icon.setPlainText(ACTION_ICONS.get(action, ""))
        target_pos = None
        self.target = attack_target
        
        if action == "DANGER":
            nearest_hz = min(self.scene_ref.hazards, key=lambda h: math.hypot(h.x()-self.x(), h.y()-self.y()))
            dx = self.x() - nearest_hz.x(); dy = self.y() - nearest_hz.y(); dist = math.hypot(dx, dy)
            if dist > 0: target_pos = (self.x() + (dx/dist)*100, self.y() + (dy/dist)*100)
        elif action == "FLEE":
            sanctuary = self.find_nearest_terrain("sanctuary")
            if sanctuary: target_pos = sanctuary
            else: target_pos = (20, self.y()) if self.team == "red" else (SCENE_WIDTH-20, self.y())
        elif action == "CAPTURE": target_pos = self.find_nearest_terrain("capture_point")
        elif action in ["GROUP", "DEFEND"]:
            protectors = [a for a in allies if a.unit_type in PROTECTOR_TYPES and not a.is_dead()]
            if protectors:
                closest_prot = min(protectors, key=lambda p: math.hypot(p.x()-self.x(), p.y()-self.y()))
                target_pos = (closest_prot.x(), closest_prot.y())
        elif action == "PEEL":
            squishies = [a for a in allies if a.unit_type in SQUISHY_TYPES and not a.is_dead()]
            threatened_squishy = None
            for s in squishies:
                for e in enemies:
                    if not e.is_dead() and math.hypot(e.x()-s.x(), e.y()-s.y()) < 40:
                        threatened_squishy = s; break
                if threatened_squishy: break
            if threatened_squishy:
                target_pos = ((threatened_squishy.x() + enemies[0].x())/2, (threatened_squishy.y() + enemies[0].y())/2)
        elif action == "HEAL":
            injured = [a for a in allies if a.health < a.max_health * 0.8 and not a.is_dead()]
            if injured:
                most_injured = max(injured, key=lambda a: a.max_health - a.health)
                self.target = most_injured; target_pos = (most_injured.x(), most_injured.y())
        elif action == "CLEANSE":
            cc_allies = [a for a in allies if (a.stun_timer > 0 or a.polymorph_timer > 0 or a.charm_timer > 0) and not a.is_dead()]
            if cc_allies:
                closest_cc = min(cc_allies, key=lambda a: math.hypot(a.x()-self.x(), a.y()-self.y()))
                self.target = closest_cc; target_pos = (closest_cc.x(), closest_cc.y())
        elif action == "GATHER":
            if self.scene_ref.crates:
                nearest_crate = min(self.scene_ref.crates, key=lambda c: math.hypot(c.x()-self.x(), c.y()-self.y()))
                target_pos = (nearest_crate.x(), nearest_crate.y())
                if math.hypot(nearest_crate.x() - self.x(), nearest_crate.y() - self.y()) < 20:
                    self.energy = self.max_energy
                    self.shield_hp = max(self.shield_hp, 100)
                    self.buff_timer = max(self.buff_timer, 8000)
                    self.scene_ref.add_effect(self.x(), self.y(), "✨", size=20)
                    self.scene_ref.crates.remove(nearest_crate)
                    self.scene().removeItem(nearest_crate)
                    self.scene_ref.add_combat_text(self.x(), self.y(), "CRATE!", QColor(255, 215, 0))
        elif action == "ATTACK" and attack_target:
            target_pos = (attack_target.x(), attack_target.y())
            
        move_x, move_y = 0, 0; is_kiting = False
        
        if self.base_speed > 0 and target_pos:
            dx = target_pos[0] - self.x(); dy = target_pos[1] - self.y()
            distance = math.hypot(dx, dy)
            
            if action == "ATTACK" and distance <= eff_range:
                has_los = self.pathfinder.has_los((int(self.x()//TILE_SIZE), int(self.y()//TILE_SIZE)), 
                                                  (int(self.target.x()//TILE_SIZE), int(self.target.y()//TILE_SIZE)))
                if not has_los:
                    if distance > 10:
                        if not self.path or current_time - self.repath_timer > 1000:
                            self.path = self.pathfinder.find_path(self.pos().toTuple(), target_pos)
                            self.repath_timer = current_time
                        if self.path:
                            next_waypoint = self.path[0]
                            wp_dx = next_waypoint[0] - self.x(); wp_dy = next_waypoint[1] - self.y()
                            wp_dist = math.hypot(wp_dx, wp_dy)
                            if wp_dist < eff_speed * 2: self.path.pop(0)
                            elif wp_dist > 1e-6: move_x = wp_dx/wp_dist * eff_speed; move_y = wp_dy/wp_dist * eff_speed
                else:
                    if distance > 1e-6 and self.unit_type in RANGED_KITERS and not self.is_bear and distance < 60:
                        is_kiting = True
                        move_x = -dx/distance * eff_speed; move_y = -dy/distance * eff_speed
                    else:
                        if current_time - self.last_attack_time >= ATTACK_COOLDOWN:
                            self.attack_target(eff_damage, enemies, is_ranged); self.last_attack_time = current_time
            elif action == "HEAL" and distance <= eff_range:
                if current_time - self.last_attack_time >= ATTACK_COOLDOWN:
                    self.attack_target(eff_damage, enemies, True); self.last_attack_time = current_time
            elif action == "CLEANSE" and distance <= eff_range:
                if current_time - self.last_attack_time >= ATTACK_COOLDOWN:
                    self.target.stun_timer = 0; self.target.polymorph_timer = 0; self.target.charm_timer = 0
                    self.target.shield_hp = max(self.target.shield_hp, 50)
                    self.scene_ref.add_effect(self.target.x(), self.target.y(), "🌊", size=18)
                    self.last_attack_time = current_time
                    
            if not is_kiting and distance > 10 and action not in ["CLEANSE", "ATTACK"]:
                if not self.path or current_time - self.repath_timer > 1000:
                    self.path = self.pathfinder.find_path(self.pos().toTuple(), target_pos)
                    self.repath_timer = current_time
                if self.path:
                    next_waypoint = self.path[0]
                    wp_dx = next_waypoint[0] - self.x(); wp_dy = next_waypoint[1] - self.y()
                    wp_dist = math.hypot(wp_dx, wp_dy)
                    if wp_dist < eff_speed * 2: self.path.pop(0)
                    elif wp_dist > 1e-6: move_x = wp_dx/wp_dist * eff_speed; move_y = wp_dy/wp_dist * eff_speed
            elif not is_kiting and distance > 10: 
                if not self.path or current_time - self.repath_timer > 1000:
                    self.path = self.pathfinder.find_path(self.pos().toTuple(), target_pos)
                    self.repath_timer = current_time
                if self.path:
                    next_waypoint = self.path[0]
                    wp_dx = next_waypoint[0] - self.x(); wp_dy = next_waypoint[1] - self.y()
                    wp_dist = math.hypot(wp_dx, wp_dy)
                    if wp_dist < eff_speed * 2: self.path.pop(0)
                    elif wp_dist > 1e-6: move_x = wp_dx/wp_dist * eff_speed; move_y = wp_dy/wp_dist * eff_speed

        sep_x, sep_y = 0, 0
        for ally in allies:
            if ally == self or ally.is_dead(): continue
            ally_dx = self.x() - ally.x(); ally_dy = self.y() - ally.y(); ally_dist = math.hypot(ally_dx, ally_dy)
            if 0 < ally_dist < 28: sep_x += (ally_dx / ally_dist) * (28 - ally_dist); sep_y += (ally_dy / ally_dist) * (28 - ally_dist)
        for enemy in enemies:
            if enemy.is_dead(): continue
            en_dx = self.x() - enemy.x(); en_dy = self.y() - enemy.y(); en_dist = math.hypot(en_dx, en_dy)
            if 0 < en_dist < 28: sep_x += (en_dx / en_dist) * (28 - en_dist); sep_y += (en_dy / en_dist) * (28 - en_dist)

        final_x = move_x + (sep_x * 0.4) + self.knockback_x
        final_y = move_y + (sep_y * 0.4) + self.knockback_y
        self.knockback_x *= 0.8; self.knockback_y *= 0.8
        
        final_mag = math.hypot(final_x, final_y)
        if final_mag > 0:
            if math.hypot(self.knockback_x, self.knockback_y) > eff_speed: self.moveBy(final_x, final_y)
            else:
                speed_factor = min(eff_speed, final_mag) / final_mag
                self.moveBy(final_x * speed_factor, final_y * speed_factor)

        self.update_health_visual(); self.update_status_visuals(); self.update_debug_visuals()

        if self.energy >= self.max_energy and not self.is_minion:
            self.cast_ultimate(enemies, allies, eff_damage); self.energy = 0

    def find_nearest_terrain(self, t_type):
        positions = self.scene_ref._simulator.get_terrain_positions(t_type)
        if not positions: return None
        return min(positions, key=lambda p: math.hypot(p[0]-self.x(), p[1]-self.y()))

    def attack_target(self, eff_damage, enemies, is_ranged):
        is_crit = random.random() < 0.2
        dmg = eff_damage * (1.5 if is_crit else 1.0)
        self.energy = min(self.max_energy, self.energy + 15)
        if self.is_hidden: self.is_hidden = False; self.setOpacity(1.0)
            
        if is_ranged:
            if self.is_healer: proj_emoji = "✨"
            elif self.unit_type == "mage": proj_emoji = "🔥"
            elif self.unit_type == "commander": proj_emoji = "🚩"
            elif self.unit_type == "necromancer": proj_emoji = "☠️"
            elif self.unit_type == "druid": proj_emoji = "🌿"
            elif self.unit_type == "vampire": proj_emoji = "🩸"
            elif self.unit_type == "tinkerer": proj_emoji = "🔩"
            elif self.unit_type == "alchemist": proj_emoji = "🧪"
            else: proj_emoji = "➶"
            
            applies_poly = (self.unit_type == "mage" and random.random() < 0.15)
            applies_poison = (self.unit_type in ["druid", "alchemist"])
            applies_slow = (self.unit_type == "tinkerer")
            if applies_poly: proj_emoji = "🐑"
            
            proj = Projectile(self.x(), self.y(), self.target, dmg, proj_emoji, is_crit, splash=self.splash, all_enemies=enemies, applies_poly=applies_poly, applies_poison=applies_poison, applies_slow=applies_slow, attacker=self, scene_ref=self.scene_ref)
            self.scene().addItem(proj); self.scene().projectiles.append(proj)
        else:
            self.target.take_damage(dmg, attacker=self, is_crit=is_crit)
            if self.unit_type == "vampire" and dmg > 0:
                self.health = min(self.max_health, self.health + dmg * self.lifesteal)
                self.scene_ref.add_combat_text(self.x(), self.y()-5, f"+{int(dmg*self.lifesteal)}", QColor(200, 0, 0))
            if self.unit_type == "tank":
                self.target.taunt_target = self; self.target.taunt_timer = 3000; self.apply_knockback(self.target, 3)
            if self.unit_type == "paladin" and random.random() < 0.15:
                self.target.stun_timer = 1000
            if self.is_bear: 
                for e in enemies:
                    if e != self.target and not e.is_dead():
                        if math.hypot(e.x() - self.target.x(), e.y() - self.target.y()) < 40: e.take_damage(dmg * 0.5, attacker=self)

    def cast_ultimate(self, enemies, allies, eff_damage):
        choice = random.randint(1, 3)
        if self.unit_type == "tank":
            if choice == 1:
                self.scene_ref.add_effect(self.x(), self.y(), "💥", size=24)
                for e in enemies:
                    if e.is_dead(): continue
                    if math.hypot(e.x() - self.x(), e.y() - self.y()) < 80: e.take_damage(eff_damage * 2.0, attacker=self); self.apply_knockback(e, 15)
                self.scene_ref.damage_terrain(self.x(), self.y(), eff_damage * 2.0)
            elif choice == 2:
                self.scene_ref.add_effect(self.x(), self.y(), "🛡️", size=20); self.shield_hp = 150; self.health = min(self.max_health, self.health + 50)
            else:
                if self.target: self.scene_ref.add_effect(self.target.x(), self.target.y(), "🪨", size=20); self.target.take_damage(eff_damage * 3.0, attacker=self); self.apply_knockback(self.target, 10)
        elif self.unit_type == "alchemist":
            if choice == 1: 
                self.scene_ref.add_effect(self.x(), self.y(), "💧", size=24)
                for a in allies:
                    if a.is_dead(): continue
                    if math.hypot(a.x() - self.x(), a.y() - self.y()) < 100: a.health = min(a.max_health, a.health + 100)
            elif choice == 2: 
                self.scene_ref.add_effect(self.x(), self.y(), "🧪", size=24)
                for e in enemies:
                    if e.is_dead(): continue
                    if math.hypot(e.x() - self.x(), e.y() - self.y()) < 100:
                        e.take_damage(eff_damage * 2.0, attacker=self); e.armor_break_timer = 4000; e.poison_timer = 4000
            else: 
                self.scene_ref.add_effect(self.x(), self.y(), "😡", size=22); self.rage_timer = 8000; self.health = min(self.max_health, self.health + 50)
        elif self.unit_type == "warrior":
            if choice == 1:
                self.scene_ref.add_effect(self.x(), self.y(), "⚡", size=20)
                if self.target: self.setPos(self.target.x() + random.uniform(-10, 10), self.target.y() + random.uniform(-10, 10)); self.target.take_damage(eff_damage * 3.0, attacker=self, is_crit=True)
            elif choice == 2:
                self.scene_ref.add_effect(self.x(), self.y(), "🌀", size=22)
                for e in enemies:
                    if e.is_dead(): continue
                    if math.hypot(e.x() - self.x(), e.y() - self.y()) < 50: e.take_damage(eff_damage * 1.5, attacker=self); self.apply_knockback(e, 5)
            else:
                self.scene_ref.add_effect(self.x(), self.y(), "📣", size=20)
                for a in allies:
                    if a.is_dead(): continue
                    if math.hypot(a.x() - self.x(), a.y() - self.y()) < 80: a.buff_timer = 4000
        elif self.unit_type == "archer":
            if choice == 1:
                self.scene_ref.add_effect(self.x(), self.y(), "🏹", size=18)
                if self.target:
                    for _ in range(3): proj = Projectile(self.x(), self.y(), self.target, eff_damage * 1.5, "🏹", is_crit=True, attacker=self, scene_ref=self.scene_ref); self.scene().addItem(proj); self.scene().projectiles.append(proj)
            elif choice == 2:
                if self.target: self.scene_ref.add_effect(self.target.x(), self.target.y(), "🎯", size=18)
                if self.target: proj = Projectile(self.x(), self.y(), self.target, eff_damage * 4.0, "➶", is_crit=True, attacker=self, scene_ref=self.scene_ref); proj.speed = 15.0; self.scene().addItem(proj); self.scene().projectiles.append(proj)
            else:
                self.scene_ref.add_effect(self.x(), self.y(), "❄️", size=18)
                if self.target: proj = Projectile(self.x(), self.y(), self.target, eff_damage, "❄️", applies_slow=True, attacker=self, scene_ref=self.scene_ref); self.scene().addItem(proj); self.scene().projectiles.append(proj)
        elif self.unit_type == "mage":
            if choice == 1:
                self.scene_ref.add_effect(self.x(), self.y(), "💥", size=28)
                for e in enemies:
                    if e.is_dead(): continue
                    if math.hypot(e.x() - self.x(), e.y() - self.y()) < 100: e.take_damage(eff_damage * 2.5, attacker=self); self.apply_knockback(e, 12)
                self.scene_ref.damage_terrain(self.x(), self.y(), eff_damage * 2.5)
            elif choice == 2:
                if self.target: self.scene_ref.add_effect(self.target.x(), self.target.y(), "☄️", size=24); self.target.take_damage(eff_damage * 4.0, attacker=self, is_crit=True)
                for e in enemies:
                    if e != self.target and not e.is_dead():
                        if math.hypot(e.x() - self.target.x(), e.y() - self.target.y()) < 50: e.take_damage(eff_damage * 1.5, attacker=self)
                self.scene_ref.damage_terrain(self.target.x(), self.target.y(), eff_damage * 4.0)
            else:
                self.scene_ref.add_effect(self.x(), self.y(), "🐑", size=24)
                for e in enemies:
                    if e.is_dead(): continue
                    if math.hypot(e.x() - self.x(), e.y() - self.y()) < 90: e.polymorph_timer = 2500
        elif self.unit_type == "assassin":
            if choice == 1:
                self.scene_ref.add_effect(self.x(), self.y(), "🌑", size=20)
                if self.target: self.setPos(self.target.x() + random.uniform(-10, 10), self.target.y() + random.uniform(-10, 10)); self.target.take_damage(eff_damage * 4.0, attacker=self, is_crit=True); self.stealth_timer = 1000
            elif choice == 2:
                self.scene_ref.add_effect(self.x(), self.y(), "🗡️", size=22)
                for e in enemies:
                    if e.is_dead(): continue
                    if math.hypot(e.x() - self.x(), e.y() - self.y()) < 40: e.take_damage(eff_damage * 2.0, attacker=self)
            else:
                self.scene_ref.add_effect(self.x(), self.y(), "💨", size=20); self.stealth_timer = 3000; self.health = min(self.max_health, self.health + 30)
        elif self.unit_type == "berserker":
            if choice == 1:
                self.scene_ref.add_effect(self.x(), self.y(), "🩸", size=24); self.health = self.max_health; self.rampage_timer = 5000
            elif choice == 2:
                self.scene_ref.add_effect(self.x(), self.y(), "🪓", size=22)
                for e in enemies:
                    if e.is_dead(): continue
                    if math.hypot(e.x() - self.x(), e.y() - self.y()) < 45: e.take_damage(eff_damage * 2.5, attacker=self)
                self.scene_ref.damage_terrain(self.x(), self.y(), eff_damage * 2.5)
            else:
                self.scene_ref.add_effect(self.x(), self.y(), "😡", size=20); self.buff_timer = 6000
        elif self.unit_type == "necromancer":
            if choice == 1:
                self.scene_ref.add_effect(self.x(), self.y(), "🪦", size=24); self.shield_hp = 100
                for _ in range(3):
                    sx, sy = self.x() + random.uniform(-30, 30), self.y() + random.uniform(-30, 30)
                    self.spawn_cb(sx, sy, self.team, "minion")
            elif choice == 2:
                if self.target: self.scene_ref.add_effect(self.target.x(), self.target.y(), "☠️", size=20); self.target.take_damage(eff_damage * 4.0, attacker=self)
                self.health = min(self.max_health, self.health + 40)
            else:
                self.scene_ref.add_effect(self.x(), self.y(), "🔋", size=22)
                for e in enemies:
                    if e.is_dead(): continue
                    if math.hypot(e.x() - self.x(), e.y() - self.y()) < 90: e.slow_timer = 4000; e.buff_timer = 0
        elif self.unit_type == "paladin":
            if choice == 1: 
                self.scene_ref.add_effect(self.x(), self.y(), "🛡️", size=24); self.divine_shield_timer = 4000
            elif choice == 2: 
                self.scene_ref.add_effect(self.x(), self.y(), "⚒️", size=24)
                for e in enemies:
                    if e.is_dead(): continue
                    if math.hypot(e.x() - self.x(), e.y() - self.y()) < 80: e.take_damage(eff_damage * 2.0, attacker=self)
                for a in allies:
                    if a.is_dead(): continue
                    if math.hypot(a.x() - self.x(), a.y() - self.y()) < 80: a.health = min(a.max_health, a.health + 40)
            else: 
                self.scene_ref.add_effect(self.x(), self.y(), "⚖️", size=22)
                for e in enemies:
                    if e.is_dead(): continue
                    if math.hypot(e.x() - self.x(), e.y() - self.y()) < 90: e.armor_break_timer = 4000
        elif self.unit_type == "druid":
            if choice == 1: 
                self.scene_ref.add_effect(self.x(), self.y(), "🐻", size=24); self.is_bear = True; self.bear_timer = 8000; self.health += 200; self.max_health += 200
            elif choice == 2: 
                self.scene_ref.add_effect(self.x(), self.y(), "🌿", size=24)
                for e in enemies:
                    if e.is_dead(): continue
                    if math.hypot(e.x() - self.x(), e.y() - self.y()) < 90: e.stun_timer = 2000
            else: 
                self.scene_ref.add_effect(self.x(), self.y(), "💧", size=24)
                for a in allies:
                    if a.is_dead(): continue
                    if math.hypot(a.x() - self.x(), a.y() - self.y()) < 120: a.health = min(a.max_health, a.health + 80)
        elif self.unit_type == "vampire":
            if choice == 1: 
                self.scene_ref.add_effect(self.x(), self.y(), "🦇", size=24)
                for _ in range(2):
                    sx, sy = self.x() + random.uniform(-20, 20), self.y() + random.uniform(-20, 20)
                    self.spawn_cb(sx, sy, self.team, "bat")
            elif choice == 2: 
                self.scene_ref.add_effect(self.x(), self.y(), "🩸", size=26)
                self.health -= self.health * 0.3
                dmg_dealt = 0
                for e in enemies:
                    if e.is_dead(): continue
                    if math.hypot(e.x() - self.x(), e.y() - self.y()) < 90:
                        dmg = eff_damage * 3.0; e.take_damage(dmg, attacker=self); dmg_dealt += dmg
                for a in allies:
                    if a.is_dead(): continue
                    if math.hypot(a.x() - self.x(), a.y() - self.y()) < 90: a.health = min(a.max_health, a.health + dmg_dealt * 0.2)
            else: 
                if self.target and not self.target.is_dead():
                    self.scene_ref.add_effect(self.target.x(), self.target.y(), "👁️", size=20)
                    self.target.charm_timer = 3000
        elif self.unit_type == "tinkerer":
            if choice == 1: 
                self.scene_ref.add_effect(self.x(), self.y(), "🔫", size=22)
                self.spawn_cb(self.x()+20, self.y(), self.team, "turret")
                self.spawn_cb(self.x()-20, self.y(), self.team, "turret")
            elif choice == 2: 
                self.scene_ref.add_effect(self.x(), self.y(), "🏥", size=22)
                self.spawn_cb(self.x(), self.y(), self.team, "ward")
            else: 
                self.scene_ref.add_effect(self.x(), self.y(), "⚡", size=24)
                for a in allies:
                    if a.is_dead(): continue
                    if math.hypot(a.x() - self.x(), a.y() - self.y()) < 100: a.overclock_timer = 5000
        elif self.unit_type == "healer":
            if choice == 1:
                self.scene_ref.add_effect(self.x(), self.y(), "✨", size=24)
                for a in allies:
                    if a.is_dead(): continue
                    if math.hypot(a.x() - self.x(), a.y() - self.y()) < 100: a.take_damage(eff_damage * 2.0)
            elif choice == 2:
                if self.target: self.scene_ref.add_effect(self.target.x(), self.target.y(), "💧", size=20); self.target.health = self.target.max_health; self.target.shield_hp = 80; self.target.slow_timer = 0
            else:
                dead_allies = [a for a in allies if a.is_dead() and a.death_timer < 5000 and not a.is_minion]
                if dead_allies:
                    closest_dead = min(dead_allies, key=lambda a: math.hypot(a.x() - self.x(), a.y() - self.y()))
                    closest_dead.health = closest_dead.max_health * 0.5; closest_dead.death_timer = 0
                    closest_dead.text_item.setPlainText(closest_dead.emoji); closest_dead.text_item.setDefaultTextColor(QColor(0, 0, 0))
                    self.scene_ref.add_effect(closest_dead.x(), closest_dead.y(), "✝️", size=24)

    def apply_knockback(self, target, force):
        dx = target.x() - self.x(); dy = target.y() - self.y(); dist = math.hypot(dx, dy)
        if dist < 1e-6:
            ang = random.uniform(0, math.tau)
            target.knockback_x = math.cos(ang) * force; target.knockback_y = math.sin(ang) * force
        else:
            target.knockback_x = (dx/dist) * force; target.knockback_y = (dy/dist) * force

    def find_strategic_target(self, enemies, allies):
        best_score = -float('inf'); best_target = None
        ally_targets = {a.target for a in allies if a.target is not None and not a.target.is_dead() and a.target in enemies}
        squishies = [a for a in allies if a.unit_type in SQUISHY_TYPES and not a.is_dead()]
        eff_vision = getattr(self, "_eff_vision", self.vision_range)

        for e in enemies:
            if e.health <= 0: continue
            if e.is_hidden:
                if math.hypot(e.x() - self.x(), e.y() - self.y()) > 30: continue

            dist = math.hypot(e.x() - self.x(), e.y() - self.y())
            if dist > eff_vision:
                spotted = any(not a.is_dead() and math.hypot(a.x() - e.x(), a.y() - e.y()) < 60 for a in allies)
                if not spotted: continue
            
            threat = self.aggro_table.get(e, 0)
            score = threat - (dist * 0.1)
            
            if e.kills >= 3: score += 100
            if e.unit_type == "nexus": score -= 200 
            
            if self.unit_type == "assassin" and e.unit_type == "tank": score -= 500
            if self.unit_type == "mage":
                cluster_count = sum(1 for en in enemies if math.hypot(en.x() - e.x(), en.y() - e.y()) < 60)
                score += cluster_count * 20
            if e in ally_targets: score += 60 
            if self.unit_type in ["tank", "paladin"] and squishies:
                min_e_dist_to_squishy = min([math.hypot(e.x() - s.x(), e.y() - s.y()) for s in squishies])
                if min_e_dist_to_squishy < 120: score += 100 
            if score > best_score: best_score = score; best_target = e
            
            self.aggro_table[e] = max(0, threat - 0.1)
            
        return best_target

    def take_damage(self, amount, attacker=None, is_crit=False, is_env=False):
        if self.health <= 0: return
        
        if self.divine_shield_timer > 0 and amount > 0:
            self.scene_ref.add_combat_text(self.x(), self.y(), "IMMUNE", QColor(255, 215, 0))
            return

        if not is_env and amount > 0:
            curr_terrain = self.get_current_terrain()
            evasion_chance = self.base_evasion + TERRAIN_TYPES[curr_terrain].get("evasion_mod", 0.0)
            if random.random() < evasion_chance:
                self.scene_ref.add_combat_text(self.x(), self.y(), "MISS", QColor(150, 150, 150))
                return
            
        if self.shield_hp > 0 and amount > 0:
            absorbed = min(self.shield_hp, amount); self.shield_hp -= absorbed; amount -= absorbed
            if amount <= 0: return
        if amount > 0:
            curr_terrain = self.get_current_terrain(); terrain_def_mod = TERRAIN_TYPES[curr_terrain]["defense_mod"]
            amount *= (1.0 - terrain_def_mod)
            if self.tank_aura_timer > 0: amount *= 0.85
            if self.armor_break_timer > 0: amount *= 1.25
            if self.polymorph_timer > 0: amount *= 1.5

        self.health -= amount
        if not is_env: self.energy = min(self.max_energy, self.energy + 5)
        if self.is_hidden: self.is_hidden = False; self.setOpacity(1.0)
        
        if self.unit_type == "paladin" and attacker and not is_env and amount > 0:
            attacker.take_damage(amount * 0.15, is_env=True)
        if attacker and not is_env:
            self.add_threat(attacker, amount * 2)
            if self.team == "red": self.scene_ref.team_blue_ult = min(100, self.scene_ref.team_blue_ult + amount * 0.05)
            else: self.scene_ref.team_red_ult = min(100, self.scene_ref.team_red_ult + amount * 0.05)
            
        self.text_item.setDefaultTextColor(QColor(255, 255, 255)); self.hit_flash_timer = 100
        if amount > 0:
            txt = f"-{int(amount)}"
            if is_crit: txt = f"CRIT {txt}!"
            color = QColor(255, 50, 50) if is_crit else QColor(255, 255, 255)
            self.scene_ref.add_combat_text(self.x(), self.y(), txt, color)
            
        if self.health <= 0:
            self.health = 0; self.death_timer = 0
            self.text_item.setPlainText("💀"); self.text_item.setDefaultTextColor(QColor(100, 100, 100))
            self.scene_ref.add_effect(self.x(), self.y(), "💥", size=20)
            if self.is_bear: self.max_health -= 200 
            if attacker: 
                self.kill_feed_cb(attacker.emoji, self.emoji)
                if not self.is_minion:
                    attacker.kills += 1
                    if attacker.team == "red": self.scene_ref.team_red_ult = min(100, self.scene_ref.team_red_ult + 15)
                    else: self.scene_ref.team_blue_ult = min(100, self.scene_ref.team_blue_ult + 15)
                    
                    if attacker.kills == 3:
                        attacker.scene_ref.add_combat_text(attacker.x(), attacker.y(), "SLAYER!", QColor(255, 100, 0))
                        attacker.setScale(1.2)
                    elif attacker.kills == 6:
                        attacker.scene_ref.add_combat_text(attacker.x(), attacker.y(), "RAMPAGE!", QColor(255, 0, 0))
                        attacker.setScale(1.5)
            elif is_env:
                env_emoji = TERRAIN_TYPES[self.get_current_terrain()]["emojis"][0]
                self.kill_feed_cb(env_emoji, self.emoji)

    def update_health_visual(self):
        health_percent = self.health / self.max_health
        self.health_bar.setRect(-15, 12, 30 * health_percent, 4)
        if self.rampage_timer > 0: self.health_bar.setBrush(QBrush(QColor(255, 0, 0)))
        elif self.divine_shield_timer > 0: self.health_bar.setBrush(QBrush(QColor(255, 215, 0)))
        elif self.buff_timer > 0: self.health_bar.setBrush(QBrush(QColor(255, 215, 0)))
        elif self.shield_hp > 0: self.health_bar.setBrush(QBrush(QColor(0, 150, 255)))
        elif self.is_healer: self.health_bar.setBrush(QBrush(QColor(0, 255, 255)))
        elif health_percent > 0.5: self.health_bar.setBrush(QBrush(QColor(0, 200, 0)))
        elif health_percent > 0.25: self.health_bar.setBrush(QBrush(QColor(255, 165, 0)))
        else: self.health_bar.setBrush(QBrush(QColor(255, 0, 0)))

    def update_status_visuals(self):
        status_text = ""
        if self.divine_shield_timer > 0: status_text += STATUS_ICONS["SHIELD"]
        if self.is_bear: status_text += STATUS_ICONS["BEAR"]
        if self.stun_timer > 0: status_text += STATUS_ICONS["STUN"]
        if self.poison_timer > 0: status_text += STATUS_ICONS["POISON"]
        if self.armor_break_timer > 0: status_text += STATUS_ICONS["ARMOR_BREAK"]
        if self.burn_timer > 0: status_text += STATUS_ICONS["BURN"]
        if self.taunt_timer > 0: status_text += "💢"
        if self.polymorph_timer > 0: status_text += "🐑"
        if self.charm_timer > 0: status_text += STATUS_ICONS["CHARM"]
        if self.overclock_timer > 0: status_text += STATUS_ICONS["OVERCLOCK"]
        if self.rage_timer > 0: status_text += STATUS_ICONS["RAGE"]
        self.status_icon.setPlainText(status_text)

    def update_debug_visuals(self):
        if self._target_line and self._target_line.scene(): self.scene().removeItem(self._target_line)
        self._target_line = None
        if self.scene_ref.show_debug and self.target and not self.target.is_dead():
            self._target_line = QGraphicsLineItem(QLineF(self.pos(), self.target.pos()))
            self._target_line.setPen(QPen(QColor(255, 0, 0), 1, Qt.PenStyle.DashLine))
            self._target_line.setZValue(0.5); self.scene().addItem(self._target_line)

    def is_dead(self): return self.health <= 0

class BattleSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nexus & Alchemist AI Battle Simulator V18")
        self.resize(1100, 800)

        self.terrain = [["grass" for _ in range(GRID_W)] for _ in range(GRID_H)]
        self.editing_map = False; self.mirror_editing = True; self.show_debug = False
        self._terrain_cache_dirty = True

        central_widget = QWidget(); self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        self.scene = CustomScene(simulator=self)
        self.scene.setSceneRect(0, 0, SCENE_WIDTH, SCENE_HEIGHT)
        self.scene.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.scene.terrain = self.terrain
        
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(self.view.renderHints().Antialiasing)
        self.view.mousePressEvent = self.handle_map_click
        main_layout.addWidget(self.view, stretch=3)

        self.weather_overlay = QGraphicsRectItem(0, 0, SCENE_WIDTH, SCENE_HEIGHT)
        self.weather_overlay.setPen(QPen(Qt.PenStyle.NoPen))
        self.weather_overlay.setBrush(QBrush(QColor(0, 0, 0, 0)))
        self.weather_overlay.setZValue(5) 
        self.scene.addItem(self.weather_overlay)
        
        self.night_overlay = QGraphicsRectItem(0, 0, SCENE_WIDTH, SCENE_HEIGHT)
        self.night_overlay.setPen(QPen(Qt.PenStyle.NoPen))
        self.night_overlay.setBrush(QBrush(QColor(0, 0, 50, 0)))
        self.night_overlay.setZValue(4) 
        self.scene.addItem(self.night_overlay)

        right_widget = QWidget(); right_layout = QVBoxLayout(right_widget)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.addWidget(right_widget, stretch=1)

        legend_label = QLabel("V18 Features:\n"
                              "🌙 Day/Night Cycle: Assassins & Vampires buffed at night\n"
                              "📦 Supply Crates: Units gather crates for buffs\n"
                              "🏯 Nexus: Spawns minions, destroying it causes a rout\n"
                              "⚗️ Alchemist: AoE potions, buffs, and debuffs\n\n"
                              "Classes:\n"
                              "🐉 Tank / 🐺 Warrior / 🏹 Archer\n"
                              "🔮 Mage / 🥷 Assassin / 🪓 Berserker\n"
                              "👑 Commander / 🧟 Necromancer / 🤴 Paladin\n"
                              "🌳 Druid / 🧛‍♂️ Vampire / 🤖 Tinkerer / ⚗️ Alchemist / 🧙 Healer")
        legend_label.setStyleSheet("font-size: 12px; padding: 5px; border: 1px solid #ccc; border-radius: 5px;")
        right_layout.addWidget(legend_label)

        self.time_label = QLabel("Time: ☀️ Day")
        self.time_label.setStyleSheet("font-size: 14px; font-weight: bold; color: orange;")
        right_layout.addWidget(self.time_label)
        
        self.weather_label = QLabel("Weather: ☀️ Clear")
        self.weather_label.setStyleSheet("font-size: 14px; font-weight: bold; color: blue;")
        right_layout.addWidget(self.weather_label)

        self.size_label = QLabel("Army Size per Team: 15")
        right_layout.addWidget(self.size_label)
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(5, 40); self.size_slider.setValue(15)
        self.size_slider.valueChanged.connect(self.update_size_label)
        right_layout.addWidget(self.size_slider)

        self.speed_label = QLabel("Simulation Speed: 1x")
        right_layout.addWidget(self.speed_label)
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 10); self.speed_slider.setValue(1)
        self.speed_slider.valueChanged.connect(self.update_speed_label)
        right_layout.addWidget(self.speed_slider)

        self.map_edit_btn = QPushButton("Enable Map Editing (Off)")
        self.map_edit_btn.clicked.connect(self.toggle_map_editing)
        right_layout.addWidget(self.map_edit_btn)
        
        self.clear_map_btn = QPushButton("Clear All Obstacles")
        self.clear_map_btn.clicked.connect(self.clear_map)
        right_layout.addWidget(self.clear_map_btn)

        map_btn_layout = QHBoxLayout()
        self.tactical_btn = QPushButton("Tactical Map"); self.tactical_btn.clicked.connect(self.generate_tactical_map)
        map_btn_layout.addWidget(self.tactical_btn)
        self.biome_btn = QPushButton("Biome Map"); self.biome_btn.clicked.connect(self.generate_biome_map)
        map_btn_layout.addWidget(self.biome_btn)
        self.choke_btn = QPushButton("Chokepoint Map"); self.choke_btn.clicked.connect(self.generate_chokepoint_map)
        map_btn_layout.addWidget(self.choke_btn)
        right_layout.addLayout(map_btn_layout)

        self.mirror_chk = QCheckBox("Mirror Map Editing"); self.mirror_chk.setChecked(True)
        self.mirror_chk.stateChanged.connect(self.toggle_mirror)
        right_layout.addWidget(self.mirror_chk)

        self.debug_chk = QCheckBox("Show Debug Targets"); self.debug_chk.stateChanged.connect(self.toggle_debug)
        right_layout.addWidget(self.debug_chk)

        self.start_btn = QPushButton("Start Battle"); self.start_btn.clicked.connect(self.start_battle)
        right_layout.addWidget(self.start_btn)
        self.reset_btn = QPushButton("Reset / Spawn Armies"); self.reset_btn.clicked.connect(self.spawn_armies)
        right_layout.addWidget(self.reset_btn)

        ult_layout = QHBoxLayout()
        red_ult_widget = QWidget(); red_ult_layout = QVBoxLayout(red_ult_widget)
        red_ult_layout.addWidget(QLabel("<b>Red Team Ult</b>"))
        self.red_ult_bar = QProgressBar(); self.red_ult_bar.setMaximum(100); self.red_ult_bar.setValue(0)
        self.red_ult_bar.setStyleSheet("QProgressBar::chunk { background-color: #ff0000; }")
        red_ult_layout.addWidget(self.red_ult_bar)
        ult_layout.addWidget(red_ult_widget)
        
        blue_ult_widget = QWidget(); blue_ult_layout = QVBoxLayout(blue_ult_widget)
        blue_ult_layout.addWidget(QLabel("<b>Blue Team Ult</b>"))
        self.blue_ult_bar = QProgressBar(); self.blue_ult_bar.setMaximum(100); self.blue_ult_bar.setValue(0)
        self.blue_ult_bar.setStyleSheet("QProgressBar::chunk { background-color: #0000ff; }")
        blue_ult_layout.addWidget(self.blue_ult_bar)
        ult_layout.addWidget(blue_ult_widget)
        right_layout.addLayout(ult_layout)

        self.status_label = QLabel("Red Team: 0 | Blue Team: 0")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        right_layout.addWidget(self.status_label)
        self.winner_label = QLabel(""); self.winner_label.setStyleSheet("font-size: 20px; font-weight: bold; color: green;")
        right_layout.addWidget(self.winner_label)
        
        right_layout.addWidget(QLabel("<b>Kill Feed</b>"))
        self.kill_feed_label = QLabel(""); self.kill_feed_label.setStyleSheet("font-size: 14px; color: #333;")
        right_layout.addWidget(self.kill_feed_label)

        self.team_red = []; self.team_blue = []
        self.battle_active = False
        self.timer = QTimer(); self.timer.timeout.connect(self.game_loop)
        self.elapsed_time = 0; self.kill_feed_history = []
        self.crate_spawn_timer = 20000

        self.pathfinder = DStar(GRID_W, GRID_H, lambda x, y: TERRAIN_TYPES[self.terrain[y][x]]["walkable"])
        self.generate_tactical_map(); self.spawn_armies()

    def update_size_label(self, value): self.size_label.setText(f"Army Size per Team: {value}")
    def update_speed_label(self, value):
        self.speed_label.setText(f"Simulation Speed: {value}x")
        if self.battle_active: self.timer.start(int(16 / value))

    def toggle_debug(self, state):
        self.show_debug = (state == Qt.CheckState.Checked.value); self.scene.show_debug = self.show_debug
        if not self.show_debug:
            for u in self.team_red + self.team_blue:
                if u._target_line and u._target_line.scene(): self.scene.removeItem(u._target_line)
                u._target_line = None

    def toggle_mirror(self, state): self.mirror_editing = (state == Qt.CheckState.Checked.value)
    def toggle_map_editing(self):
        self.editing_map = not self.editing_map
        state = "On" if self.editing_map else "Off"
        self.map_edit_btn.setText(f"Enable Map Editing ({state})")
        if self.editing_map:
            self.battle_active = False; self.timer.stop(); self.start_btn.setText("Start Battle")

    def clear_map(self):
        for y in range(GRID_H):
            for x in range(GRID_W): self.set_terrain(x, y, "grass")
        self.scene.terrain_health.clear()
        self.update_cp_coords(); self.draw_map()

    def handle_map_click(self, event):
        if not self.editing_map: super(QGraphicsView, self.view).mousePressEvent(event); return
        pos = self.view.mapToScene(event.pos())
        gx, gy = int(pos.x() // TILE_SIZE), int(pos.y() // TILE_SIZE)
        if 0 <= gx < GRID_W and 0 <= gy < GRID_H:
            if event.button() == Qt.MouseButton.RightButton: new_t = "grass"
            else:
                types = list(TERRAIN_TYPES.keys())
                current_idx = types.index(self.terrain[gy][gx])
                new_t = types[(current_idx + 1) % len(types)]
            self.set_terrain(gx, gy, new_t)
            if self.mirror_editing: self.set_terrain(GRID_W - 1 - gx, gy, new_t)
            self.update_cp_coords(); self.draw_map()

    def set_terrain(self, x, y, t_type):
        self.terrain[y][x] = t_type
        if TERRAIN_TYPES[t_type]["hp"] > 0:
            self.scene.terrain_health[(x, y)] = TERRAIN_TYPES[t_type]["hp"]
        else:
            self.scene.terrain_health.pop((x, y), None)
        self._terrain_cache_dirty = True
        if hasattr(self, "_tiles"):
            self.refresh_tile(x, y)

    def _rebuild_terrain_cache(self):
        self._terrain_positions = {}
        for y in range(GRID_H):
            for x in range(GRID_W):
                self._terrain_positions.setdefault(self.terrain[y][x], []).append(
                    (x * TILE_SIZE + TILE_SIZE/2, y * TILE_SIZE + TILE_SIZE/2))
        self._terrain_cache_dirty = False

    def get_terrain_positions(self, t_type):
        if self._terrain_cache_dirty:
            self._rebuild_terrain_cache()
        return self._terrain_positions.get(t_type, [])

    def update_cp_coords(self):
        self.scene.cp_coords = []
        for y in range(GRID_H):
            for x in range(GRID_W):
                if self.terrain[y][x] == "capture_point":
                    self.scene.cp_coords.append((x * TILE_SIZE + TILE_SIZE/2, y * TILE_SIZE + TILE_SIZE/2))

    def generate_tactical_map(self):
        for y in range(GRID_H):
            for x in range(GRID_W): self.set_terrain(x, y, "grass")
        for _ in range(8):
            cx = random.randint(2, GRID_W//2 - 2); cy = random.randint(2, GRID_H - 3)
            blob_size = random.randint(3, 6); terrain_choice = random.choice(["forest", "rock", "bush"])
            for _ in range(blob_size):
                nx = cx + random.randint(-2, 2); ny = cy + random.randint(-2, 2)
                if 0 <= nx < GRID_W//2 and 0 <= ny < GRID_H:
                    self.set_terrain(nx, ny, terrain_choice); self.set_terrain(GRID_W - 1 - nx, ny, terrain_choice)
        for y in range(GRID_H):
            lx1 = random.randint(1, 3); lx2 = GRID_W - 1 - random.randint(1, 3)
            self.set_terrain(lx1, y, "lava"); self.set_terrain(lx2, y, "lava")
        mid_x = GRID_W // 2
        for y in range(GRID_H//2 - 3, GRID_H//2 + 4):
            for x in range(mid_x - 2, mid_x + 3): self.set_terrain(x, y, "high_ground")
        self.set_terrain(4, GRID_H//2, "capture_point"); self.set_terrain(GRID_W - 5, GRID_H//2, "capture_point")
        self.set_terrain(mid_x, GRID_H//2, "capture_point")
        self.update_cp_coords(); self.draw_map()

    def generate_biome_map(self):
        mid_x, mid_y = GRID_W // 2, GRID_H // 2
        for y in range(GRID_H):
            for x in range(GRID_W):
                if   x <  mid_x and y <  mid_y: t = "swamp"
                elif x >= mid_x and y <  mid_y: t = "ice"
                elif x <  mid_x and y >= mid_y: t = "forest"
                else:                           t = "lava"
                self.set_terrain(x, y, t)
        for _ in range(30):
            fx = random.randint(0, mid_x - 1)
            fy = random.randint(0, GRID_H - 1)
            self.set_terrain(fx, fy, "grass")
            self.set_terrain(GRID_W - 1 - fx, fy, "grass")
        for x in range(GRID_W): self.set_terrain(x, mid_y, "road")
        for y in range(GRID_H): self.set_terrain(mid_x, y, "road")
        self.set_terrain(mid_x, mid_y, "sanctuary")
        self.update_cp_coords(); self.draw_map()

    def generate_chokepoint_map(self):
        for y in range(GRID_H):
            for x in range(GRID_W): self.set_terrain(x, y, "grass")
        gaps_y = [GRID_H//4, GRID_H//2, 3*GRID_H//4]; wall_xs = [GRID_W//4, 3*GRID_W//4]
        for wx in wall_xs:
            for y in range(GRID_H):
                if y not in gaps_y:
                    self.set_terrain(wx, y, "water" if y % 2 == 0 else "rock")
                    self.set_terrain(wx+1, y, "water" if y % 2 == 0 else "rock")
        for gap_y in gaps_y:
            self.set_terrain(GRID_W//4, gap_y, "capture_point"); self.set_terrain(3*GRID_W//4, gap_y, "capture_point")
        for _ in range(10):
            bx = random.choice([random.randint(2, GRID_W//4-2), random.randint(GRID_W//4+2, 3*GRID_W//4-2), random.randint(3*GRID_W//4+2, GRID_W-3)])
            by = random.randint(2, GRID_H-3); self.set_terrain(bx, by, "bush")
        self.update_cp_coords(); self.draw_map()

    def _build_tile_layer(self):
        if hasattr(self, "_tiles"):
            for bg, txt in self._tiles.values():
                self.scene.removeItem(bg)
                self.scene.removeItem(txt)
        self._tiles = {}
        font = QFont(); font.setPointSize(14)
        for y in range(GRID_H):
            for x in range(GRID_W):
                bg = QGraphicsRectItem(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                bg.setPen(Qt.PenStyle.NoPen); bg.setZValue(-2)
                self.scene.addItem(bg)
                txt = QGraphicsTextItem(); txt.setFont(font); txt.setZValue(-1)
                self.scene.addItem(txt)
                self._tiles[(x, y)] = (bg, txt)

    def refresh_tile(self, x, y):
        if not hasattr(self, "_tiles") or (x, y) not in self._tiles:
            return
        bg, txt = self._tiles[(x, y)]
        t_type = self.terrain[y][x]; t_data = TERRAIN_TYPES[t_type]
        bg.setBrush(QBrush(t_data["bg_color"]))
        emoji = random.choice(t_data["emojis"])
        if (x, y) in self.scene.terrain_health and self.scene.terrain_health[(x, y)] < t_data["hp"]:
            if t_type == "forest": emoji = "🍂"
            elif t_type == "rock": emoji = "🪨"
            elif t_type == "bush": emoji = "🍂"
        txt.setPlainText(emoji)
        r = txt.boundingRect()
        txt.setPos(x * TILE_SIZE + (TILE_SIZE - r.width())/2,
                   y * TILE_SIZE + (TILE_SIZE - r.height())/2)

    def draw_map(self):
        if not hasattr(self, "_tiles"):
            self._build_tile_layer()
        for y in range(GRID_H):
            for x in range(GRID_W):
                self.refresh_tile(x, y)

    def spawn_unit(self, x, y, team, unit_type):
        unit = Unit(x, y, team, unit_type, self.pathfinder, self.scene, self.add_to_kill_feed, self.spawn_unit)
        if team == "red": self.team_red.append(unit)
        else: self.team_blue.append(unit)
        self.scene.addItem(unit)
        return unit

    def spawn_armies(self):
        self.timer.stop(); self.battle_active = False
        for item in self.scene.items():
            if isinstance(item, Unit) or isinstance(item, QGraphicsLineItem) or isinstance(item, Meteor) or isinstance(item, Crate):
                self.scene.removeItem(item)
        self.scene.projectiles.clear(); self.scene.hazards.clear(); self.scene.crates.clear()
        self.team_red.clear(); self.team_blue.clear()
        self.scene.team_red_ult = 0; self.scene.team_blue_ult = 0
        self.scene.team_red_ult_active_timer = 0; self.scene.team_blue_ult_active_timer = 0
        self.winner_label.setText(""); self.kill_feed_history.clear(); self.update_kill_feed()
        self.draw_map()
        army_size = self.size_slider.value()
        unit_types = [k for k in UNIT_TYPES.keys() if k not in ["minion", "bat", "turret", "ward", "nexus"]]
        self.scene.team_red_initial_size = army_size
        self.scene.team_blue_initial_size = army_size

        self.scene.nexus_red = self.spawn_unit(20, SCENE_HEIGHT/2, "red", "nexus")
        self.scene.nexus_blue = self.spawn_unit(SCENE_WIDTH-20, SCENE_HEIGHT/2, "blue", "nexus")

        for _ in range(army_size):
            while True:
                gx, gy = random.randint(0, GRID_W//4), random.randint(0, GRID_H-1)
                if TERRAIN_TYPES[self.terrain[gy][gx]]["walkable"]: x, y = gx * TILE_SIZE + TILE_SIZE/2, gy * TILE_SIZE + TILE_SIZE/2; break
            ut = random.choice(unit_types)
            self.spawn_unit(x, y, "red", ut)

        for _ in range(army_size):
            while True:
                gx, gy = random.randint(GRID_W - GRID_W//4, GRID_W-1), random.randint(0, GRID_H-1)
                if TERRAIN_TYPES[self.terrain[gy][gx]]["walkable"]: x, y = gx * TILE_SIZE + TILE_SIZE/2, gy * TILE_SIZE + TILE_SIZE/2; break
            ut = random.choice(unit_types)
            self.spawn_unit(x, y, "blue", ut)
            
        self.update_status(); self.start_btn.setText("Start Battle")

    def start_battle(self):
        if not self.battle_active:
            self.battle_active = True; self.elapsed_time = 0
            speed = self.speed_slider.value(); self.timer.start(int(16 / speed))
            self.start_btn.setText("Pause Battle")
        else:
            self.battle_active = False; self.timer.stop(); self.start_btn.setText("Resume Battle")

    def cast_team_ultimate(self, team):
        if team == "red":
            self.scene.team_red_ult = 0; self.scene.team_red_ult_active_timer = 10000
            self.scene.add_effect(SCENE_WIDTH/4, 50, "🩸", lifespan=2000, size=32)
            for u in self.team_red:
                if not u.is_dead() and not u.is_minion:
                    u.buff_timer = max(u.buff_timer, 10000)
                    if not hasattr(u, "_saved_lifesteal"):
                        u._saved_lifesteal = u.lifesteal
                    u.lifesteal = max(u.lifesteal, 0.5)
                    u.scene_ref.add_combat_text(u.x(), u.y(), "BLOODLUST!", QColor(255, 0, 0))
        else:
            self.scene.team_blue_ult = 0; self.scene.team_blue_ult_active_timer = 10000
            self.scene.add_effect(3*SCENE_WIDTH/4, 50, "🛡️", lifespan=2000, size=32)
            for u in self.team_blue:
                if not u.is_dead() and not u.is_minion:
                    u.buff_timer = max(u.buff_timer, 10000)
                    u.shield_hp = max(u.shield_hp, 200)
                    u.scene_ref.add_combat_text(u.x(), u.y(), "AEGIS!", QColor(0, 150, 255))

    def game_loop(self):
        if not self.battle_active: return
        dt = self.timer.interval(); self.elapsed_time += dt; current_time = self.elapsed_time

        active_projectiles = [p for p in self.scene.projectiles if p.tick()]
        self.scene.projectiles = active_projectiles

        active_texts = [t for t in self.scene.combat_texts if t.tick(dt)]
        self.scene.combat_texts = active_texts
        
        active_effects = [e for e in self.scene.effects if e.tick(dt)]
        self.scene.effects = active_effects
        
        active_hazards = [hz for hz in self.scene.hazards if hz.tick(dt)]
        self.scene.hazards = active_hazards
        
        active_crates = [c for c in self.scene.crates if c.tick(dt)]
        self.scene.crates = active_crates
        
        self.crate_spawn_timer -= dt
        if self.crate_spawn_timer <= 0 and len(self.scene.crates) < 3:
            self.crate_spawn_timer = 20000
            while True:
                gx, gy = random.randint(2, GRID_W-3), random.randint(2, GRID_H-3)
                if TERRAIN_TYPES[self.terrain[gy][gx]]["walkable"]:
                    cx, cy = gx * TILE_SIZE + TILE_SIZE/2, gy * TILE_SIZE + TILE_SIZE/2
                    crate = Crate(cx, cy); crate.setZValue(3)
                    self.scene.addItem(crate); self.scene.crates.append(crate)
                    break

        self.scene.weather_timer -= dt
        if self.scene.weather_timer <= 0:
            self.scene.weather = random.choice(["CLEAR", "RAIN", "FOG", "METEOR"])
            self.scene.weather_timer = 30000
            self.scene.meteor_timer = 2000
            self.update_weather_ui()
            
        if self.scene.weather == "METEOR":
            self.scene.meteor_timer -= dt
            if self.scene.meteor_timer <= 0:
                self.scene.meteor_timer = 1500
                mx, my = random.uniform(50, SCENE_WIDTH-50), random.uniform(50, SCENE_HEIGHT-50)
                meteor = Meteor(mx, my); meteor.setZValue(4)
                self.scene.addItem(meteor); self.scene.hazards.append(meteor)

        self.scene.time_of_day = (self.elapsed_time % 60000) / 60000
        is_night = self.scene.time_of_day > 0.5
        if is_night != self.scene.is_night:
            self.scene.is_night = is_night
            self.update_time_ui()
        alpha = 0.0
        if 0.4 < self.scene.time_of_day < 0.6:
            alpha = 1.0 - (abs(self.scene.time_of_day - 0.5) * 2.0)
        elif self.scene.time_of_day >= 0.6:
            alpha = 1.0
        self.night_overlay.setBrush(QBrush(QColor(0, 0, 50, int(120 * alpha))))

        self.scene.commander_in_danger = any(
            not u.is_dead() and u.health / u.max_health < 0.5
            for u in self.team_red + self.team_blue if u.unit_type == "commander"
        )

        for unit in self.team_red:
            if not unit.is_dead(): unit.update_ai(self.team_blue, self.team_red, current_time, dt)
        for unit in self.team_blue:
            if not unit.is_dead(): unit.update_ai(self.team_red, self.team_blue, current_time, dt)

        self.cleanup_dead(); self.update_status()

        self.red_ult_bar.setValue(int(self.scene.team_red_ult))
        self.blue_ult_bar.setValue(int(self.scene.team_blue_ult))
        if self.scene.team_red_ult >= 100: self.cast_team_ultimate("red")
        if self.scene.team_blue_ult >= 100: self.cast_team_ultimate("blue")
        
        if self.scene.team_red_ult_active_timer > 0:
            self.scene.team_red_ult_active_timer -= dt
            if self.scene.team_red_ult_active_timer <= 0:
                for u in self.team_red:
                    if hasattr(u, "_saved_lifesteal"):
                        u.lifesteal = u._saved_lifesteal
                        del u._saved_lifesteal
        if self.scene.team_blue_ult_active_timer > 0:
            self.scene.team_blue_ult_active_timer -= dt

        red_alive = len([u for u in self.team_red if not u.is_dead() and not u.is_minion and u.unit_type not in ["turret", "ward", "bat", "nexus"]])
        blue_alive = len([u for u in self.team_blue if not u.is_dead() and not u.is_minion and u.unit_type not in ["turret", "ward", "bat", "nexus"]])
        
        nexus_red_dead = self.scene.nexus_red and self.scene.nexus_red.is_dead()
        nexus_blue_dead = self.scene.nexus_blue and self.scene.nexus_blue.is_dead()
        
        if nexus_red_dead: self.scene.team_red_routing = True
        if nexus_blue_dead: self.scene.team_blue_routing = True
        
        self.scene.team_red_routing = self.scene.team_red_routing or (red_alive < self.scene.team_red_initial_size * 0.3)
        self.scene.team_blue_routing = self.scene.team_blue_routing or (blue_alive < self.scene.team_blue_initial_size * 0.3)

        if nexus_red_dead or nexus_blue_dead:
            self.timer.stop(); self.battle_active = False; self.start_btn.setText("Start Battle")
            if nexus_red_dead and nexus_blue_dead: self.winner_label.setText("It's a Draw!")
            elif nexus_red_dead: self.winner_label.setText("Blue Team Wins (Nexus Destroyed)!"); self.winner_label.setStyleSheet("color: blue;")
            else: self.winner_label.setText("Red Team Wins (Nexus Destroyed)!"); self.winner_label.setStyleSheet("color: red;")
        elif red_alive == 0 or blue_alive == 0:
            self.timer.stop(); self.battle_active = False; self.start_btn.setText("Start Battle")
            if red_alive == 0 and blue_alive == 0: self.winner_label.setText("It's a Draw!")
            elif red_alive == 0: self.winner_label.setText("Blue Team Wins!"); self.winner_label.setStyleSheet("color: blue;")
            else: self.winner_label.setText("Red Team Wins!"); self.winner_label.setStyleSheet("color: red;")

    def update_time_ui(self):
        self.time_label.setText("Time: 🌙 Night" if self.scene.is_night else "Time: ☀️ Day")

    def update_weather_ui(self):
        w = self.scene.weather
        if w == "CLEAR":
            self.weather_label.setText("Weather: ☀️ Clear")
            self.weather_overlay.setBrush(QBrush(QColor(0, 0, 0, 0)))
        elif w == "RAIN":
            self.weather_label.setText("Weather: 🌧️ Rain (-Speed, Extinguishes Fire)")
            self.weather_overlay.setBrush(QBrush(QColor(0, 100, 255, 40)))
        elif w == "FOG":
            self.weather_label.setText("Weather: 🌫️ Fog (-50% Vision)")
            self.weather_overlay.setBrush(QBrush(QColor(200, 200, 200, 80)))
        elif w == "METEOR":
            self.weather_label.setText("Weather: ☄️ Meteor Storm! (Take Cover!)")
            self.weather_overlay.setBrush(QBrush(QColor(255, 100, 0, 40)))

    def cleanup_dead(self):
        dead_red = [u for u in self.team_red if u.is_dead() and u.death_timer > 6000]
        dead_blue = [u for u in self.team_blue if u.is_dead() and u.death_timer > 6000]
        for u in dead_red: self.scene.removeItem(u); self.team_red.remove(u)
        for u in dead_blue: self.scene.removeItem(u); self.team_blue.remove(u)

    def update_status(self):
        red_count = len([u for u in self.team_red if not u.is_dead() and not u.is_minion and u.unit_type not in ["turret", "ward", "bat", "nexus"]])
        blue_count = len([u for u in self.team_blue if not u.is_dead() and not u.is_minion and u.unit_type not in ["turret", "ward", "bat", "nexus"]])
        self.status_label.setText(f"Red Team: {red_count} | Blue Team: {blue_count}")
        
    def add_to_kill_feed(self, killer_emoji, victim_emoji):
        self.kill_feed_history.insert(0, f"{killer_emoji}  >  {victim_emoji}")
        if len(self.kill_feed_history) > 5: self.kill_feed_history.pop()
        self.update_kill_feed()
        
    def update_kill_feed(self): self.kill_feed_label.setText("\n".join(self.kill_feed_history))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BattleSimulator()
    window.show()
    sys.exit(app.exec())