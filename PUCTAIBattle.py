import sys
import math
import random
import copy
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QTextEdit, QFrame, QSlider, QProgressBar)
from PySide6.QtCore import QTimer, Qt, QRectF, QLineF
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QBrush

# ==========================================
# 1. UNIT DEFINITIONS & STATS
# ==========================================
UNIT_TEMPLATES = {
    'Warrior':    {'emoji': '🤖', 'hp': 6,  'dmg': 2, 'rng': 1, 'arm': 1, 'res': 0, 'spd': 1, 'max_ap': 2, 'atk_cost': 1, 'mov_cost': 1, 'atk_type': 'P', 'crit': 0.1, 'dodge': 0.1, 'behaviors': ['Berserker', 'Counter', 'Vanguard', 'Attack of Opportunity']},
    'Archer':     {'emoji': '🏹', 'hp': 4,  'dmg': 2, 'rng': 3, 'arm': 0, 'res': 0, 'spd': 1, 'max_ap': 2, 'atk_cost': 1, 'mov_cost': 1, 'atk_type': 'P', 'crit': 0.2, 'dodge': 0.2, 'behaviors': ['Pierce']},
    'Tank':       {'emoji': '🛡️', 'hp': 12, 'dmg': 1, 'rng': 1, 'arm': 3, 'res': 1, 'spd': 1, 'max_ap': 1, 'atk_cost': 1, 'mov_cost': 1, 'atk_type': 'P', 'crit': 0.0, 'dodge': 0.0, 'behaviors': ['Unyielding', 'Guardian', 'Bulwark'], 'aura': {'arm': 2}},
    'Mage':       {'emoji': '🧙', 'hp': 4,  'dmg': 4, 'rng': 2, 'arm': 0, 'res': 0, 'spd': 1, 'max_ap': 2, 'atk_cost': 2, 'mov_cost': 1, 'atk_type': 'M', 'crit': 0.1, 'dodge': 0.1, 'behaviors': []},
    'Assassin':   {'emoji': '🦹', 'hp': 4,  'dmg': 3, 'rng': 1, 'arm': 0, 'res': 0, 'spd': 2, 'max_ap': 2, 'atk_cost': 1, 'mov_cost': 1, 'atk_type': 'P', 'crit': 0.4, 'dodge': 0.3, 'behaviors': ['Flanker', 'Executioner', 'Riposte', 'Swarm']},
    'Cleric':     {'emoji': '⚗️', 'hp': 5,  'dmg': 1, 'rng': 2, 'arm': 0, 'res': 2, 'spd': 1, 'max_ap': 2, 'atk_cost': 1, 'mov_cost': 1, 'atk_type': 'M', 'crit': 0.0, 'dodge': 0.1, 'heal': 4, 'behaviors': ['Purify'], 'aura': {'dodge': 0.05}},
    'Necromancer':{'emoji': '🧟', 'hp': 4,  'dmg': 1, 'rng': 2, 'arm': 0, 'res': 1, 'spd': 1, 'max_ap': 2, 'atk_cost': 1, 'mov_cost': 1, 'atk_type': 'M', 'crit': 0.1, 'dodge': 0.1, 'poison': 2, 'behaviors': ['Life Steal', 'Bloodlust']},
    'Paladin':    {'emoji': '⚔️', 'hp': 8,  'dmg': 2, 'rng': 1, 'arm': 2, 'res': 2, 'spd': 1, 'max_ap': 2, 'atk_cost': 1, 'mov_cost': 1, 'atk_type': 'P', 'crit': 0.1, 'dodge': 0.0, 'self_heal': 2, 'behaviors': ['Counter'], 'aura': {'res': 1, 'dodge': 0.05}},
    'Sniper':     {'emoji': '🎯', 'hp': 3,  'dmg': 3, 'rng': 5, 'arm': 0, 'res': 0, 'spd': 1, 'max_ap': 2, 'atk_cost': 2, 'mov_cost': 1, 'atk_type': 'P', 'crit': 0.3, 'dodge': 0.1, 'min_rng': 2, 'behaviors': ['Eagle Eye', 'Overwatch', 'Pierce']},
    'Cannoneer':  {'emoji': '🎆', 'hp': 5,  'dmg': 2, 'rng': 3, 'arm': 1, 'res': 0, 'spd': 1, 'max_ap': 1, 'atk_cost': 1, 'mov_cost': 1, 'atk_type': 'P', 'crit': 0.0, 'dodge': 0.0, 'splash': 1, 'behaviors': ['Siege Breaker', 'Executioner']},
    'Vampire':    {'emoji': '🦇', 'hp': 6,  'dmg': 2, 'rng': 1, 'arm': 0, 'res': 1, 'spd': 2, 'max_ap': 2, 'atk_cost': 1, 'mov_cost': 1, 'atk_type': 'P', 'crit': 0.1, 'dodge': 0.2, 'behaviors': ['Flying', 'Bloodthirst', 'Counter']},
    'Samurai':    {'emoji': '⚔️', 'hp': 5,  'dmg': 3, 'rng': 1, 'arm': 1, 'res': 0, 'spd': 2, 'max_ap': 2, 'atk_cost': 2, 'mov_cost': 1, 'atk_type': 'P', 'crit': 0.2, 'dodge': 0.2, 'behaviors': ['Iaido', 'Bladestorm']},
    'Sapper':     {'emoji': '🧨', 'hp': 4,  'dmg': 2, 'rng': 1, 'arm': 0, 'res': 0, 'spd': 1, 'max_ap': 2, 'atk_cost': 1, 'mov_cost': 1, 'atk_type': 'P', 'crit': 0.0, 'dodge': 0.0, 'behaviors': ['Martyr', 'Demolition']},
    'Fairy':      {'emoji': '🧚', 'hp': 4,  'dmg': 0, 'rng': 2, 'arm': 0, 'res': 2, 'spd': 2, 'max_ap': 2, 'atk_cost': 1, 'mov_cost': 1, 'atk_type': 'M', 'crit': 0.0, 'dodge': 0.4, 'heal': 3, 'behaviors': ['Graceful', 'Regen', 'Benediction']},
    'Golem':      {'emoji': '🗿', 'hp': 15, 'dmg': 2, 'rng': 1, 'arm': 2, 'res': 5, 'spd': 1, 'max_ap': 1, 'atk_cost': 1, 'mov_cost': 1, 'atk_type': 'P', 'crit': 0.0, 'dodge': 0.0, 'behaviors': ['Construct', 'Taunt', 'Unyielding']},
    'Witch':      {'emoji': '🧙‍♀️', 'hp': 5,  'dmg': 2, 'rng': 2, 'arm': 0, 'res': 1, 'spd': 1, 'max_ap': 2, 'atk_cost': 1, 'mov_cost': 1, 'atk_type': 'M', 'crit': 0.1, 'dodge': 0.2, 'behaviors': ['Hex']},
    'Barbarian':  {'emoji': '🪓', 'hp': 8,  'dmg': 3, 'rng': 1, 'arm': 0, 'res': 0, 'spd': 1, 'max_ap': 2, 'atk_cost': 1, 'mov_cost': 1, 'atk_type': 'P', 'crit': 0.2, 'dodge': 0.1, 'behaviors': ['Reckless', 'Cleave']},
    'Dragon':     {'emoji': '🐉', 'hp': 10, 'dmg': 3, 'rng': 3, 'arm': 2, 'res': 2, 'spd': 2, 'max_ap': 2, 'atk_cost': 2, 'mov_cost': 1, 'atk_type': 'M', 'crit': 0.1, 'dodge': 0.1, 'behaviors': ['Flying', 'Breath', 'Colossal', 'Terrify']},
    'Genie':      {'emoji': '🧞', 'hp': 5,  'dmg': 3, 'rng': 2, 'arm': 0, 'res': 3, 'spd': 2, 'max_ap': 3, 'atk_cost': 3, 'mov_cost': 1, 'atk_type': 'M', 'crit': 0.2, 'dodge': 0.3, 'heal': 5, 'behaviors': ['Phasing', 'Wish']},
    'Commander':  {'emoji': '🚩', 'hp': 6,  'dmg': 2, 'rng': 1, 'arm': 2, 'res': 0, 'spd': 1, 'max_ap': 2, 'atk_cost': 1, 'mov_cost': 1, 'atk_type': 'P', 'crit': 0.1, 'dodge': 0.1, 'behaviors': ['Rally', 'Vanguard'], 'aura': {'arm': 1, 'dmg': 1}},
    'Jester':     {'emoji': '🤡', 'hp': 5,  'dmg': 2, 'rng': 1, 'arm': 1, 'res': 0, 'spd': 2, 'max_ap': 2, 'atk_cost': 1, 'mov_cost': 1, 'atk_type': 'P', 'crit': 0.3, 'dodge': 0.4, 'behaviors': ['Chaos', 'Agile']},
    'Scorpion':   {'emoji': '🦂', 'hp': 5,  'dmg': 2, 'rng': 2, 'arm': 1, 'res': 0, 'spd': 1, 'max_ap': 2, 'atk_cost': 1, 'mov_cost': 1, 'atk_type': 'P', 'crit': 0.1, 'dodge': 0.1, 'poison': 3, 'behaviors': ['Hook', 'Venom']},
    'Griffin':    {'emoji': '🦅', 'hp': 6,  'dmg': 2, 'rng': 1, 'arm': 1, 'res': 0, 'spd': 2, 'max_ap': 2, 'atk_cost': 1, 'mov_cost': 1, 'atk_type': 'P', 'crit': 0.2, 'dodge': 0.2, 'behaviors': ['Flying', 'Dive Bomb', 'Counter']},
    'Elf':        {'emoji': '🧝', 'hp': 4,  'dmg': 2, 'rng': 3, 'arm': 0, 'res': 0, 'spd': 1, 'max_ap': 2, 'atk_cost': 1, 'mov_cost': 1, 'atk_type': 'P', 'crit': 0.2, 'dodge': 0.3, 'behaviors': ['Multishot', 'Deflect']},
    'Centaur':    {'emoji': '🦌', 'hp': 5,  'dmg': 2, 'rng': 2, 'arm': 1, 'res': 0, 'spd': 2, 'max_ap': 2, 'atk_cost': 1, 'mov_cost': 1, 'atk_type': 'P', 'crit': 0.1, 'dodge': 0.2, 'behaviors': ['Hit and Run', 'Charge']},
    'Druid':      {'emoji': '🌿', 'hp': 5,  'dmg': 2, 'rng': 2, 'arm': 0, 'res': 2, 'spd': 1, 'max_ap': 2, 'atk_cost': 1, 'mov_cost': 1, 'atk_type': 'M', 'crit': 0.0, 'dodge': 0.2, 'heal': 3, 'behaviors': ['Entangle', "Nature's Blessing"]},
    'Lizardman':  {'emoji': '🦎', 'hp': 6,  'dmg': 2, 'rng': 1, 'arm': 1, 'res': 0, 'spd': 1, 'max_ap': 2, 'atk_cost': 1, 'mov_cost': 1, 'atk_type': 'P', 'crit': 0.1, 'dodge': 0.2, 'behaviors': ['Amphibious', 'Tongue Lash']},
    'Wraith':     {'emoji': '👻', 'hp': 4,  'dmg': 3, 'rng': 1, 'arm': 0, 'res': 2, 'spd': 2, 'max_ap': 2, 'atk_cost': 1, 'mov_cost': 1, 'atk_type': 'M', 'crit': 0.2, 'dodge': 0.3, 'behaviors': ['Incorporeal', 'Life Drain', 'Terrify']},
    'Duelist':    {'emoji': '🤺', 'hp': 5,  'dmg': 3, 'rng': 1, 'arm': 1, 'res': 0, 'spd': 2, 'max_ap': 2, 'atk_cost': 1, 'mov_cost': 1, 'atk_type': 'P', 'crit': 0.2, 'dodge': 0.3, 'behaviors': ['Lunge', 'Elegant', 'Attack of Opportunity']},
    
    # --- NEW UNITS ---
    'Chronomancer':{'emoji': '⏳', 'hp': 4,  'dmg': 1, 'rng': 2, 'arm': 0, 'res': 2, 'spd': 1, 'max_ap': 2, 'atk_cost': 1, 'mov_cost': 1, 'atk_type': 'M', 'crit': 0.1, 'dodge': 0.2, 'behaviors': ['Blink', 'Haste']},
    'Hydra':      {'emoji': '🐍', 'hp': 8,  'dmg': 2, 'rng': 1, 'arm': 2, 'res': 0, 'spd': 1, 'max_ap': 2, 'atk_cost': 1, 'mov_cost': 1, 'atk_type': 'P', 'crit': 0.1, 'dodge': 0.1, 'behaviors': ['Multi-Head', 'Regrowth']},
    'Basilisk':   {'emoji': '🦎', 'hp': 6,  'dmg': 2, 'rng': 2, 'arm': 2, 'res': 1, 'spd': 1, 'max_ap': 2, 'atk_cost': 1, 'mov_cost': 1, 'atk_type': 'P', 'crit': 0.1, 'dodge': 0.1, 'behaviors': ['Petrify', 'Stone Skin']},
    'Phantom':    {'emoji': '👤', 'hp': 4,  'dmg': 3, 'rng': 1, 'arm': 0, 'res': 1, 'spd': 2, 'max_ap': 2, 'atk_cost': 1, 'mov_cost': 1, 'atk_type': 'M', 'crit': 0.3, 'dodge': 0.3, 'behaviors': ['Stealth', 'Shadow Strike']},
    'Seraph':     {'emoji': '🕊️', 'hp': 5,  'dmg': 1, 'rng': 2, 'arm': 0, 'res': 3, 'spd': 1, 'max_ap': 2, 'atk_cost': 1, 'mov_cost': 1, 'atk_type': 'M', 'crit': 0.0, 'dodge': 0.2, 'heal': 3, 'behaviors': ['Shield Ally'], 'aura': {'res': 1}}
}

# ==========================================
# 2. GAME LOGIC & ENVIRONMENT
# ==========================================
class GameState:
    def __init__(self):
        self.grid_size = 9
        self.units = {} 
        self.current_turn = 'P1'
        self.winner = None
        self.turn_count = 0
        self.weather = '☀️' 
        
        self.passable_emojis = ['🌱', '🌼', '🌿', '💖', '⭐', '⛰️', '🌳', '🔥', '❄️', '🌌']
        self.impassable_emojis = ['🪨', '🌊']
        self.terrain = {}
        self.temp_terrain = {} 
        
        self.dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        
        self.generate_map()
        self.spawn_units()
        self.calculate_occupied()

    def generate_map(self):
        mid_x = self.grid_size // 2
        all_emojis = self.passable_emojis + self.impassable_emojis * 2
        for x in range(mid_x + 1):
            for y in range(self.grid_size):
                r = random.random()
                if r < 0.03: emoji = '💖'      
                elif r < 0.06: emoji = '⭐'    
                elif r < 0.10: emoji = '⛰️'    
                elif r < 0.15: emoji = '🌳'    
                elif r < 0.18: emoji = '🔥'
                elif r < 0.21: emoji = '❄️'
                elif r < 0.24: emoji = '🌌' 
                else: emoji = random.choice(all_emojis)
                self.terrain[(x, y)] = emoji
                self.terrain[(self.grid_size - 1 - x, y)] = emoji

    def spawn_units(self):
        p1_classes = random.sample(list(UNIT_TEMPLATES.keys()), 4)
        p1_spawns = [(0, 1), (0, 3), (0, 5), (0, 7)]
        for i, (cls, pos) in enumerate(zip(p1_classes, p1_spawns)):
            self.units[f'P1_u{i+1}'] = {'owner': 'P1', 'class': cls, 'pos': pos, **UNIT_TEMPLATES[cls].copy(), 'ap': UNIT_TEMPLATES[cls]['max_ap'], 'status': {'moved_dist': 0}}
            self.terrain[pos] = '🌱'

        p2_classes = random.sample(list(UNIT_TEMPLATES.keys()), 4)
        p2_spawns = [(8, 1), (8, 3), (8, 5), (8, 7)]
        for i, (cls, pos) in enumerate(zip(p2_classes, p2_spawns)):
            self.units[f'P2_u{i+1}'] = {'owner': 'P2', 'class': cls, 'pos': pos, **UNIT_TEMPLATES[cls].copy(), 'ap': UNIT_TEMPLATES[cls]['max_ap'], 'status': {'moved_dist': 0}}
            self.terrain[pos] = '🌱'

    def calculate_occupied(self):
        self.occupied = {u['pos'] for u in self.units.values() if u['hp'] > 0}

    def get_distance(self, pos1, pos2):
        return math.sqrt((pos1[0]-pos2[0])**2 + (pos1[1]-pos2[1])**2)

    def get_aura_bonuses(self, unit_id):
        unit = self.units[unit_id]
        if self.terrain.get(unit['pos']) == '🌌': return 0, 0, 0.0, 0
        arm_bonus, res_bonus, dodge_bonus, dmg_bonus = 0, 0, 0.0, 0
        x, y = unit['pos']
        for dx, dy in self.dirs:
            adj_pos = (x + dx, y + dy)
            for uid, u in self.units.items():
                if u['pos'] == adj_pos and u['owner'] == unit['owner'] and u['hp'] > 0:
                    if 'aura' in u:
                        arm_bonus += u['aura'].get('arm', 0)
                        res_bonus += u['aura'].get('res', 0)
                        dodge_bonus += u['aura'].get('dodge', 0.0)
                        dmg_bonus += u['aura'].get('dmg', 0)
        return arm_bonus, res_bonus, dodge_bonus, dmg_bonus

    def count_adjacent_allies(self, unit_id):
        unit = self.units[unit_id]
        count = 0
        x, y = unit['pos']
        for dx, dy in self.dirs:
            adj_pos = (x + dx, y + dy)
            for uid, u in self.units.items():
                if u['pos'] == adj_pos and u['owner'] == unit['owner'] and u['hp'] > 0:
                    count += 1
        return count

    def has_cohesion(self, unit_id):
        unit = self.units[unit_id]
        allies_near = 0
        for uid, u in self.units.items():
            if uid != unit_id and u['owner'] == unit['owner'] and u['hp'] > 0:
                if self.get_distance(unit['pos'], u['pos']) <= 2.0:
                    allies_near += 1
        return allies_near >= 2

    def is_flanking(self, attacker_pos, target_id):
        target = self.units[target_id]
        target_pos = target['pos']
        attacker_owner = 'P2' if target['owner'] == 'P1' else 'P1'
        if self.count_adjacent_allies(target_id) >= 2: return False
        dx = target_pos[0] - attacker_pos[0]
        dy = target_pos[1] - attacker_pos[1]
        opp_pos = (target_pos[0] + dx, target_pos[1] + dy)
        for uid, u in self.units.items():
            if u['owner'] == attacker_owner and u['hp'] > 0 and u['pos'] == opp_pos:
                return True
        return False

    def get_effective_stats(self, unit_id):
        unit = self.units[unit_id]
        base_def = unit['arm'] if unit.get('atk_type', 'P') == 'P' else unit['res']
        eff_rng = unit['rng']
        eff_dodge = unit['dodge']
        eff_crit = unit['crit']
        eff_dmg = unit['dmg']
        eff_spd = unit['spd']
        
        if self.terrain.get(unit['pos']) == '⛰️':
            base_def += 1; eff_rng += 1
        elif self.terrain.get(unit['pos']) == '🌳':
            eff_dodge += 0.30
        elif self.terrain.get(unit['pos']) == '❄️':
            eff_spd += 1
        elif self.terrain.get(unit['pos']) == '🌊' and 'Amphibious' in unit['behaviors']:
            eff_spd += 2
            
        arm_bonus, res_bonus, dodge_bonus, dmg_bonus = self.get_aura_bonuses(unit_id)
        eff_def = base_def + (arm_bonus if unit.get('atk_type', 'P') == 'P' else res_bonus)
        eff_dodge += dodge_bonus
        eff_dmg += dmg_bonus
        
        if 'Stone Skin' in unit['behaviors']: eff_def += 2
        if 'Reckless' in unit['behaviors']: eff_dmg += 2
        if 'Berserker' in unit['behaviors']:
            missing_hp = UNIT_TEMPLATES[unit['class']]['hp'] - unit['hp']
            eff_dmg += missing_hp // 2
        if 'Vanguard' in unit['behaviors'] and unit['hp'] == UNIT_TEMPLATES[unit['class']]['hp']: eff_dmg += 1
        if 'Elegant' in unit['behaviors'] and unit['hp'] == UNIT_TEMPLATES[unit['class']]['hp']: eff_dodge += 0.20
        if 'Swarm' in unit['behaviors']: eff_crit += 0.05 * self.count_adjacent_allies(unit_id)
        if self.has_cohesion(unit_id):
            eff_dodge += 0.10; eff_crit += 0.05
            
        if self.weather == '🌧️' and eff_rng > 2: eff_rng -= 1
        if unit['status'].get('curse', 0) > 0: eff_dmg = max(1, eff_dmg // 2)
        if unit['status'].get('rallied', 0) > 0:
            eff_dmg += 1; eff_def += 1
            
        if 'Charge' in unit['behaviors'] and unit['status'].get('moved_dist', 0) > 0:
            eff_dmg += unit['status']['moved_dist']
        if 'Dive Bomb' in unit['behaviors'] and unit['status'].get('moved_dist', 0) >= 2:
            eff_dmg += 2
            
        return eff_def, eff_rng, eff_dodge, eff_crit, eff_dmg, eff_spd

    def get_valid_actions(self, unit_id):
        unit = self.units[unit_id]
        if self.winner is not None or unit['ap'] <= 0 or unit['hp'] <= 0: return []
        
        actions = []
        x, y = unit['pos']
        _, eff_rng, _, _, _, eff_spd = self.get_effective_stats(unit_id)
        min_rng = unit.get('min_rng', 0)
        is_flying = 'Flying' in unit['behaviors'] or 'Graceful' in unit['behaviors']
        is_phasing = 'Phasing' in unit['behaviors'] or 'Incorporeal' in unit['behaviors']
        is_amphibious = 'Amphibious' in unit['behaviors']
        on_void = self.terrain.get(unit['pos']) == '🌌'
        
        if unit['ap'] >= unit['mov_cost']:
            for dx, dy in self.dirs:
                for step in range(1, eff_spd + 1):
                    nx, ny = x + dx * step, y + dy * step
                    if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                        path_clear = True
                        for s in range(1, step + 1):
                            check_pos = (x + dx * s, y + dy * s)
                            if not is_phasing:
                                if check_pos in self.occupied: path_clear = False; break
                                terrain = self.terrain[check_pos]
                                if terrain == '🪨' and not is_flying: path_clear = False; break
                                if terrain == '🌊' and not is_flying and not is_amphibious: path_clear = False; break
                        if path_clear:
                            actions.append(('MOVE', unit_id, (nx, ny)))
                        else:
                            break
        
        # Chronomancer Blink Action
        if 'Blink' in unit['behaviors'] and unit['ap'] >= 1:
            for dx, dy in self.dirs:
                for step in range(2, 5): # Blink range 2 to 4
                    nx, ny = x + dx * step, y + dy * step
                    if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                        if (nx, ny) not in self.occupied and self.terrain[(nx, ny)] not in self.impassable_emojis:
                            actions.append(('BLINK', unit_id, (nx, ny)))
                            
        # Chronomancer Haste Action
        if 'Haste' in unit['behaviors'] and unit['ap'] >= 2 and not on_void:
            for tid, t in self.units.items():
                if t['owner'] == unit['owner'] and t['hp'] > 0:
                    if self.get_distance(unit['pos'], t['pos']) <= 2.0:
                        actions.append(('HASTE', unit_id, tid))
                        
        # Seraph Shield Action
        if 'Shield Ally' in unit['behaviors'] and unit['ap'] >= 1 and not on_void:
            for tid, t in self.units.items():
                if t['owner'] == unit['owner'] and t['hp'] > 0 and t['status'].get('shield', 0) == 0:
                    if self.get_distance(unit['pos'], t['pos']) <= 2.0:
                        actions.append(('SHIELD', unit_id, tid))
                        
        # Basilisk Petrify Action
        if 'Petrify' in unit['behaviors'] and unit['ap'] >= 1 and not on_void:
            for tid, t in self.units.items():
                if t['owner'] != unit['owner'] and t['hp'] > 0 and 'Colossal' not in t['behaviors']:
                    if self.get_distance(unit['pos'], t['pos']) <= 2.0:
                        actions.append(('PETRIFY', unit_id, tid))
        
        if 'Demolition' in unit['behaviors'] and unit['ap'] >= 1 and not on_void:
            actions.append(('DEMOLISH', unit_id, None))

        if 'Lunge' in unit['behaviors'] and unit['ap'] >= (unit['atk_cost'] + unit['mov_cost']):
            for dx, dy in self.dirs:
                mid_pos = (x + dx, y + dy)
                target_pos = (x + dx*2, y + dy*2)
                if 0 <= target_pos[0] < self.grid_size and 0 <= target_pos[1] < self.grid_size:
                    if mid_pos not in self.occupied and self.terrain[mid_pos] not in self.impassable_emojis:
                        for tid, t in self.units.items():
                            if t['owner'] != unit['owner'] and t['hp'] > 0 and t['pos'] == target_pos:
                                actions.append(('LUNGE', unit_id, tid))
                    
        if unit['ap'] >= unit['atk_cost'] and unit['dmg'] > 0:
            if 'Bladestorm' in unit['behaviors'] and not on_void:
                adj_enemies = [tid for tid, t in self.units.items() if t['owner'] != unit['owner'] and t['hp'] > 0 and self.get_distance(unit['pos'], t['pos']) <= 1.5]
                if adj_enemies: actions.append(('BLADESTORM', unit_id, None))
            else:
                valid_targets = []
                for target_id, target in self.units.items():
                    if target['owner'] != unit['owner'] and target['hp'] > 0:
                        dist = self.get_distance(unit['pos'], target['pos'])
                        if min_rng <= dist <= eff_rng:
                            # Stealth Behavior: Can't be targeted from range
                            if 'Stealth' in target['behaviors'] and dist > 1.5:
                                continue
                            valid_targets.append(target_id)
                taunting_golems = []
                if 'Colossal' not in unit['behaviors']:
                    for tid, t in self.units.items():
                        if t['owner'] != unit['owner'] and t['hp'] > 0 and 'Taunt' in t['behaviors']:
                            if self.get_distance(unit['pos'], t['pos']) <= 1.5: taunting_golems.append(tid)
                if taunting_golems: valid_targets = taunting_golems
                for target_id in valid_targets: actions.append(('ATTACK', unit_id, target_id))
                    
        if unit['class'] == 'Witch' and unit['ap'] >= 1 and not on_void:
            for target_id, target in self.units.items():
                if target['owner'] != unit['owner'] and target['hp'] > 0:
                    if self.get_distance(unit['pos'], target['pos']) <= eff_rng: actions.append(('CURSE', unit_id, target_id))

        if 'Wish' in unit['behaviors'] and unit['ap'] >= 3 and not on_void:
            for target_id, target in self.units.items():
                dist = self.get_distance(unit['pos'], target['pos'])
                if dist <= eff_rng:
                    if target['owner'] != unit['owner'] and target['hp'] > 0: actions.append(('WISH_DMG', unit_id, target_id))
                    elif target['owner'] == unit['owner'] and target['hp'] > 0 and target['hp'] < UNIT_TEMPLATES[target['class']]['hp']: actions.append(('WISH_HEAL', unit_id, target_id))

        if 'Rally' in unit['behaviors'] and unit['ap'] >= 1 and not on_void:
            for target_id, target in self.units.items():
                if target['owner'] == unit['owner'] and target['hp'] > 0 and target['status'].get('rallied', 0) == 0:
                    if self.get_distance(unit['pos'], target['pos']) <= 1.5: actions.append(('RALLY', unit_id, target_id))
                        
        if 'Hook' in unit['behaviors'] and unit['ap'] >= 1:
            for dx, dy in self.dirs:
                for step in range(2, 4):
                    tx, ty = x + dx * step, y + dy * step
                    if 0 <= tx < self.grid_size and 0 <= ty < self.grid_size:
                        for tid, t in self.units.items():
                            if t['owner'] != unit['owner'] and t['hp'] > 0 and t['pos'] == (tx, ty):
                                if 'Colossal' not in t['behaviors']: actions.append(('HOOK', unit_id, tid))
                                    
        if 'Tongue Lash' in unit['behaviors'] and unit['ap'] >= 1:
            for dx, dy in self.dirs:
                for step in range(2, 3):
                    tx, ty = x + dx * step, y + dy * step
                    if 0 <= tx < self.grid_size and 0 <= ty < self.grid_size:
                        for tid, t in self.units.items():
                            if t['owner'] != unit['owner'] and t['hp'] > 0 and t['pos'] == (tx, ty):
                                if 'Colossal' not in t['behaviors']: actions.append(('TONGUE', unit_id, tid))
                                        
        if 'Entangle' in unit['behaviors'] and unit['ap'] >= 1 and not on_void:
            for dx, dy in self.dirs:
                tx, ty = x + dx, y + dy
                if 0 <= tx < self.grid_size and 0 <= ty < self.grid_size:
                    if (tx, ty) not in self.occupied and self.terrain[(tx, ty)] not in self.impassable_emojis and self.terrain[(tx, ty)] != '🌌':
                        actions.append(('ENTANGLE', unit_id, (tx, ty)))
                        
        if 'heal' in unit and unit['ap'] >= unit['atk_cost']:
            for target_id, target in self.units.items():
                if target['owner'] == unit['owner'] and target['hp'] > 0 and target['hp'] < UNIT_TEMPLATES[target['class']]['hp'] and 'Construct' not in target['behaviors']:
                    if self.terrain.get(target['pos']) != '🌌':
                        if self.get_distance(unit['pos'], target['pos']) <= eff_rng: actions.append(('HEAL', unit_id, target_id))

        if 'self_heal' in unit and unit['ap'] >= 1 and unit['hp'] < UNIT_TEMPLATES[unit['class']]['hp'] and 'Construct' not in unit['behaviors'] and not on_void:
            actions.append(('HEAL_SELF', unit_id, None))
                        
        return actions

    def apply_damage(self, target_id, amount, attacker_id=None, true_damage=False):
        target = self.units[target_id]
        if true_damage:
            actual_dmg = amount
        else:
            tgt_def, _, _, _, _, _ = self.get_effective_stats(target_id)
            attacker = self.units.get(attacker_id, {})
            if 'Hex' in attacker.get('behaviors', []) or 'Shadow Strike' in attacker.get('behaviors', []): tgt_def = 0
            actual_dmg = max(1, amount - tgt_def)
            if 'Reckless' in target['behaviors']: actual_dmg += 1
            if target['status'].get('curse', 0) > 0: actual_dmg *= 2
            dist = self.get_distance(self.units[attacker_id]['pos'], target['pos']) if attacker_id else 0
            if 'Deflect' in target['behaviors'] and dist > 1.5:
                actual_dmg = max(1, actual_dmg // 2)
            
        # Shield Absorption
        if target['status'].get('shield', 0) > 0:
            absorbed = min(actual_dmg, target['status']['shield'])
            target['status']['shield'] -= absorbed
            actual_dmg -= absorbed
            if target['status']['shield'] <= 0:
                del target['status']['shield']
                if 'shield_turns' in target['status']: del target['status']['shield_turns']
            if actual_dmg <= 0: return
            
        target['hp'] -= actual_dmg
        if target['hp'] <= 0:
            if 'Unyielding' in target['behaviors'] and not target['status'].get('unyielding_used', False):
                target['hp'] = 1
                target['status']['unyielding_used'] = True
            else:
                target['hp'] = 0
                if 'Martyr' in target['behaviors'] and not target['status'].get('martyred', False):
                    target['status']['martyred'] = True
                    for e_id, e_u in self.units.items():
                        if e_u['owner'] != target['owner'] and e_u['hp'] > 0 and self.get_distance(target['pos'], e_u['pos']) <= 1.5:
                            self.apply_damage(e_id, target['dmg'] * 2, true_damage=True)
                p1_alive = any(u['hp'] > 0 for u in self.units.values() if u['owner'] == 'P1')
                p2_alive = any(u['hp'] > 0 for u in self.units.values() if u['owner'] == 'P2')
                if not p1_alive: self.winner = 'P2'
                elif not p2_alive: self.winner = 'P1'

    def apply_action(self, action):
        new_state = self.clone()
        act_type, unit_id, target = action
        unit = new_state.units[unit_id]
        
        if act_type == 'MOVE':
            old_pos = unit['pos']
            for enemy_id, enemy in new_state.units.items():
                if enemy['owner'] != unit['owner'] and enemy['hp'] > 0 and 'Overwatch' in enemy['behaviors']:
                    if not enemy['status'].get('ow_used', False):
                        dist_to_target = new_state.get_distance(enemy['pos'], target)
                        if dist_to_target <= enemy['rng'] and dist_to_target >= enemy.get('min_rng', 0):
                            enemy['status']['ow_used'] = True
                            _, _, _, _, ow_dmg, _ = new_state.get_effective_stats(enemy_id)
                            new_state.apply_damage(unit_id, ow_dmg, enemy_id)
                            if unit['hp'] <= 0:
                                new_state.calculate_occupied()
                                unit['ap'] -= unit['mov_cost']
                                return new_state

            dist_moved = new_state.get_distance(old_pos, target)
            unit['status']['moved_dist'] = unit['status'].get('moved_dist', 0) + int(dist_moved)
            unit['pos'] = target
            unit['ap'] -= unit['mov_cost']
            new_state.calculate_occupied()
            
            for enemy_id, enemy in new_state.units.items():
                if enemy['owner'] != unit['owner'] and enemy['hp'] > 0 and 'Attack of Opportunity' in enemy['behaviors']:
                    dist_before = new_state.get_distance(old_pos, enemy['pos'])
                    dist_after = new_state.get_distance(unit['pos'], enemy['pos'])
                    if dist_before <= 1.5 and dist_after > 1.5:
                        ao_dmg = max(1, enemy['dmg'] // 2)
                        new_state.apply_damage(unit_id, ao_dmg, enemy_id)
                        if unit['hp'] <= 0:
                            return new_state
            
            tile = new_state.terrain[target]
            if tile == '💖':
                unit['hp'] = min(unit['hp'] + 4, UNIT_TEMPLATES[unit['class']]['hp'])
                new_state.terrain[target] = '🌱'
            elif tile == '⭐':
                unit['dmg'] += 1
                new_state.terrain[target] = '🌱'

        elif act_type == 'BLINK':
            unit['pos'] = target
            unit['ap'] -= 1
            new_state.calculate_occupied()
            
        elif act_type == 'HASTE':
            target_unit = new_state.units[target]
            unit['ap'] -= 2
            target_unit['ap'] = min(target_unit['max_ap'] + 1, target_unit['ap'] + 1)
            
        elif act_type == 'SHIELD':
            target_unit = new_state.units[target]
            unit['ap'] -= 1
            target_unit['status']['shield'] = 3
            target_unit['status']['shield_turns'] = 2
            
        elif act_type == 'PETRIFY':
            target_unit = new_state.units[target]
            unit['ap'] -= 1
            target_unit['status']['stun'] = 1
            
        elif act_type == 'LUNGE':
            target_unit = new_state.units[target]
            dx = target_unit['pos'][0] - unit['pos'][0]
            dy = target_unit['pos'][1] - unit['pos'][1]
            if dx != 0: dx = dx // abs(dx)
            if dy != 0: dy = dy // abs(dy)
            mid_pos = (unit['pos'][0] + dx, unit['pos'][1] + dy)
            unit['pos'] = mid_pos
            unit['ap'] -= (unit['atk_cost'] + unit['mov_cost'])
            unit['status']['moved_dist'] = unit['status'].get('moved_dist', 0) + 1
            new_state.calculate_occupied()
            act_type = 'ATTACK' 
            target = target

        if act_type == 'DEMOLISH':
            for e_id, e_u in list(new_state.units.items()):
                if e_u['owner'] != unit['owner'] and e_u['hp'] > 0 and new_state.get_distance(unit['pos'], e_u['pos']) <= 2.0:
                    new_state.apply_damage(e_id, 6, true_damage=True)
            unit['hp'] = 0
            unit['status']['martyred'] = True 
            p1_alive = any(u['hp'] > 0 for u in new_state.units.values() if u['owner'] == 'P1')
            p2_alive = any(u['hp'] > 0 for u in new_state.units.values() if u['owner'] == 'P2')
            if not p1_alive: new_state.winner = 'P2'
            elif not p2_alive: new_state.winner = 'P1'
            new_state.calculate_occupied()

        elif act_type == 'BLADESTORM':
            unit['ap'] -= unit['atk_cost']
            _, _, _, eff_crit, eff_dmg, _ = new_state.get_effective_stats(unit_id)
            dmg = eff_dmg
            if random.random() < eff_crit or new_state.weather == '🩸': dmg = int(dmg * 1.5)
            if 'Iaido' in unit['behaviors'] and not unit['status'].get('iaido_used', False):
                dmg += 2; unit['status']['iaido_used'] = True
            for e_id, e_u in list(new_state.units.items()):
                if e_u['owner'] != unit['owner'] and e_u['hp'] > 0 and new_state.get_distance(unit['pos'], e_u['pos']) <= 1.5:
                    new_state.apply_damage(e_id, dmg, unit_id)
                    
        elif act_type == 'CURSE':
            target_unit = new_state.units[target]
            unit['ap'] -= 1
            target_unit['status']['curse'] = 2
            
        elif act_type == 'RALLY':
            target_unit = new_state.units[target]
            unit['ap'] -= 1
            target_unit['status']['rallied'] = 3
            
        elif act_type == 'WISH_DMG':
            target_unit = new_state.units[target]
            unit['ap'] -= 3
            new_state.apply_damage(target, 5, unit_id, true_damage=True)
            
        elif act_type == 'WISH_HEAL':
            target_unit = new_state.units[target]
            unit['ap'] -= 3
            target_unit['hp'] = UNIT_TEMPLATES[target_unit['class']]['hp']
            
        elif act_type == 'HOOK' or act_type == 'TONGUE':
            target_unit = new_state.units[target]
            unit['ap'] -= 1
            pull_dist = 2 if act_type == 'HOOK' else 1
            dx = unit['pos'][0] - target_unit['pos'][0]
            dy = unit['pos'][1] - target_unit['pos'][1]
            if dx != 0: dx = dx // abs(dx)
            if dy != 0: dy = dy // abs(dy)
            for _ in range(pull_dist):
                next_pos = (target_unit['pos'][0] + dx, target_unit['pos'][1] + dy)
                if new_state.get_distance(next_pos, unit['pos']) <= 1.0: break
                if next_pos in new_state.occupied or next_pos in new_state.impassable_emojis: break
                target_unit['pos'] = next_pos
            new_state.calculate_occupied()
            
        elif act_type == 'ENTANGLE':
            unit['ap'] -= 1
            if target not in new_state.temp_terrain:
                new_state.temp_terrain[target] = {'orig': new_state.terrain[target], 'turns': 2}
            new_state.terrain[target] = '🌳'
            
        elif act_type == 'ATTACK':
            target_unit = new_state.units[target]
            unit['ap'] -= unit['atk_cost']
            
            if 'Chaos' in unit['behaviors'] and random.random() < 0.5:
                adj_enemies = [tid for tid, t in new_state.units.items() if t['owner'] != unit['owner'] and t['hp'] > 0 and new_state.get_distance(unit['pos'], t['pos']) <= 1.5]
                if adj_enemies:
                    target = random.choice(adj_enemies)
                    target_unit = new_state.units[target]
            
            if 'Guardian' not in target_unit['behaviors']:
                for guardian_id, guardian in new_state.units.items():
                    if guardian['owner'] == target_unit['owner'] and guardian['hp'] > 0 and 'Guardian' in guardian['behaviors']:
                        if new_state.get_distance(guardian['pos'], target_unit['pos']) <= 1.5:
                            if random.random() < 0.50:
                                target_unit = guardian; target = guardian_id; break
            
            _, _, tgt_dodge, _, _, _ = new_state.get_effective_stats(target)
            attacks = 2 if 'Multishot' in unit['behaviors'] else 1
            for _ in range(attacks):
                if target_unit['hp'] <= 0: break
                if random.random() < tgt_dodge:
                    if 'Riposte' in target_unit['behaviors']:
                        _, _, _, _, rip_dmg, _ = new_state.get_effective_stats(target)
                        new_state.apply_damage(unit_id, rip_dmg, target, true_damage=True)
                else:
                    _, _, _, eff_crit, eff_dmg, _ = new_state.get_effective_stats(unit_id)
                    dmg = eff_dmg
                    if attacks == 2: dmg = max(1, dmg // 2)
                    dist = new_state.get_distance(unit['pos'], target_unit['pos'])
                    is_crit = False
                    if new_state.weather == '🩸': is_crit = True
                    elif 'Eagle Eye' in unit['behaviors'] and dist > 2:
                        if random.random() < (eff_crit + 0.10 * int(dist - 2)): is_crit = True
                    elif random.random() < eff_crit: is_crit = True
                    if is_crit: dmg = int(dmg * 1.5)
                    if 'Iaido' in unit['behaviors'] and not unit['status'].get('iaido_used', False):
                        dmg += 2; unit['status']['iaido_used'] = True
                    is_flank = new_state.is_flanking(unit['pos'], target)
                    if is_flank:
                        dmg = int(dmg * 1.5)
                        if 'Flanker' in unit['behaviors']: dmg += 2
                    if target_unit['status'].get('marked', 0) > 0: dmg += 1
                    
                    new_state.apply_damage(target, dmg, unit_id)
                    
                    if dist <= 1.5 and unit['atk_type'] == 'P' and 'Construct' not in target_unit['behaviors'] and 'Colossal' not in target_unit['behaviors'] and 'Bulwark' not in target_unit['behaviors']:
                        protected = False
                        for ally_id, ally in new_state.units.items():
                            if ally['owner'] == target_unit['owner'] and 'Bulwark' in ally['behaviors'] and new_state.get_distance(ally['pos'], target_unit['pos']) <= 1.5:
                                protected = True; break
                        if not protected:
                            kb_chance = 1.0 if new_state.weather == '🌬️' else 0.30
                            kb_dist = 2 if new_state.weather == '🌬️' else 1
                            if random.random() < kb_chance:
                                dx = target_unit['pos'][0] - unit['pos'][0]
                                dy = target_unit['pos'][1] - unit['pos'][1]
                                if dx != 0: dx = dx // abs(dx)
                                if dy != 0: dy = dy // abs(dy)
                                for _ in range(kb_dist):
                                    push_pos = (target_unit['pos'][0] + dx, target_unit['pos'][1] + dy)
                                    if 0 <= push_pos[0] < new_state.grid_size and 0 <= push_pos[1] < new_state.grid_size:
                                        if push_pos in new_state.occupied or new_state.terrain[push_pos] in new_state.impassable_emojis:
                                            new_state.apply_damage(target, 1, true_damage=True); break
                                        else:
                                            target_unit['pos'] = push_pos; new_state.calculate_occupied()
                                    else:
                                        new_state.apply_damage(target, 1, true_damage=True); break

                    if 'Life Drain' in unit['behaviors']:
                        unit['hp'] = min(unit['hp'] + dmg, UNIT_TEMPLATES[unit['class']]['hp'])
                    elif 'Bloodthirst' in unit['behaviors'] and target_unit['hp'] < target_unit['hp'] + dmg:
                        unit['hp'] = min(unit['hp'] + dmg // 2, UNIT_TEMPLATES[unit['class']]['hp'])
                    elif 'Life Steal' in unit['behaviors']:
                        unit['hp'] = min(unit['hp'] + 1, UNIT_TEMPLATES[unit['class']]['hp'])
                    
                    if 'poison' in unit and 'Construct' not in target_unit['behaviors'] and 'Stone Skin' not in target_unit['behaviors']:
                        target_unit['status']['poison'] = {'dmg': unit['poison'], 'turns': 2}
                    
                    if 'Pierce' in unit['behaviors']:
                        dx = target_unit['pos'][0] - unit['pos'][0]
                        dy = target_unit['pos'][1] - unit['pos'][1]
                        if dx != 0: dx = dx // abs(dx)
                        if dy != 0: dy = dy // abs(dy)
                        pierce_pos = (target_unit['pos'][0] + dx, target_unit['pos'][1] + dy)
                        for p_id, p_u in new_state.units.items():
                            if p_u['pos'] == pierce_pos and p_u['owner'] != unit['owner'] and p_u['hp'] > 0:
                                new_state.apply_damage(p_id, int(dmg * 0.5), true_damage=True)
                                p_u['status']['marked'] = 1; break

                    if 'Breath' in unit['behaviors']:
                        dx = target_unit['pos'][0] - unit['pos'][0]
                        dy = target_unit['pos'][1] - unit['pos'][1]
                        if dx != 0: dx = dx // abs(dx)
                        if dy != 0: dy = dy // abs(dy)
                        curr_x, curr_y = target_unit['pos']
                        for step in range(1, 4):
                            curr_x += dx; curr_y += dy
                            hit_something = False
                            for e_id, e_u in new_state.units.items():
                                if e_u['pos'] == (curr_x, curr_y) and e_u['owner'] != unit['owner'] and e_u['hp'] > 0:
                                    new_state.apply_damage(e_id, dmg, unit_id, true_damage=True)
                                    hit_something = True; break
                            if (curr_x, curr_y) in new_state.impassable_emojis or not (0 <= curr_x < new_state.grid_size and 0 <= curr_y < new_state.grid_size): break

                    if 'splash' in unit:
                        for splash_id, splash_u in new_state.units.items():
                            if splash_id != target and splash_u['owner'] != unit['owner'] and splash_u['hp'] > 0:
                                if new_state.get_distance(target_unit['pos'], splash_u['pos']) <= 1.5:
                                    new_state.apply_damage(splash_id, unit['splash'], unit_id)
                                    splash_u['status']['marked'] = 1
                                    
                    if 'Cleave' in unit['behaviors'] and dist <= 1.5:
                        for c_id, c_u in new_state.units.items():
                            if c_id != target and c_u['owner'] != unit['owner'] and c_u['hp'] > 0:
                                if new_state.get_distance(unit['pos'], c_u['pos']) <= 1.5 and new_state.get_distance(target_unit['pos'], c_u['pos']) <= 1.5:
                                    new_state.apply_damage(c_id, dmg, unit_id)
                                    
                    # Multi-Head Behavior (Hydra)
                    if 'Multi-Head' in unit['behaviors'] and dist <= 1.5:
                        for c_id, c_u in new_state.units.items():
                            if c_id != target and c_u['owner'] != unit['owner'] and c_u['hp'] > 0:
                                if new_state.get_distance(unit['pos'], c_u['pos']) <= 1.5:
                                    new_state.apply_damage(c_id, dmg, unit_id)

                    if target_unit['hp'] > 0: target_unit['status']['marked'] = 1
                    
                    if target_unit['hp'] <= 0:
                        if 'Executioner' in unit['behaviors']: unit['ap'] = min(unit['max_ap'], unit['ap'] + 1)
                        if 'Bloodlust' in unit['behaviors']:
                            for ally_id, ally in new_state.units.items():
                                if ally['owner'] == unit['owner'] and ally['hp'] > 0 and new_state.get_distance(unit['pos'], ally['pos']) <= 1.5:
                                    ally['hp'] = min(ally['hp'] + 2, UNIT_TEMPLATES[ally['class']]['hp'])
                    else:
                        if 'Counter' in target_unit['behaviors'] and unit['rng'] == 1:
                            new_state.apply_damage(unit_id, target_unit['dmg'] // 2, target)
            
            if 'Hit and Run' in unit['behaviors'] and unit['status'].get('moved_dist', 0) > 0:
                unit['ap'] = min(unit['max_ap'], unit['ap'] + 1)
                    
        elif act_type == 'HEAL':
            target_unit = new_state.units[target]
            unit['ap'] -= unit['atk_cost']
            heal_amt = unit['heal'] + (2 if new_state.weather == '☀️' else 0)
            target_unit['hp'] = min(target_unit['hp'] + heal_amt, UNIT_TEMPLATES[target_unit['class']]['hp'])
            if 'Benediction' in unit['behaviors']:
                target_unit['hp'] = min(target_unit['hp'] + 1, UNIT_TEMPLATES[target_unit['class']]['hp'])
            if 'Purify' in unit['behaviors']:
                target_unit['status']['marked'] = 0
                if 'poison' in target_unit['status']: del target_unit['status']['poison']
                if 'curse' in target_unit['status']: del target_unit['status']['curse']
            
        elif act_type == 'HEAL_SELF':
            unit['ap'] -= 1
            heal_amt = unit['self_heal'] + (2 if new_state.weather == '☀️' else 0)
            unit['hp'] = min(unit['hp'] + heal_amt, UNIT_TEMPLATES[unit['class']]['hp'])
            
        if all(u['ap'] == 0 for u in new_state.units.values() if u['owner'] == new_state.current_turn and u['hp'] > 0) or new_state.winner:
            new_state.current_turn = 'P2' if new_state.current_turn == 'P1' else 'P1'
            new_state.turn_count += 1
            if new_state.turn_count % 4 == 0:
                weathers = ['☀️', '🌧️', '🌬️', '🩸']
                new_state.weather = weathers[(weathers.index(new_state.weather) + 1) % len(weathers)]
            
            for pos, data in list(new_state.temp_terrain.items()):
                data['turns'] -= 1
                if data['turns'] <= 0:
                    new_state.terrain[pos] = data['orig']
                    del new_state.temp_terrain[pos]
            
            for uid, u in new_state.units.items():
                if u['owner'] == new_state.current_turn and u['hp'] > 0:
                    u['ap'] = u['max_ap']
                    u['status']['ow_used'] = False
                    u['status']['unyielding_used'] = False
                    u['status']['iaido_used'] = False
                    u['status']['moved_dist'] = 0 
                    
                    # Stun (Petrify) Check
                    if u['status'].get('stun', 0) > 0:
                        u['ap'] = 0
                        u['status']['stun'] -= 1
                        if u['status']['stun'] <= 0: del u['status']['stun']
                        continue # Skip other start of turn effects
                    
                    # Shield Decay
                    if u['status'].get('shield', 0) > 0:
                        u['status']['shield_turns'] -= 1
                        if u['status']['shield_turns'] <= 0:
                            del u['status']['shield']
                            del u['status']['shield_turns']
                    
                    # Regrowth (Hydra)
                    if 'Regrowth' in u['behaviors'] and u['hp'] <= UNIT_TEMPLATES[u['class']]['hp'] // 2:
                        u['hp'] = min(u['hp'] + 2, UNIT_TEMPLATES[u['class']]['hp'])
                    
                    if "Nature's Blessing" in u['behaviors']:
                        for ally_id, ally in new_state.units.items():
                            if ally['owner'] == u['owner'] and ally['hp'] > 0 and new_state.get_distance(u['pos'], ally['pos']) <= 1.5:
                                ally['hp'] = min(ally['hp'] + 1, UNIT_TEMPLATES[ally['class']]['hp'])
                    
                    for e_id, e_u in new_state.units.items():
                        if e_u['owner'] != u['owner'] and e_u['hp'] > 0 and 'Terrify' in e_u['behaviors']:
                            if new_state.get_distance(u['pos'], e_u['pos']) <= 1.5:
                                u['ap'] = max(0, u['ap'] - 1)
                                break
                                
                    if 'Regen' in u['behaviors'] and 'Construct' not in u['behaviors'] and new_state.terrain.get(u['pos']) != '🌌':
                        regen_amt = 2 if new_state.weather == '☀️' else 1
                        u['hp'] = min(u['hp'] + regen_amt, UNIT_TEMPLATES[u['class']]['hp'])
                    if new_state.terrain.get(u['pos']) == '🔥' and 'Construct' not in u['behaviors']:
                        new_state.apply_damage(uid, 1, true_damage=True)
                    for s in ['marked', 'curse', 'rallied']:
                        if u['status'].get(s, 0) > 0:
                            u['status'][s] -= 1
                            if u['status'][s] <= 0: del u['status'][s]
                    if 'poison' in u['status'] and 'Construct' not in u['behaviors'] and 'Stone Skin' not in u['behaviors']:
                        new_state.apply_damage(uid, u['status']['poison']['dmg'], true_damage=True)
                        if u['hp'] > 0:
                            u['status']['poison']['turns'] -= 1
                            if u['status']['poison']['turns'] <= 0: del u['status']['poison']
            new_state.calculate_occupied()
                    
        return new_state

    def clone(self):
        new_state = GameState.__new__(GameState)
        new_state.grid_size = self.grid_size
        new_state.units = copy.deepcopy(self.units)
        new_state.current_turn = self.current_turn
        new_state.winner = self.winner
        new_state.turn_count = self.turn_count
        new_state.weather = self.weather
        new_state.passable_emojis = self.passable_emojis
        new_state.impassable_emojis = self.impassable_emojis
        new_state.terrain = self.terrain.copy()
        new_state.temp_terrain = copy.deepcopy(self.temp_terrain)
        new_state.occupied = self.occupied.copy()
        new_state.dirs = self.dirs
        return new_state

    def is_terminal(self):
        return self.winner is not None

    def evaluate(self):
        if self.winner == 'P1': return 1.0
        if self.winner == 'P2': return -1.0
        p1_score = 0; p2_score = 0
        for uid, u in self.units.items():
            if u['hp'] > 0:
                eff_def, _, eff_dodge, eff_crit, eff_dmg, _ = self.get_effective_stats(uid)
                score = u['hp'] + eff_def + (eff_dmg * 2) + (eff_dodge * 10) + (eff_crit * 10)
                if 'poison' in u['status']: score -= 3
                if u['status'].get('marked', 0) > 0: score -= 4 
                if u['status'].get('curse', 0) > 0: score -= 5
                if u['status'].get('rallied', 0) > 0: score += 4
                if u['status'].get('shield', 0) > 0: score += u['status']['shield'] * 3
                if u['status'].get('stun', 0) > 0: score -= 5
                if 'Stealth' in u['behaviors']: score += 5
                if u['ap'] < u['max_ap']: score -= (u['max_ap'] - u['ap']) * 2
                if self.terrain.get(u['pos']) == '⛰️': score += 2
                if self.terrain.get(u['pos']) == '🔥': score -= 3 
                if self.terrain.get(u['pos']) == '❄️': score += 1 
                if self.terrain.get(u['pos']) == '🌌': score -= 4 
                if self.count_adjacent_allies(uid) >= 2: score += 3
                if self.has_cohesion(uid): score += 4
                for e_id, e_u in self.units.items():
                    if e_u['owner'] != u['owner'] and e_u['hp'] > 0 and 'Martyr' in e_u['behaviors']:
                        if self.get_distance(u['pos'], e_u['pos']) <= 1.5: score -= 5
                    if e_u['owner'] != u['owner'] and e_u['hp'] > 0 and 'Terrify' in e_u['behaviors']:
                        if self.get_distance(u['pos'], e_u['pos']) <= 1.5: score -= 3
                enemies = [e for e in self.units.values() if e['owner'] != u['owner'] and e['hp'] > 0]
                if enemies:
                    min_dist = min(self.get_distance(u['pos'], e['pos']) for e in enemies)
                    if u['rng'] >= 3: 
                        if min_dist < 2: score -= 4 
                        else: score += 2 
                    else: 
                        if min_dist > 2: score -= 2 
                if u['owner'] == 'P1': p1_score += score
                else: p2_score += score
        return (p1_score - p2_score) / 200.0

# ==========================================
# 3. PUCT ALGORITHM (AlphaZero Style)
# ==========================================
class PUCTNode:
    def __init__(self, state, parent=None, action=None, prior=0.0):
        self.state = state; self.parent = parent; self.action = action; self.prior = prior  
        self.children = []; self.visits = 0; self.value = 0.0; self.untried_actions = []
        for uid, u in state.units.items():
            if u['owner'] == state.current_turn and u['hp'] > 0:
                self.untried_actions.extend(state.get_valid_actions(uid))
        if not self.untried_actions: self.untried_actions = [('END_TURN', None, None)]

    def is_fully_expanded(self): return len(self.untried_actions) == 0

    def best_child(self, c_puct=1.4):
        best_score = -float('inf'); best_child = None
        for child in self.children:
            q = child.value / (child.visits + 1e-6) 
            u = c_puct * child.prior * math.sqrt(self.visits) / (1 + child.visits) 
            score = q + u
            if score > best_score: best_score = score; best_child = child
        return best_child

def mcts_puct_search(root_state, iterations=600):
    root = PUCTNode(root_state)
    for _ in range(iterations):
        node = root; state = root_state
        while node.is_fully_expanded() and not state.is_terminal():
            node = node.best_child(); state = node.state
        if not state.is_terminal():
            if node.untried_actions:
                action = node.untried_actions.pop(random.randrange(len(node.untried_actions)))
                next_state = state.apply_action(action)
                prior = 1.0 / len(root.untried_actions) if root.untried_actions else 0.1 
                child_node = PUCTNode(next_state, parent=node, action=action, prior=prior)
                node.children.append(child_node); node = child_node; state = next_state
        value = state.evaluate()
        while node is not None:
            node.visits += 1
            node.value += value if node.state.current_turn == 'P2' else -value
            node = node.parent
    if root.children:
        dirichlet_noise = [random.gammavariate(0.3, 1) for _ in range(len(root.children))]
        for child, noise in zip(root.children, dirichlet_noise):
            child.prior = 0.75 * child.prior + 0.25 * noise
    best_child = max(root.children, key=lambda c: c.visits, default=None)
    return best_child.action if best_child else None

# ==========================================
# 4. PYSIDE6 GUI
# ==========================================
class BattleCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.state = GameState(); self.is_running = False
        self.hit_effects = []; self.attack_lines = []; self.flash_color = None 
        self.setWindowTitle("PUCT AI battle - Time & Stealth (34 Units)")
        self.resize(1200, 850)
        self.setStyleSheet("""
            QWidget { background-color: #1e1e1e; color: #e0e0e0; font-family: Arial; }
            QPushButton { background-color: #007acc; border: 1px solid #005a9e; padding: 8px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #0098ff; }
            QTextEdit { background-color: #2d2d2d; border: 1px solid #3c3c3c; }
            QLabel { font-size: 14px; }
            QProgressBar { text-align: center; border: 1px solid #444; border-radius: 4px; background-color: #2d2d2d; }
            QProgressBar::chunk { background-color: #007acc; }
        """)
        main_layout = QHBoxLayout(self)
        left_panel = QVBoxLayout()
        top_bar = QHBoxLayout()
        self.eval_bar = QProgressBar(); self.eval_bar.setRange(0, 100)
        self.eval_bar.setFormat("AI Confidence (P1 Win %): %v%"); self.eval_bar.setValue(50)
        top_bar.addWidget(self.eval_bar, stretch=2)
        self.weather_label = QLabel(f"Weather: {self.state.weather}")
        self.weather_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffaa00; padding-left: 10px;")
        top_bar.addWidget(self.weather_label, stretch=1)
        left_panel.addLayout(top_bar)
        self.canvas_label = QLabel(); self.canvas_label.setMinimumSize(800, 800)
        left_panel.addWidget(self.canvas_label, stretch=1)
        main_layout.addLayout(left_panel, stretch=2)
        
        right_panel = QVBoxLayout(); right_panel.setSpacing(10)
        title = QLabel("⚙️ Control Panel")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #007acc;")
        right_panel.addWidget(title)
        self.start_btn = QPushButton("▶️ Start Battle"); self.start_btn.clicked.connect(self.toggle_battle)
        right_panel.addWidget(self.start_btn)
        self.regen_btn = QPushButton("🗺️ Generate New Squads & Map"); self.regen_btn.clicked.connect(self.regenerate_map)
        right_panel.addWidget(self.regen_btn)
        right_panel.addWidget(QLabel("🧠 AI Strength (MCTS Iterations):"))
        self.strength_slider = QSlider(Qt.Horizontal); self.strength_slider.setRange(100, 2000); self.strength_slider.setValue(800)
        right_panel.addWidget(self.strength_slider)
        self.strength_label = QLabel("Current: 800 Iterations")
        self.strength_slider.valueChanged.connect(lambda v: self.strength_label.setText(f"Current: {v} Iterations"))
        right_panel.addWidget(self.strength_label)
        right_panel.addWidget(QLabel("⚡ AI Speed (Delay ms):"))
        self.speed_slider = QSlider(Qt.Horizontal); self.speed_slider.setRange(10, 1000); self.speed_slider.setValue(150)
        right_panel.addWidget(self.speed_slider)
        right_panel.addWidget(QLabel("🛡️ Team Rosters:"))
        self.team_info_label = QLabel(); self.team_info_label.setStyleSheet("font-size: 12px; color: #cccccc;")
        right_panel.addWidget(self.team_info_label)
        right_panel.addWidget(QLabel("📜 Combat Log:"))
        self.log_area = QTextEdit(); self.log_area.setReadOnly(True)
        right_panel.addWidget(self.log_area, stretch=1)
        main_layout.addLayout(right_panel, stretch=1)
        
        self.timer = QTimer(self); self.timer.timeout.connect(self.ai_step)
        self.effect_timer = QTimer(self); self.effect_timer.setSingleShot(True)
        self.effect_timer.timeout.connect(self.clear_effects)
        self.update_ui()

    def clear_effects(self):
        self.hit_effects = []; self.attack_lines = []; self.flash_color = None; self.update()

    def toggle_battle(self):
        if self.is_running:
            self.timer.stop(); self.start_btn.setText("▶️ Resume Battle"); self.is_running = False
        else:
            if self.state.winner:
                self.state = GameState(); self.log_area.clear()
            self.timer.start(self.speed_slider.value()); self.start_btn.setText("⏸️ Pause Battle"); self.is_running = True; self.update_ui()

    def regenerate_map(self):
        if not self.is_running:
            self.state = GameState(); self.log_area.clear(); self.log("🗺️ New map & squads generated."); self.update_ui()

    def log(self, message):
        self.log_area.append(message)
        self.log_area.verticalScrollBar().setValue(self.log_area.verticalScrollBar().maximum())

    def update_ui(self):
        p1_text = "<b style='color:#0098ff'>Blue Team:</b><br>"
        p2_text = "<b style='color:#ff5555'>Red Team:</b><br>"
        for uid, u in self.state.units.items():
            status_emoji = "🤢" if 'poison' in u['status'] else ""
            beh = f"<i>[{', '.join(u['behaviors'])}]</i> " if u['behaviors'] else ""
            stats = f"❤{u['hp']} 🗡{u['dmg']} 🛡{u['arm']} 🔮{u['res']} 🏹{u['rng']} 👟{u['spd']} ⚡{u['ap']} {status_emoji}"
            txt = f"{u['emoji']} {beh}{u['class']} ({stats})<br>"
            if u['owner'] == 'P1': p1_text += txt
            else: p2_text += txt
        self.team_info_label.setText(p1_text + "<br>" + p2_text)
        self.weather_label.setText(f"Weather: {self.state.weather}")
        eval_score = self.state.evaluate()
        win_prob = int((eval_score + 1.0) / 2.0 * 100)
        self.eval_bar.setValue(win_prob)
        self.update()

    def ai_step(self):
        if not self.is_running: return
        if self.state.is_terminal():
            self.timer.stop(); self.is_running = False; self.start_btn.setText("▶️ Restart Battle")
            winner_color = "Blue (P1)" if self.state.winner == 'P1' else "Red (P2)"
            self.log(f"<span style='color: #00ff00; font-weight: bold;'>🏆 Game Over! Winner: {winner_color}</span>")
            self.update_ui(); return
            
        current_player = self.state.current_turn
        old_weather = self.state.weather
        iterations = self.strength_slider.value()
        action = mcts_puct_search(self.state, iterations=iterations)
        
        if action:
            act_type, unit_id, target = action
            if act_type == 'MOVE':
                u = self.state.units[unit_id]
                self.log(f"{u['emoji']} {u['class']} moved to {target}")
            elif act_type == 'BLINK':
                u = self.state.units[unit_id]
                self.attack_lines.append((u['pos'], target, QColor(0, 255, 255)))
                self.hit_effects.append(target)
                self.effect_timer.start(400)
                self.log(f"<span style='color: #00ffff; font-weight: bold;'>⏳ {u['emoji']} {u['class']} blinked to {target}!</span>")
            elif act_type == 'HASTE':
                u = self.state.units[unit_id]; t = self.state.units[target]
                self.attack_lines.append((u['pos'], t['pos'], QColor(255, 255, 0)))
                self.hit_effects.append(t['pos'])
                self.effect_timer.start(400)
                self.log(f"<span style='color: #ffff00; font-weight: bold;'>⏳ {u['emoji']} {u['class']} hasted {t['emoji']} {t['class']}!</span>")
            elif act_type == 'SHIELD':
                u = self.state.units[unit_id]; t = self.state.units[target]
                self.attack_lines.append((u['pos'], t['pos'], QColor(0, 150, 255)))
                self.hit_effects.append(t['pos'])
                self.effect_timer.start(400)
                self.log(f"<span style='color: #0099ff; font-weight: bold;'>🕊️ {u['emoji']} {u['class']} shielded {t['emoji']} {t['class']}!</span>")
            elif act_type == 'PETRIFY':
                u = self.state.units[unit_id]; t = self.state.units[target]
                self.attack_lines.append((u['pos'], t['pos'], QColor(150, 150, 150)))
                self.hit_effects.append(t['pos'])
                self.effect_timer.start(400)
                self.log(f"<span style='color: #aaaaaa; font-weight: bold;'>🦎 {u['emoji']} {u['class']} petrified {t['emoji']} {t['class']}!</span>")
            elif act_type == 'DEMOLISH':
                u = self.state.units[unit_id]
                self.flash_color = QColor(255, 100, 0, 150); self.hit_effects.append(u['pos'])
                for e_id, e_u in self.state.units.items():
                    if e_u['owner'] != u['owner'] and e_u['hp'] > 0 and self.state.get_distance(u['pos'], e_u['pos']) <= 2.0:
                        self.hit_effects.append(e_u['pos'])
                self.effect_timer.start(600)
                self.log(f"<span style='color: #ff5500; font-weight: bold;'>🧨 {u['emoji']} {u['class']} used DEMOLITION!</span>")
            elif act_type == 'BLADESTORM':
                attacker = self.state.units[unit_id]
                for e_id, e_u in self.state.units.items():
                    if e_u['owner'] != attacker['owner'] and e_u['hp'] > 0 and self.state.get_distance(attacker['pos'], e_u['pos']) <= 1.5:
                        self.attack_lines.append((attacker['pos'], e_u['pos'], QColor(0, 255, 255))); self.hit_effects.append(e_u['pos'])
                self.flash_color = QColor(0, 255, 255, 50); self.effect_timer.start(400)
                self.log(f"<span style='color: #00ffff; font-weight: bold;'>🌪️ {attacker['emoji']} {attacker['class']} used BLADESTORM!</span>")
            elif act_type == 'CURSE':
                attacker = self.state.units[unit_id]; target_unit = self.state.units[target]
                self.attack_lines.append((attacker['pos'], target_unit['pos'], QColor(153, 51, 255))); self.hit_effects.append(target_unit['pos'])
                self.effect_timer.start(400)
                self.log(f"<span style='color: #9933ff;'>🔮 {attacker['emoji']} {attacker['class']} cursed {target_unit['emoji']} {target_unit['class']}!</span>")
            elif act_type == 'RALLY':
                attacker = self.state.units[unit_id]; target_unit = self.state.units[target]
                self.attack_lines.append((attacker['pos'], target_unit['pos'], QColor(255, 165, 0))); self.hit_effects.append(target_unit['pos'])
                self.effect_timer.start(400)
                self.log(f"<span style='color: #ffaa00;'>🚩 {attacker['emoji']} {attacker['class']} rallied {target_unit['emoji']} {target_unit['class']}!</span>")
            elif act_type == 'HOOK' or act_type == 'TONGUE':
                attacker = self.state.units[unit_id]; target_unit = self.state.units[target]
                self.attack_lines.append((attacker['pos'], target_unit['pos'], QColor(255, 255, 0))); self.hit_effects.append(target_unit['pos'])
                self.effect_timer.start(400)
                verb = "hooked" if act_type == 'HOOK' else "lashed"
                self.log(f"<span style='color: #ffff00; font-weight: bold;'>🪝 {attacker['emoji']} {attacker['class']} {verb} {target_unit['emoji']} {target_unit['class']}!</span>")
            elif act_type == 'ENTANGLE':
                attacker = self.state.units[unit_id]
                self.attack_lines.append((attacker['pos'], target, QColor(0, 150, 0))); self.hit_effects.append(target)
                self.effect_timer.start(400)
                self.log(f"<span style='color: #00aa00; font-weight: bold;'>🌿 {attacker['emoji']} {attacker['class']} entangled the ground at {target}!</span>")
            elif act_type == 'LUNGE':
                attacker = self.state.units[unit_id]; target_unit = self.state.units[target]
                self.attack_lines.append((attacker['pos'], target_unit['pos'], QColor(255, 50, 50))); self.hit_effects.append(target_unit['pos'])
                self.effect_timer.start(400)
                self.log(f"<span style='color: #ff5555;'>🤺 {attacker['emoji']} {attacker['class']} lunged at {target_unit['emoji']} {target_unit['class']}!</span>")
            elif act_type == 'WISH_DMG' or act_type == 'WISH_HEAL':
                attacker = self.state.units[unit_id]; target_unit = self.state.units[target]
                color = QColor(255, 0, 255) if act_type == 'WISH_DMG' else QColor(0, 255, 0)
                self.attack_lines.append((attacker['pos'], target_unit['pos'], color)); self.hit_effects.append(target_unit['pos'])
                self.flash_color = QColor(255, 0, 255, 50) if act_type == 'WISH_DMG' else QColor(0, 255, 0, 50)
                self.effect_timer.start(500)
                verb = "smited" if act_type == 'WISH_DMG' else "healed"
                self.log(f"<span style='color: #ff00ff; font-weight: bold;'>🌟 {attacker['emoji']} {attacker['class']} used Wish and {verb} {target_unit['emoji']} {target_unit['class']}!</span>")
            elif act_type == 'ATTACK':
                attacker = self.state.units[unit_id]; target_unit = self.state.units[target]
                intercepted_by = None
                if 'Guardian' not in target_unit['behaviors']:
                    for g_id, g in self.state.units.items():
                        if g['owner'] == target_unit['owner'] and g['hp'] > 0 and 'Guardian' in g['behaviors']:
                            if self.state.get_distance(g['pos'], target_unit['pos']) <= 1.5:
                                if random.random() < 0.50: intercepted_by = g; break
                actual_target = intercepted_by if intercepted_by else target_unit
                actual_target_id = target if not intercepted_by else [k for k, v in self.state.units.items() if v == intercepted_by][0]
                _, _, tgt_dodge, _, _, _ = self.state.get_effective_stats(actual_target_id)
                is_miss = random.random() < tgt_dodge
                is_flank = self.state.is_flanking(attacker['pos'], target)
                is_marked = actual_target['status'].get('marked', 0) > 0
                is_cursed = actual_target['status'].get('curse', 0) > 0
                is_blood_moon = self.state.weather == '🩸'
                is_multishot = 'Multishot' in attacker['behaviors']
                
                self.attack_lines.append((attacker['pos'], actual_target['pos'], QColor(255, 165, 0) if intercepted_by else QColor(255, 50, 50)))
                if intercepted_by:
                    self.log(f"<span style='color: #ffaa00;'>🛡️ {intercepted_by['emoji']} {intercepted_by['class']} intercepted the attack!</span>")
                if not is_miss:
                    self.hit_effects.append(actual_target['pos'])
                    if 'splash' in attacker:
                        for s_id, s_u in self.state.units.items():
                            if s_id != target and s_u['owner'] != attacker['owner'] and s_u['hp'] > 0:
                                if self.state.get_distance(target_unit['pos'], s_u['pos']) <= 1.5: self.hit_effects.append(s_u['pos'])
                    if 'Pierce' in attacker['behaviors'] or 'Breath' in attacker['behaviors']:
                        dx = target_unit['pos'][0] - attacker['pos'][0]; dy = target_unit['pos'][1] - attacker['pos'][1]
                        if dx != 0: dx = dx // abs(dx)
                        if dy != 0: dy = dy // abs(dy)
                        pierce_pos = (target_unit['pos'][0] + dx, target_unit['pos'][1] + dy)
                        for p_id, p_u in self.state.units.items():
                            if p_u['pos'] == pierce_pos and p_u['owner'] != attacker['owner'] and p_u['hp'] > 0:
                                self.hit_effects.append(p_u['pos'])
                                self.attack_lines.append((target_unit['pos'], p_u['pos'], QColor(255, 100, 100))); break
                        if 'Breath' in attacker['behaviors']:
                            curr_x, curr_y = target_unit['pos']
                            for step in range(1, 4):
                                curr_x += dx; curr_y += dy; hit_something = False
                                for p_id, p_u in self.state.units.items():
                                    if p_u['pos'] == (curr_x, curr_y) and p_u['owner'] != attacker['owner'] and p_u['hp'] > 0:
                                        self.hit_effects.append(p_u['pos'])
                                        self.attack_lines.append((target_unit['pos'], p_u['pos'], QColor(255, 50, 50))); hit_something = True; break
                                if not hit_something:
                                    self.attack_lines.append((target_unit['pos'], (curr_x, curr_y), QColor(255, 50, 50, 100)))
                    if 'Cleave' in attacker['behaviors'] or 'Multi-Head' in attacker['behaviors']:
                        for c_id, c_u in self.state.units.items():
                            if c_id != target and c_u['owner'] != attacker['owner'] and c_u['hp'] > 0:
                                if self.state.get_distance(attacker['pos'], c_u['pos']) <= 1.5:
                                    self.hit_effects.append(c_u['pos'])
                                    self.attack_lines.append((attacker['pos'], c_u['pos'], QColor(255, 50, 50)))
                    self.flash_color = QColor(255, 0, 0, 50)
                    flank_text = " <span style='color:#ff00ff; font-weight:bold;'>FLANK!</span>" if is_flank else ""
                    mark_text = " <span style='color:#ff0000; font-weight:bold;'>MARKED!</span>" if is_marked else ""
                    curse_text = " <span style='color:#9933ff; font-weight:bold;'>CURSED!</span>" if is_cursed else ""
                    crit_text = " <span style='color:#ff0000; font-weight:bold;'>CRIT!</span>" if is_blood_moon else ""
                    multi_text = " <span style='color:#00ffff; font-weight:bold;'>MULTISHOT!</span>" if is_multishot else ""
                    self.log(f"<span style='color: #ff5555;'>💥 {attacker['emoji']} {attacker['class']} attacked {actual_target['emoji']} {actual_target['class']}!{flank_text}{mark_text}{curse_text}{crit_text}{multi_text}</span>")
                    if 'Counter' in actual_target['behaviors'] and actual_target['hp'] > attacker['dmg'] and attacker['rng'] == 1:
                        self.attack_lines.append((actual_target['pos'], attacker['pos'], QColor(255, 165, 0)))
                        self.hit_effects.append(attacker['pos'])
                        self.log(f"<span style='color: #ffaa00;'>⚔️ {actual_target['emoji']} {actual_target['class']} counter-attacked!</span>")
                else:
                    self.log(f"<span style='color: #aaaaaa;'>💨 {attacker['emoji']} {attacker['class']} attacked {actual_target['emoji']} {actual_target['class']} but MISSED!</span>")
                    if 'Riposte' in actual_target['behaviors']:
                        self.attack_lines.append((actual_target['pos'], attacker['pos'], QColor(255, 0, 255)))
                        self.hit_effects.append(attacker['pos'])
                        self.log(f"<span style='color: #ff00ff;'>🗡️ {actual_target['emoji']} {actual_target['class']} riposted the attack!</span>")
                self.effect_timer.start(400)
            elif act_type == 'HEAL':
                healer = self.state.units[unit_id]; target_unit = self.state.units[target]
                self.attack_lines.append((healer['pos'], target_unit['pos'], QColor(50, 255, 50))); self.hit_effects.append(target_unit['pos'])
                self.effect_timer.start(400)
                self.log(f"<span style='color: #55ff55;'>✨ {healer['emoji']} {healer['class']} healed {target_unit['emoji']} {target_unit['class']}!</span>")
            elif act_type == 'HEAL_SELF':
                u = self.state.units[unit_id]
                self.log(f"<span style='color: #55ff55;'>✨ {u['emoji']} {u['class']} healed itself!</span>")
                
            self.state = self.state.apply_action(action)
            if self.state.current_turn != current_player:
                turn_color = "Blue" if self.state.current_turn == 'P1' else "Red"
                self.log(f"--- {turn_color}'s Turn ---")
            if self.state.weather != old_weather:
                self.log(f"<span style='color: #ffaa00; font-weight: bold;'>🌤️ The weather has changed to {self.state.weather}!</span>")
            
        self.timer.start(self.speed_slider.value())
        self.update_ui()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing); painter.setRenderHint(QPainter.TextAntialiasing)
        if self.flash_color: painter.fillRect(self.rect(), self.flash_color)
        font = QFont("Segoe UI Emoji", 16, QFont.Bold); painter.setFont(font)
        widget_width = self.width(); widget_height = self.height()
        grid_size = self.state.grid_size
        cell_size = min(widget_width - 400, widget_height - 50) // grid_size
        offset_x = 20; offset_y = 40 
        
        if not self.state.winner:
            for uid, u in self.state.units.items():
                if u['owner'] == self.state.current_turn and u['hp'] > 0:
                    actions = self.state.get_valid_actions(uid)
                    for act in actions:
                        if act[0] == 'MOVE' or act[0] == 'BLINK':
                            tx, ty = act[2]; px = offset_x + tx * cell_size; py = offset_y + ty * cell_size
                            color = QColor(0, 255, 255, 40) if act[0] == 'BLINK' else QColor(0, 255, 0, 40)
                            painter.setBrush(color); painter.setPen(Qt.NoPen)
                            painter.drawRect(px, py, cell_size, cell_size)
        
        for x in range(grid_size):
            for y in range(grid_size):
                px = offset_x + x * cell_size; py = offset_y + y * cell_size
                if (x + y) % 2 == 0: painter.setBrush(QColor(45, 45, 45))
                else: painter.setBrush(QColor(35, 35, 35))
                painter.setPen(QPen(QColor(20, 20, 20), 1))
                painter.drawRect(px, py, cell_size, cell_size)
                terrain_emoji = self.state.terrain[(x, y)]
                rect = QRectF(px, py - 5, cell_size, cell_size)
                painter.drawText(rect, Qt.AlignCenter, terrain_emoji)
                
        for line in self.attack_lines:
            pos1, pos2, color = line
            p1 = (offset_x + pos1[0] * cell_size + cell_size//2, offset_y + pos1[1] * cell_size + cell_size//2)
            p2 = (offset_x + pos2[0] * cell_size + cell_size//2, offset_y + pos2[1] * cell_size + cell_size//2)
            painter.setPen(QPen(color, 3, Qt.DashLine))
            painter.drawLine(QLineF(p1[0], p1[1], p2[0], p2[1]))
                
        for hx, hy in self.hit_effects:
            px = offset_x + hx * cell_size; py = offset_y + hy * cell_size
            hit_font = QFont("Segoe UI Emoji", 36, QFont.Bold)
            painter.setFont(hit_font)
            painter.drawText(QRectF(px, py - 10, cell_size, cell_size), Qt.AlignCenter, "💥")
            painter.setFont(font) 
            
        for uid, data in self.state.units.items():
            if data['hp'] <= 0: continue
            x, y = data['pos']
            px = offset_x + x * cell_size; py = offset_y + y * cell_size
            if 'aura' in data and self.state.terrain.get(data['pos']) != '🌌':
                painter.setBrush(QBrush(QColor(255, 255, 0, 30)))
                painter.setPen(QPen(QColor(255, 255, 0, 100), 1, Qt.DashLine))
                painter.drawEllipse(QRectF(px+5, py+5, cell_size-10, cell_size-10))
            if self.state.has_cohesion(uid):
                painter.setBrush(QBrush(QColor(0, 255, 255, 20)))
                painter.setPen(QPen(QColor(0, 255, 255, 150), 2))
                painter.drawRoundedRect(px, py, cell_size, cell_size, 8, 8)
            if data['owner'] == self.state.current_turn:
                color = QColor(0, 152, 255) if data['owner'] == 'P1' else QColor(255, 85, 85)
                painter.setPen(QPen(color, 3)); painter.setBrush(Qt.NoBrush)
                painter.drawRoundedRect(px+2, py+2, cell_size-4, cell_size-4, 5, 5)
            painter.setPen(QColor(255, 100, 100))
            text_font = QFont("Arial", 8, QFont.Bold); painter.setFont(text_font)
            status_text = ""
            if 'poison' in data['status']: status_text += "🤢"
            if data['status'].get('marked', 0) > 0: status_text += "🎯"
            if data['status'].get('curse', 0) > 0: status_text += "🔮"
            if data['status'].get('rallied', 0) > 0: status_text += "🚩"
            if data['status'].get('shield', 0) > 0: status_text += "🛡️"
            if data['status'].get('stun', 0) > 0: status_text += "🗿"
            if 'Overwatch' in data['behaviors'] and not data['status'].get('ow_used', False): status_text += "🎯"
            if 'Martyr' in data['behaviors']: status_text += "🧨"
            if 'Taunt' in data['behaviors']: status_text += "📢"
            if 'Terrify' in data['behaviors']: status_text += "😱"
            if 'Stealth' in data['behaviors']: status_text += "👤"
            painter.drawText(QRectF(px, py - 15, cell_size, 15), Qt.AlignCenter, f"❤{data['hp']}{status_text}")
            painter.setPen(QColor(255, 215, 0))
            painter.drawText(QRectF(px, py + cell_size - 12, cell_size, 12), Qt.AlignCenter, f"⚡{data['ap']}")
            painter.setPen(Qt.white); painter.setFont(font) 
            unit_rect = QRectF(px, py - 5, cell_size, cell_size)
            painter.drawText(unit_rect, Qt.AlignCenter, data['emoji'])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BattleCanvas()
    window.show()
    sys.exit(app.exec())