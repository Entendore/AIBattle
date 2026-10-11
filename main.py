#!/usr/bin/env python3
"""
⚔️ AI Battle Arena V20 - Bloodthirst & Tactics Edition
Featuring Overkill bonuses, Dodge counters, Target Leading, Crash damage,
and color-coded damage numbers.
Built with PySide6
"""

import sys
import random
import math
import os
import json
import subprocess
import shutil
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, List, Dict, Tuple, Callable
from datetime import datetime
from collections import deque

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QGroupBox, QGridLayout,
    QSizePolicy, QFileDialog, QMessageBox, QSlider, QCheckBox,
    QProgressDialog, QLineEdit, QTabWidget, QTextEdit, QFrame,
    QScrollArea
)
from PySide6.QtCore import (
    Qt, QTimer, QPointF, QRectF, Signal, QElapsedTimer, QSize
)
from PySide6.QtGui import (
    QPainter, QColor, QPen, QFont, QPainterPath,
    QRadialGradient, QLinearGradient, QPixmap, QPolygonF, QImage,
    QKeySequence, QShortcut
)

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION & DATABASES
# ═══════════════════════════════════════════════════════════════

MAX_PARTICLES = 600
HISTORY_FILE = "battle_history.json"
ACHIEVEMENTS_FILE = "achievements.json"

# Tunable balance constants
BLOCK_DAMAGE_REDUCTION = 0.25
COUNTER_ATTACK_MULT = 0.5
DODGE_CHANCE_BASE = 0.6
RAGE_HP_THRESHOLD = 0.3
RAGE_ATTACK_MULT = 1.5
BUFF_ATTACK_MULT = 1.4
BUFF_DURATION = 5.0
OVERDRIVE_THRESHOLD = 3
OVERDRIVE_MULT = 1.2
HEAL_HP_PERCENT = 0.3
HEAL_MP_COST = 25
BUFF_MP_COST = 30
SPECIAL_MP_COST = 40
LIGHT_MP_GAIN = 15
HEAVY_MP_GAIN = 5
PASSIVE_MP_REGEN = 5
SPECIAL_COOLDOWN = 8.0
HAZARD_INTERVAL = 8.0
HEAL_COOLDOWN_MAX = 6.0
BUFF_COOLDOWN_MAX = 8.0

# Status Effect Durations
SLOW_DURATION = 3.0
SLOW_SPEED_MULT = 0.5
WEAKEN_DURATION = 4.0
WEAKEN_DMG_MULT = 0.6
MARK_DURATION = 3.0
MARK_DMG_BONUS = 1.5
INVINCIBILITY_DURATION = 3.0
SHIELD_DURATION = 4.0
HASTE_DURATION = 4.0
HASTE_SPEED_MULT = 1.6
RAGE_PICKUP_DURATION = 5.0
SLOW_MO_FINISHER_DURATION = 1.5

class CanvasMode(Enum):
    SHORT_9_16 = (540, 960)
    VIDEO_16_9 = (960, 540)
    SQUARE_1_1 = (720, 720)

class ExportQuality(Enum):
    HD_1080P = ("1080p (2x)", 2)
    UHD_4K = ("4K (4x)", 4)

class AIDifficulty(Enum):
    EASY = "Easy"
    NORMAL = "Normal"
    HARD = "Hard"
    NIGHTMARE = "Nightmare"

class DamageType(Enum):
    PHYSICAL = "Physical"
    FIRE = "Fire"
    ICE = "Ice"
    LIGHTNING = "Lightning"
    POISON = "Poison"
    HOLY = "Holy"

CLASSES_DB = {
    "Fighter":      {"emoji": "⚔️", "hp_mult": 1.0,  "atk_mult": 1.0,  "def_mult": 1.0,  "spd_mult": 1.0, "mp_mult": 1.0, "dmg_type": DamageType.PHYSICAL, "resist": {DamageType.PHYSICAL: 1.0}},
    "Mage":         {"emoji": "🔮", "hp_mult": 0.8,  "atk_mult": 1.4,  "def_mult": 0.7,  "spd_mult": 1.1, "mp_mult": 1.5, "dmg_type": DamageType.FIRE, "resist": {DamageType.FIRE: 0.7, DamageType.ICE: 1.3}},
    "Assassin":     {"emoji": "🗡️", "hp_mult": 0.7,  "atk_mult": 1.3,  "def_mult": 0.6,  "spd_mult": 1.5, "mp_mult": 0.8, "dmg_type": DamageType.PHYSICAL, "resist": {DamageType.PHYSICAL: 1.1}},
    "Tank":         {"emoji": "🛡️", "hp_mult": 1.5,  "atk_mult": 0.8,  "def_mult": 1.6,  "spd_mult": 0.6, "mp_mult": 0.7, "dmg_type": DamageType.PHYSICAL, "resist": {DamageType.PHYSICAL: 0.7, DamageType.FIRE: 0.8}},
    "Berserker":    {"emoji": "🪓", "hp_mult": 0.6,  "atk_mult": 1.8,  "def_mult": 0.5,  "spd_mult": 1.3, "mp_mult": 0.5, "dmg_type": DamageType.PHYSICAL, "resist": {DamageType.PHYSICAL: 1.2}},
    "Cleric":       {"emoji": "✝️", "hp_mult": 1.3,  "atk_mult": 1.0,  "def_mult": 1.3,  "spd_mult": 0.8, "mp_mult": 1.4, "dmg_type": DamageType.HOLY, "resist": {DamageType.HOLY: 0.5, DamageType.POISON: 0.7}},
    "Ranger":       {"emoji": "🏹", "hp_mult": 0.9,  "atk_mult": 1.2,  "def_mult": 0.8,  "spd_mult": 1.3, "mp_mult": 0.9, "dmg_type": DamageType.PHYSICAL, "resist": {DamageType.PHYSICAL: 1.0}},
    "Monk":         {"emoji": "🧘", "hp_mult": 0.8,  "atk_mult": 0.9,  "def_mult": 1.4,  "spd_mult": 1.4, "mp_mult": 1.1, "dmg_type": DamageType.PHYSICAL, "resist": {DamageType.PHYSICAL: 0.85, DamageType.FIRE: 0.8}},
    "Brawler":      {"emoji": "👊", "hp_mult": 1.4,  "atk_mult": 1.2,  "def_mult": 1.0,  "spd_mult": 0.8, "mp_mult": 0.6, "dmg_type": DamageType.PHYSICAL, "resist": {DamageType.PHYSICAL: 0.9}},
    "Necromancer":  {"emoji": "💀", "hp_mult": 0.7,  "atk_mult": 1.5,  "def_mult": 0.6,  "spd_mult": 1.0, "mp_mult": 1.6, "dmg_type": DamageType.POISON, "resist": {DamageType.POISON: 0.4, DamageType.HOLY: 1.4}},
    "Samurai":      {"emoji": "🏯", "hp_mult": 1.1,  "atk_mult": 1.3,  "def_mult": 1.1,  "spd_mult": 1.1, "mp_mult": 1.0, "dmg_type": DamageType.PHYSICAL, "resist": {DamageType.PHYSICAL: 0.95}},
    "Engineer":     {"emoji": "🔧", "hp_mult": 1.2,  "atk_mult": 1.0,  "def_mult": 1.4,  "spd_mult": 0.7, "mp_mult": 0.8, "dmg_type": DamageType.LIGHTNING, "resist": {DamageType.LIGHTNING: 0.6, DamageType.FIRE: 0.85}},
    "Alchemist":    {"emoji": "🧪", "hp_mult": 0.9,  "atk_mult": 1.6,  "def_mult": 0.7,  "spd_mult": 0.9, "mp_mult": 1.3, "dmg_type": DamageType.POISON, "resist": {DamageType.POISON: 0.5}},
    "Dragoon":      {"emoji": "🐲", "hp_mult": 1.3,  "atk_mult": 1.4,  "def_mult": 1.2,  "spd_mult": 1.0, "mp_mult": 0.9, "dmg_type": DamageType.PHYSICAL, "resist": {DamageType.FIRE: 0.7}},
    "Paladin":      {"emoji": "⚜️", "hp_mult": 1.4,  "atk_mult": 1.1,  "def_mult": 1.5,  "spd_mult": 0.8, "mp_mult": 1.2, "dmg_type": DamageType.HOLY, "resist": {DamageType.HOLY: 0.5, DamageType.PHYSICAL: 0.85, DamageType.POISON: 0.7}},
    "Warlock":      {"emoji": "👹", "hp_mult": 0.8,  "atk_mult": 1.7,  "def_mult": 0.6,  "spd_mult": 1.0, "mp_mult": 1.5, "dmg_type": DamageType.FIRE, "resist": {DamageType.FIRE: 0.6, DamageType.HOLY: 1.3}},
    "Spellblade":   {"emoji": "🗡️", "hp_mult": 1.0,  "atk_mult": 1.3,  "def_mult": 1.0,  "spd_mult": 1.2, "mp_mult": 1.1, "dmg_type": DamageType.LIGHTNING, "resist": {DamageType.LIGHTNING: 0.7, DamageType.PHYSICAL: 0.9}},
    "Beastmaster":  {"emoji": "🐾", "hp_mult": 1.2,  "atk_mult": 1.2,  "def_mult": 1.1,  "spd_mult": 1.3, "mp_mult": 0.9, "dmg_type": DamageType.PHYSICAL, "resist": {DamageType.PHYSICAL: 0.9, DamageType.ICE: 1.2}},
}

WARRIORS_DB = {
    "Ninja":       {"emoji": "🥷", "hp": 90,  "atk": 16, "def": 6,  "spd": 18, "special": "Shadow Strike",  "special_emoji": "🗡️", "aggression": 0.7,  "color": QColor(150, 150, 150)},
    "Wizard":      {"emoji": "🧙", "hp": 75,  "atk": 22, "def": 4,  "spd": 11, "special": "Fireball",       "special_emoji": "🔥", "aggression": 0.6,  "color": QColor(255, 100, 0)},
    "Knight":      {"emoji": "🛡️", "hp": 110, "atk": 15, "def": 18, "spd": 8,  "special": "Holy Slash",     "special_emoji": "⚔️", "aggression": 0.4,  "color": QColor(255, 255, 200)},
    "Samurai":     {"emoji": "🥋", "hp": 100, "atk": 18, "def": 11, "spd": 13, "special": "Blade Storm",    "special_emoji": "🌀", "aggression": 0.6,  "color": QColor(150, 200, 255)},
    "Vampire":     {"emoji": "🧛", "hp": 95,  "atk": 17, "def": 8,  "spd": 12, "special": "Life Drain",     "special_emoji": "🩸", "aggression": 0.65, "color": QColor(200, 0, 50)},
    "Pirate":      {"emoji": "🏴‍☠️","hp": 100, "atk": 16, "def": 9,  "spd": 10, "special": "Cannon Blast",  "special_emoji": "💣", "aggression": 0.7,  "color": QColor(255, 200, 0)},
    "Superhero":   {"emoji": "🦸", "hp": 125, "atk": 20, "def": 15, "spd": 15, "special": "Hero Slam",      "special_emoji": "💥", "aggression": 0.7,  "color": QColor(0, 150, 255)},
    "Cowboy":      {"emoji": "🤠", "hp": 95,  "atk": 19, "def": 7,  "spd": 12, "special": "Quickdraw",      "special_emoji": "🔫", "aggression": 0.75, "color": QColor(200, 150, 50)},
    "Boxer":       {"emoji": "🥊", "hp": 110, "atk": 17, "def": 12, "spd": 14, "special": "Knockout Punch", "special_emoji": "🥅", "aggression": 0.8,  "color": QColor(255, 100, 100)},
    "Dragon":      {"emoji": "🐉", "hp": 150, "atk": 24, "def": 14, "spd": 6,  "special": "Dragon Breath",  "special_emoji": "🐲", "aggression": 0.5,  "color": QColor(255, 150, 0)},
    "Demon":       {"emoji": "👹", "hp": 115, "atk": 19, "def": 9,  "spd": 9,  "special": "Hellfire",       "special_emoji": "😈", "aggression": 0.8,  "color": QColor(200, 0, 0)},
    "Goblin":      {"emoji": "👺", "hp": 70,  "atk": 14, "def": 5,  "spd": 16, "special": "Sneak Attack",   "special_emoji": "💰", "aggression": 0.75, "color": QColor(100, 200, 50)},
    "Zombie":      {"emoji": "🧟", "hp": 120, "atk": 12, "def": 10, "spd": 4,  "special": "Undead Horde",   "special_emoji": "💀", "aggression": 0.5,  "color": QColor(100, 150, 50)},
    "Alien":       {"emoji": "👽", "hp": 85,  "atk": 20, "def": 6,  "spd": 14, "special": "Mind Blast",     "special_emoji": "🛸", "aggression": 0.6,  "color": QColor(150, 255, 100)},
    "Ghost":       {"emoji": "👻", "hp": 80,  "atk": 18, "def": 3,  "spd": 17, "special": "Phase Shift",    "special_emoji": "🌫️", "aggression": 0.5,  "color": QColor(220, 220, 255)},
    "T-Rex":       {"emoji": "🦖", "hp": 160, "atk": 25, "def": 12, "spd": 9,  "special": "Jaws of Doom",   "special_emoji": "🦷", "aggression": 0.8,  "color": QColor(150, 100, 50)},
    "Fairy":       {"emoji": "🧚", "hp": 70,  "atk": 15, "def": 8,  "spd": 19, "special": "Pixie Dust",     "special_emoji": "✨", "aggression": 0.4,  "color": QColor(255, 150, 255)},
    "Mummy":       {"emoji": "🧟‍♂️","hp": 130, "atk": 14, "def": 14, "spd": 5,  "special": "Sandstorm",      "special_emoji": "🌪️", "aggression": 0.5,  "color": QColor(200, 180, 100)},
    "Genie":       {"emoji": "🧞", "hp": 100, "atk": 21, "def": 9,  "spd": 13, "special": "Wish of Pain",    "special_emoji": "🔮", "aggression": 0.6,  "color": QColor(0, 255, 255)},
    "Kraken":      {"emoji": "🐙", "hp": 140, "atk": 22, "def": 12, "spd": 8,  "special": "Tentacle Slam",  "special_emoji": "🌊", "aggression": 0.6,  "color": QColor(100, 50, 150)},
    "Phoenix":     {"emoji": "🦅", "hp": 110, "atk": 23, "def": 10, "spd": 15, "special": "Rebirth Flames", "special_emoji": "🔥", "aggression": 0.7,  "color": QColor(255, 50, 0)},
    "Golem":       {"emoji": "🗿", "hp": 180, "atk": 18, "def": 20, "spd": 4,  "special": "Boulder Throw",  "special_emoji": "🪨", "aggression": 0.4,  "color": QColor(150, 120, 80)},
    "Mammoth":     {"emoji": "🦣", "hp": 170, "atk": 20, "def": 15, "spd": 6,  "special": "Tusk Charge",    "special_emoji": "🦷", "aggression": 0.5,  "color": QColor(200, 150, 100)},
    "Scorpion":    {"emoji": "🦂", "hp": 95,  "atk": 21, "def": 8,  "spd": 14, "special": "Venom Sting",    "special_emoji": "☣️", "aggression": 0.7,  "color": QColor(180, 50, 50)},
    "Spider":      {"emoji": "🕷️", "hp": 85,  "atk": 19, "def": 6,  "spd": 17, "special": "Web Net",        "special_emoji": "🕸️", "aggression": 0.6,  "color": QColor(50, 50, 50)},
    "Bat":         {"emoji": "🦇", "hp": 75,  "atk": 18, "def": 4,  "spd": 20, "special": "Echolocation",   "special_emoji": "📢", "aggression": 0.5,  "color": QColor(100, 50, 100)},
    "Snake":       {"emoji": "🐍", "hp": 90,  "atk": 20, "def": 7,  "spd": 16, "special": "Venom Spit",     "special_emoji": "💦", "aggression": 0.65, "color": QColor(50, 150, 50)},
    "Gorilla":     {"emoji": "🦍", "hp": 140, "atk": 22, "def": 12, "spd": 9,  "special": "Primal Rampage", "special_emoji": "🍌", "aggression": 0.75, "color": QColor(80, 80, 80)},
    "Lion":        {"emoji": "🦁", "hp": 120, "atk": 20, "def": 11, "spd": 13, "special": "King's Roar",    "special_emoji": "👑", "aggression": 0.7,  "color": QColor(255, 180, 0)},
    "Wolf":        {"emoji": "🐺", "hp": 95,  "atk": 18, "def": 8,  "spd": 17, "special": "Pack Hunter",    "special_emoji": "🐾", "aggression": 0.8,  "color": QColor(120, 120, 120)},
    "Rhino":       {"emoji": "🦏", "hp": 160, "atk": 19, "def": 16, "spd": 8,  "special": "Horn Charge",    "special_emoji": "📯", "aggression": 0.55, "color": QColor(100, 100, 100)},
    "Crocodile":   {"emoji": "🐊", "hp": 130, "atk": 21, "def": 14, "spd": 10, "special": "Death Roll",     "special_emoji": "🦷", "aggression": 0.65, "color": QColor(50, 120, 50)},
    "Shark":       {"emoji": "🦈", "hp": 115, "atk": 23, "def": 9,  "spd": 15, "special": "Frenzy",         "special_emoji": "🩸", "aggression": 0.85, "color": QColor(100, 150, 200)},
    "Boar":        {"emoji": "🐗", "hp": 110, "atk": 19, "def": 10, "spd": 12, "special": "Tusk Smash",     "special_emoji": "💥", "aggression": 0.7,  "color": QColor(150, 100, 50)},
    "Owl":         {"emoji": "🦉", "hp": 80,  "atk": 17, "def": 6,  "spd": 18, "special": "Silent Dive",    "special_emoji": "🌙", "aggression": 0.5,  "color": QColor(150, 100, 50)},
    "Skeleton":    {"emoji": "💀", "hp": 70,  "atk": 16, "def": 5,  "spd": 14, "special": "Bone Throw",     "special_emoji": "🦴", "aggression": 0.6,  "color": QColor(230, 230, 230)},
    "Pumpkin":     {"emoji": "🎃", "hp": 100, "atk": 18, "def": 10, "spd": 8,  "special": "Spooky Scare",    "special_emoji": "👻", "aggression": 0.6,  "color": QColor(255, 150, 0)},
    "Invader":     {"emoji": "👾", "hp": 90,  "atk": 21, "def": 7,  "spd": 13, "special": "Laser Storm",     "special_emoji": "🔫", "aggression": 0.7,  "color": QColor(150, 255, 150)},
    "Unicorn":     {"emoji": "🦄", "hp": 105, "atk": 18, "def": 12, "spd": 16, "special": "Holy Horn",       "special_emoji": "🌈", "aggression": 0.5,  "color": QColor(255, 200, 255)},
    "Mermaid":     {"emoji": "🧜", "hp": 95,  "atk": 19, "def": 8,  "spd": 14, "special": "Siren Song",      "special_emoji": "🎶", "aggression": 0.55, "color": QColor(100, 200, 255)},
    "Mushroom":    {"emoji": "🍄", "hp": 85,  "atk": 16, "def": 12, "spd": 7,  "special": "Spore Cloud",     "special_emoji": "☁️", "aggression": 0.4,  "color": QColor(200, 50, 50)},
    "Cactus":      {"emoji": "🌵", "hp": 125, "atk": 15, "def": 16, "spd": 6,  "special": "Needle Shot",     "special_emoji": "📌", "aggression": 0.45, "color": QColor(50, 150, 50)},
    "Robot":       {"emoji": "🤖", "hp": 130, "atk": 15, "def": 15, "spd": 7,  "special": "Laser Beam",     "special_emoji": "🔫", "aggression": 0.4,  "color": QColor(100, 255, 255)},
    "Cat":         {"emoji": "🐱", "hp": 70,  "atk": 16, "def": 6,  "spd": 19, "special": "Feral Claws",   "special_emoji": "🐾", "aggression": 0.7,  "color": QColor(200, 200, 200)},
    "Dog":         {"emoji": "🐶", "hp": 95,  "atk": 15, "def": 9,  "spd": 13, "special": "Bark Bite",     "special_emoji": "🦷", "aggression": 0.6,  "color": QColor(180, 130, 80)},
    "Frog":        {"emoji": "🐸", "hp": 80,  "atk": 17, "def": 7,  "spd": 15, "special": "Toxic Tongue",  "special_emoji": "👅", "aggression": 0.5,  "color": QColor(50, 200, 50)},
    "Monkey":      {"emoji": "🐵", "hp": 85,  "atk": 18, "def": 6,  "spd": 18, "special": "Banana Barrage","special_emoji": "🍌", "aggression": 0.75, "color": QColor(150, 100, 50)},
    "Parrot":      {"emoji": "🦜", "hp": 75,  "atk": 16, "def": 5,  "spd": 19, "special": "Feather Storm", "special_emoji": "🪶", "aggression": 0.6,  "color": QColor(255, 100, 50)},
    "Turtle":      {"emoji": "🐢", "hp": 150, "atk": 12, "def": 22, "spd": 3,  "special": "Shell Spin",    "special_emoji": "🌀", "aggression": 0.3,  "color": QColor(50, 150, 80)},
    "Snail":       {"emoji": "🐌", "hp": 90,  "atk": 14, "def": 14, "spd": 2,  "special": "Slime Trail",   "special_emoji": "🟢", "aggression": 0.3,  "color": QColor(200, 200, 200)},
    "Bee":         {"emoji": "🐝", "hp": 60,  "atk": 20, "def": 4,  "spd": 21, "special": "Swarm Sting",   "special_emoji": "🩸", "aggression": 0.8,  "color": QColor(255, 220, 0)},
    "Butterfly":   {"emoji": "🦋", "hp": 65,  "atk": 14, "def": 8,  "spd": 20, "special": "Wing Gust",     "special_emoji": "🌬️", "aggression": 0.4,  "color": QColor(150, 100, 255)},
    "Squid":       {"emoji": "🦑", "hp": 100, "atk": 19, "def": 9,  "spd": 12, "special": "Ink Spray",     "special_emoji": "🖋️", "aggression": 0.5,  "color": QColor(200, 50, 200)},
    "Dolphin":     {"emoji": "🐬", "hp": 90,  "atk": 18, "def": 8,  "spd": 18, "special": "Sonar Wave",    "special_emoji": "📢", "aggression": 0.6,  "color": QColor(100, 200, 255)},
    "Whale":       {"emoji": "🐳", "hp": 180, "atk": 18, "def": 15, "spd": 6,  "special": "Tidal Splash",  "special_emoji": "🌊", "aggression": 0.4,  "color": QColor(50, 100, 200)},
    "Clown":       {"emoji": "🤡", "hp": 105, "atk": 17, "def": 9,  "spd": 12, "special": "Laughing Gas",  "special_emoji": "😂", "aggression": 0.7,  "color": QColor(255, 100, 100)},
    "Brain":       {"emoji": "🧠", "hp": 75,  "atk": 24, "def": 5,  "spd": 10, "special": "Mind Control",  "special_emoji": "🧠", "aggression": 0.6,  "color": QColor(255, 150, 150)},
    "Microbe":     {"emoji": "🦠", "hp": 85,  "atk": 16, "def": 10, "spd": 8,  "special": "Cell Division", "special_emoji": "🧬", "aggression": 0.5,  "color": QColor(150, 255, 50)},
    "Supervillain":{"emoji": "🦹", "hp": 120, "atk": 21, "def": 13, "spd": 12, "special": "Death Ray",     "special_emoji": "☢️", "aggression": 0.8,  "color": QColor(100, 0, 150)},
    "Elf":         {"emoji": "🧝", "hp": 90,  "atk": 20, "def": 7,  "spd": 15, "special": "Arrow Volley",   "special_emoji": "🏹", "aggression": 0.6,  "color": QColor(100, 255, 150)},
    "Fencer":      {"emoji": "🤺", "hp": 95,  "atk": 19, "def": 10, "spd": 16, "special": "Lunge Thrust",   "special_emoji": "⚔️", "aggression": 0.7,  "color": QColor(200, 200, 200)},
    "Astronaut":   {"emoji": "👨‍🚀", "hp": 110, "atk": 19, "def": 12, "spd": 10, "special": "Orbital Strike", "special_emoji": "🛰️", "aggression": 0.5, "color": QColor(255, 255, 255)},
    "Yeti":        {"emoji": "🦍", "hp": 165, "atk": 22, "def": 16, "spd": 7,  "special": "Frost Crush",    "special_emoji": "❄️", "aggression": 0.55, "color": QColor(200, 230, 255)},
    "Hydra":       {"emoji": "🐉", "hp": 145, "atk": 21, "def": 13, "spd": 9,  "special": "Triple Bite",   "special_emoji": "🐍", "aggression": 0.65, "color": QColor(80, 130, 60)},
    "Centaur":     {"emoji": "🐎", "hp": 115, "atk": 19, "def": 11, "spd": 16, "special": "Gallop Charge", "special_emoji": "💨", "aggression": 0.6,  "color": QColor(160, 110, 60)},
    "Minotaur":    {"emoji": "🐂", "hp": 155, "atk": 23, "def": 14, "spd": 8,  "special": "Labyrinth Fury","special_emoji": "🪓", "aggression": 0.75, "color": QColor(140, 70, 30)},
    "Griffin":     {"emoji": "🦅", "hp": 120, "atk": 22, "def": 12, "spd": 17, "special": "Sky Dive",      "special_emoji": "🌪️", "aggression": 0.65, "color": QColor(220, 180, 80)},
    "Banshee":     {"emoji": "👻", "hp": 85,  "atk": 22, "def": 5,  "spd": 16, "special": "Death Wail",    "special_emoji": "💀", "aggression": 0.6,  "color": QColor(180, 200, 220)},
    "Gargoyle":    {"emoji": "🗿", "hp": 140, "atk": 19, "def": 17, "spd": 9,  "special": "Stone Curse",   "special_emoji": "🪨", "aggression": 0.5,  "color": QColor(120, 110, 130)},
    "Wraith":      {"emoji": "🌫️", "hp": 95,  "atk": 24, "def": 6,  "spd": 18, "special": "Soul Reap",     "special_emoji": "💀", "aggression": 0.7,  "color": QColor(100, 80, 130)},
    "Cyclops":     {"emoji": "👁️", "hp": 150, "atk": 22, "def": 13, "spd": 8,  "special": "Eye Beam",      "special_emoji": "🔮", "aggression": 0.6,  "color": QColor(180, 150, 120)},
    "Chimera":     {"emoji": "🦁", "hp": 135, "atk": 23, "def": 13, "spd": 12, "special": "Tri-Strike",    "special_emoji": "🔥", "aggression": 0.7,  "color": QColor(200, 120, 50)},
}

ARENAS_DB = {
    "Volcano": {
        "floor": QColor(80, 20, 0), "floor_edge": QColor(255, 100, 0),
        "sky_top": QColor(40, 0, 0), "sky_bot": QColor(10, 0, 0),
        "ambient_emoji": "🌋", "ambient_color": QColor(255, 150, 0),
        "hazard_type": "lava", "hazard_color": QColor(255, 50, 0),
        "stat_modifiers": {"atk_mult": 1.1}, "weather": "ash"
    },
    "Ice Cave": {
        "floor": QColor(0, 50, 100), "floor_edge": QColor(150, 220, 255),
        "sky_top": QColor(0, 20, 40), "sky_bot": QColor(0, 5, 15),
        "ambient_emoji": "❄️", "ambient_color": QColor(200, 230, 255),
        "hazard_type": "ice", "hazard_color": QColor(150, 220, 255),
        "stat_modifiers": {"spd_mult": 0.9}, "weather": "snow"
    },
    "Cosmic Void": {
        "floor": QColor(20, 0, 40), "floor_edge": QColor(150, 0, 255),
        "sky_top": QColor(5, 0, 15), "sky_bot": QColor(0, 0, 5),
        "ambient_emoji": "⭐", "ambient_color": QColor(200, 200, 255),
        "hazard_type": "blackhole", "hazard_color": QColor(150, 0, 255),
        "stat_modifiers": {"mp_mult": 1.2}, "weather": "stars"
    },
    "Cursed Woods": {
        "floor": QColor(20, 30, 10), "floor_edge": QColor(100, 50, 0),
        "sky_top": QColor(10, 15, 5), "sky_bot": QColor(5, 10, 0),
        "ambient_emoji": "🕸️", "ambient_color": QColor(150, 255, 150),
        "hazard_type": "poison_swamp", "hazard_color": QColor(150, 50, 200),
        "stat_modifiers": {"def_mult": 0.9}, "weather": "fog"
    },
    "Sunken Ruins": {
        "floor": QColor(150, 100, 50), "floor_edge": QColor(255, 200, 100),
        "sky_top": QColor(200, 150, 50), "sky_bot": QColor(100, 50, 10),
        "ambient_emoji": "🏜️", "ambient_color": QColor(255, 200, 100),
        "hazard_type": "sandstorm", "hazard_color": QColor(200, 180, 100),
        "stat_modifiers": {"spd_mult": 1.1, "hp_mult": 0.9}, "weather": "sand"
    },
    "Neo-Tokyo": {
        "floor": QColor(20, 20, 30), "floor_edge": QColor(0, 255, 255),
        "sky_top": QColor(10, 0, 20), "sky_bot": QColor(30, 0, 60),
        "ambient_emoji": "🏙️", "ambient_color": QColor(100, 255, 255),
        "hazard_type": "laser_grid", "hazard_color": QColor(255, 0, 100),
        "stat_modifiers": {"def_mult": 1.1}, "weather": "rain"
    },
    "Thunder Peak": {
        "floor": QColor(50, 50, 70), "floor_edge": QColor(255, 255, 0),
        "sky_top": QColor(30, 30, 50), "sky_bot": QColor(15, 15, 30),
        "ambient_emoji": "⚡", "ambient_color": QColor(255, 255, 100),
        "hazard_type": "lightning", "hazard_color": QColor(255, 255, 0),
        "stat_modifiers": {"atk_mult": 1.15, "spd_mult": 1.05}, "weather": "rain"
    },
    "Frozen Wastes": {
        "floor": QColor(100, 130, 160), "floor_edge": QColor(220, 240, 255),
        "sky_top": QColor(80, 100, 130), "sky_bot": QColor(40, 60, 90),
        "ambient_emoji": "❄️", "ambient_color": QColor(220, 240, 255),
        "hazard_type": "blizzard", "hazard_color": QColor(220, 240, 255),
        "stat_modifiers": {"spd_mult": 0.85, "def_mult": 1.1}, "weather": "snow"
    },
    "Shadow Realm": {
        "floor": QColor(30, 0, 30), "floor_edge": QColor(150, 0, 150),
        "sky_top": QColor(10, 0, 10), "sky_bot": QColor(0, 0, 0),
        "ambient_emoji": "🌑", "ambient_color": QColor(150, 0, 200),
        "hazard_type": "void", "hazard_color": QColor(150, 0, 200),
        "stat_modifiers": {"mp_mult": 1.3, "hp_mult": 0.95}, "weather": "void"
    },
}

OBSTACLE_TEMPLATES = {
    "Volcano":       [("rock", "🪨", QColor(80, 60, 50)), ("lava_pool", "🌋", QColor(200, 60, 0)), ("bone", "🦴", QColor(220, 220, 200))],
    "Ice Cave":      [("ice_pillar", "🧊", QColor(150, 220, 255)), ("frozen_rock", "🪨", QColor(180, 200, 230)), ("crystal", "💎", QColor(200, 240, 255))],
    "Cosmic Void":   [("asteroid", "☄️", QColor(120, 100, 140)), ("crystal", "💎", QColor(180, 100, 255)), ("planet", "🪐", QColor(200, 150, 100))],
    "Cursed Woods":  [("tree", "🌲", QColor(40, 80, 30)), ("tombstone", "🪦", QColor(120, 120, 120)), ("log", "🪵", QColor(100, 70, 40))],
    "Sunken Ruins":  [("pillar", "🏛️", QColor(200, 180, 130)), ("rock", "🪨", QColor(150, 130, 100)), ("urn", "🏺", QColor(180, 140, 90))],
    "Neo-Tokyo":     [("building", "🏢", QColor(80, 100, 140)), ("neon_barrier", "🚧", QColor(0, 255, 255)), ("crate", "📦", QColor(180, 140, 80))],
    "Thunder Peak":  [("lightning_rod", "📡", QColor(180, 180, 200)), ("rock", "🪨", QColor(100, 100, 120)), ("totem", "🗿", QColor(80, 80, 100))],
    "Frozen Wastes": [("iceberg", "🧊", QColor(180, 220, 255)), ("frozen_tree", "🌲", QColor(150, 180, 200)), ("rock", "🪨", QColor(120, 140, 160))],
    "Shadow Realm":  [("dark_crystal", "💎", QColor(100, 0, 150)), ("tombstone", "🪦", QColor(80, 50, 80)), ("shadow_rock", "🪨", QColor(60, 30, 60))],
}

ACTION_PHRASES = {
    "LIGHT_ATTACK": ["Hyah!", "Take this!", "Strike!", "Hah!", "Punch!", "Slice!", "Swing!", "Bop!", "Smack!", "Hit!"],
    "HEAVY_ATTACK": ["Die!", "Crush!", "Heavy blow!", "Eradicate!", "Smash!", "Destroy!", "Unleash!", "Wreck!", "Pulverize!", "Decimate!"],
    "SPECIAL": ["Special move!", "Feel my power!", "Ultimate attack!", "Take this!", "Finisher!", "Overdrive!", "Limit break!", "Apocalypse!"],
    "BLOCK": ["Guard!", "Block!", "Not a chance!", "Defend!", "Shield!", "Nope!", "Protect!", "Brace!"],
    "DODGE": ["Too slow!", "Miss me!", "Dodge!", "Whoosh!", "Swift!", "Evade!", "Out of the way!", "Zoom!"],
    "HEAL": ["Heal!", "Recover!", "Health!", "Restore!", "Mend!", "Vitality!", "Recuperate!", "Bind!"],
    "BUFF": ["Power up!", "Unleash!", "Strengthen!", "Focus!", "Gather strength!", "Empower!", "Charge up!", "Enrage!"]
}

CONTEXTUAL_BARKS = {
    "low_hp": ["I'm not done yet!", "Is that all?", "Pushing through!", "Feel the pain!"],
    "high_combo": ["Combo time!", "Can't touch this!", "Flawless!", "Ezpz!"],
    "enemy_low_hp": ["Finish him!", "Rest in peace!", "Sayonara!", "The end!"],
    "marked": ["I'm marked!", "Watch out!", "They're targeting me!", "Careful!"],
    "invincible": ["Untouchable!", "Can't touch me!", "Invincible!", "Haha!"]
}

COMMENTARY_PHRASES = {
    "first_blood": ["First blood drawn!", "The battle begins in earnest!"],
    "big_hit": ["Massive hit!", "Devastating blow!", "What an impact!"],
    "comeback": ["What a comeback!", "They're not giving up!"],
    "combo_5": ["INCREDIBLE COMBO!", "The crowd goes wild!"],
    "dodge_master": ["Matrix-level dodge!", "Incredible reflexes!"],
    "block_master": ["Impeccable defense!", "Wall of steel!"],
    "low_hp_clutch": ["Clutch moment!", "Heart-pounding action!"],
}

ACHIEVEMENTS_DB = {
    "first_win":          {"name": "First Victory", "desc": "Win your first battle", "emoji": "🥇"},
    "win_streak_3":       {"name": "Hat Trick", "desc": "Win 3 battles in a row", "emoji": "🎩"},
    "win_streak_5":       {"name": "Unstoppable", "desc": "Win 5 battles in a row", "emoji": "🔥"},
    "big_dmg":            {"name": "Big Damage", "desc": "Deal 100+ damage in one battle", "emoji": "💥"},
    "combo_master":       {"name": "Combo Master", "desc": "Achieve a 5+ hit combo", "emoji": "🔗"},
    "dodge_master":       {"name": "Matrix Dodge", "desc": "Dodge 5+ times in one battle", "emoji": "🌀"},
    "block_master":       {"name": "Wall of Steel", "desc": "Block 5+ times in one battle", "emoji": "🛡️"},
    "comeback_king":      {"name": "Comeback King", "desc": "Win with less than 10% HP", "emoji": "👑"},
    "specialist":         {"name": "Specialist", "desc": "Use 3+ specials in one battle", "emoji": "✨"},
    "untouchable":        {"name": "Untouchable", "desc": "Win without taking damage", "emoji": "💫"},
    "tournament_champ":   {"name": "Tournament Champion", "desc": "Win an 8-warrior tournament", "emoji": "🏆"},
    "mark_and_finish":    {"name": "Marked for Death", "desc": "Defeat a marked enemy", "emoji": "🎯"},
}

RANGED_CLASSES = {"Mage", "Ranger", "Necromancer", "Engineer", "Alchemist", "Warlock", "Spellblade"}

# ═══════════════════════════════════════════════════════════════
# DATACLASSES & ENUMS
# ═══════════════════════════════════════════════════════════════

class BattlePhase(Enum):
    IDLE = auto(); INTRO = auto(); COUNTDOWN = auto()
    BATTLE = auto(); ACTION_ANIM = auto(); VICTORY = auto()
    PAUSED = auto()

class ActionType(Enum):
    LIGHT_ATTACK = auto(); HEAVY_ATTACK = auto(); SPECIAL = auto()
    BLOCK = auto(); DODGE = auto()
    HEAL = auto(); BUFF = auto()

@dataclass
class Particle:
    x: float; y: float; vx: float; vy: float
    life: float; max_life: float; color: QColor; size: float
    emoji: str = ""; gravity: float = 400.0; shape: str = "circle"
    shrink: bool = True; rotation: float = 0.0; vr: float = 0.0

@dataclass
class SlashEffect:
    x: float; y: float; angle: float; life: float; max_life: float
    color: QColor; length: float = 80.0; width: float = 10.0

@dataclass
class ShockwaveEffect:
    x: float; y: float; life: float; max_life: float
    color: QColor; max_radius: float = 60.0; width: float = 5.0

@dataclass
class HazardEffect:
    x: float; y: float
    timer: float; phase: str
    hazard_type: str
    color: QColor

@dataclass
class Obstacle:
    x: float; y: float; radius: float
    obstacle_type: str; emoji: str; color: QColor
    hp: int = 50
    max_hp: int = 50
    rotation: float = 0.0
    hit_flash: float = 0.0

@dataclass
class Projectile:
    x: float; y: float; vx: float; vy: float
    damage: int; life: float; max_life: float
    color: QColor; emoji: str; size: float
    owner: 'Warrior'
    trail_timer: float = 0.0
    is_special: bool = False
    damage_type: DamageType = DamageType.PHYSICAL

@dataclass
class Pickup:
    x: float; y: float
    pickup_type: str
    emoji: str
    color: QColor
    life: float = 15.0
    bob_offset: float = 0.0

@dataclass
class FloatingText:
    x: float; y: float; text: str; color: QColor
    life: float; max_life: float; vy: float = -80.0; size: int = 28
    is_speech: bool = False
    is_commentary: bool = False

@dataclass
class BattleStats:
    damage_dealt: int = 0
    damage_taken: int = 0
    crits: int = 0
    dodges: int = 0
    blocks: int = 0
    specials_used: int = 0
    heals_used: int = 0
    max_combo: int = 0
    pickups_collected: int = 0
    damage_by_type: Dict[DamageType, int] = field(default_factory=dict)

@dataclass
class Warrior:
    name: str; emoji: str; class_name: str; max_hp: int; hp: int
    attack: int; defense: int; speed: int
    special_name: str; special_emoji: str; aggression: float; color: QColor
    side: int; x: float = 0.0; y: float = 0.0
    home_x: float = 0.0; home_y: float = 0.0; scale: float = 1.0
    
    target_x: float = 0.0
    target_y: float = 0.0
    vx: float = 0.0
    vy: float = 0.0
    facing_angle: float = 0.0
    move_state: str = "IDLE"
    move_repath_timer: float = 0.0
    strafe_dir: int = 1
    walk_bob: float = 0.0
    
    blocking: bool = False; dodging: bool = False
    special_cooldown: float = 0.0; hit_flash: float = 0.0
    is_winner: bool = False; alpha: float = 1.0
    stun_timer: float = 0.0; poison_timer: float = 0.0; combo: int = 0
    displayed_hp: float = 0.0
    is_enraged: bool = False
    buff_timer: float = 0.0
    heal_cooldown: float = 0.0
    buff_cooldown: float = 0.0

    max_mp: int = 100
    mp: int = 100
    displayed_mp: float = 100.0

    base_attack: int = 0
    guard_up: bool = False       
    dodge_ready: bool = False    

    burn_timer: float = 0.0
    freeze_timer: float = 0.0
    knockback_x: float = 0.0
    knockback_y: float = 0.0
    hit_stumble: float = 0.0
    overdrive_timer: float = 0.0
    
    slow_timer: float = 0.0
    weaken_timer: float = 0.0
    mark_timer: float = 0.0
    invincibility_timer: float = 0.0
    shield_timer: float = 0.0
    haste_timer: float = 0.0
    rage_pickup_timer: float = 0.0
    _crash_cooldown: float = 0.0

    stats: BattleStats = field(default_factory=BattleStats)
    damage_type: DamageType = DamageType.PHYSICAL
    resistances: Dict[DamageType, float] = field(default_factory=lambda: {DamageType.PHYSICAL: 1.0})
    
    _rebirth_used: bool = False
    first_blood_dealt: bool = False

    @classmethod
    def from_db(cls, name: str, class_name: str, side: int):
        data = WARRIORS_DB[name]
        c_mod = CLASSES_DB[class_name]
        max_hp = int(data["hp"] * c_mod["hp_mult"])
        attack = int(data["atk"] * c_mod["atk_mult"])
        defense = int(data["def"] * c_mod["def_mult"])
        speed = int(data["spd"] * c_mod["spd_mult"])
        max_mp = int(100 * c_mod["mp_mult"])
        w = cls(name=name, emoji=data["emoji"], class_name=class_name, max_hp=max_hp, hp=max_hp,
                attack=attack, defense=defense, speed=speed,
                special_name=data["special"], special_emoji=data["special_emoji"],
                aggression=data["aggression"], color=data["color"], side=side,
                max_mp=max_mp, mp=max_mp, base_attack=attack,
                damage_type=c_mod.get("dmg_type", DamageType.PHYSICAL),
                resistances=c_mod.get("resist", {DamageType.PHYSICAL: 1.0}).copy())
        w.displayed_hp = float(w.max_hp)
        w.displayed_mp = float(w.max_mp)
        return w

    def apply_arena_modifiers(self, mods: dict):
        if "hp_mult" in mods:
            self.max_hp = int(self.max_hp * mods["hp_mult"])
            self.hp = self.max_hp
            self.displayed_hp = float(self.hp)
        if "atk_mult" in mods:
            self.base_attack = int(self.base_attack * mods["atk_mult"])
            self.recalculate_attack()
        if "def_mult" in mods:
            self.defense = int(self.defense * mods["def_mult"])
        if "spd_mult" in mods:
            self.speed = int(self.speed * mods["spd_mult"])
        if "mp_mult" in mods:
            self.max_mp = int(self.max_mp * mods["mp_mult"])
            self.mp = self.max_mp
            self.displayed_mp = float(self.mp)

    @property
    def hp_percent(self): return max(0.0, self.hp / self.max_hp)
    @property
    def mp_percent(self): return max(0.0, self.mp / self.max_mp)
    @property
    def is_alive(self): return self.hp > 0
    @property
    def is_invincible(self): return self.invincibility_timer > 0
    @property
    def is_shielded(self): return self.shield_timer > 0
    @property
    def is_hasted(self): return self.haste_timer > 0
    @property
    def is_slowed(self): return self.slow_timer > 0
    @property
    def is_weakened(self): return self.weaken_timer > 0
    @property
    def is_marked(self): return self.mark_timer > 0

    def get_effective_attack(self) -> int:
        atk = self.base_attack
        if self.is_enraged: atk = int(atk * RAGE_ATTACK_MULT)
        if self.buff_timer > 0: atk = int(atk * BUFF_ATTACK_MULT)
        if self.overdrive_timer > 0: atk = int(atk * OVERDRIVE_MULT)
        if self.freeze_timer > 0: atk = int(atk * 0.5)
        if self.weaken_timer > 0: atk = int(atk * WEAKEN_DMG_MULT)
        if self.rage_pickup_timer > 0: atk = int(atk * 1.6)
        return atk

    def get_effective_speed(self) -> int:
        spd = self.speed
        if self.slow_timer > 0: spd = int(spd * SLOW_SPEED_MULT)
        if self.haste_timer > 0: spd = int(spd * HASTE_SPEED_MULT)
        if self.freeze_timer > 0: spd = int(spd * 0.3)
        return spd

    def get_damage_modifier(self, incoming_type: DamageType) -> float:
        mod = self.resistances.get(incoming_type, 1.0)
        if self.mark_timer > 0: mod *= MARK_DMG_BONUS
        if self.invincibility_timer > 0: mod = 0.0
        if self.shield_timer > 0: mod *= 0.5
        return mod

    def recalculate_attack(self):
        self.attack = self.get_effective_attack()

    def calculate_utility(self, action: ActionType, enemy: 'Warrior', difficulty: AIDifficulty = AIDifficulty.NORMAL) -> float:
        score = 0.0
        hp_ratio = self.hp / self.max_hp
        enemy_hp_ratio = enemy.hp / enemy.max_hp
        mp_ratio = self.mp / self.max_mp

        rand_range = {AIDifficulty.EASY: 30.0, AIDifficulty.NORMAL: 10.0,
                      AIDifficulty.HARD: 5.0, AIDifficulty.NIGHTMARE: 1.0}[difficulty]
        difficulty_mod = {AIDifficulty.EASY: 0.7, AIDifficulty.NORMAL: 1.0,
                          AIDifficulty.HARD: 1.15, AIDifficulty.NIGHTMARE: 1.3}[difficulty]

        dmg_effectiveness = enemy.get_damage_modifier(self.damage_type)
        if dmg_effectiveness > 1.0: score += 15.0
        elif dmg_effectiveness < 1.0: score -= 10.0

        if action == ActionType.HEAL:
            if self.mp < HEAL_MP_COST or self.heal_cooldown > 0: return 0.0
            if hp_ratio > 0.7: return 0.0
            score = 80.0 * (1.0 - (hp_ratio / 0.7))
            if enemy_hp_ratio < 0.2: score *= 0.1
            if self.is_marked: score += 30.0
        elif action == ActionType.BUFF:
            if self.mp < BUFF_MP_COST or self.buff_timer > 0 or self.buff_cooldown > 0: return 0.0
            score = 40.0 + (40.0 * hp_ratio)
            if enemy_hp_ratio < 0.5: score *= 0.3
        elif action == ActionType.SPECIAL:
            if self.mp < SPECIAL_MP_COST or self.special_cooldown > 0: return 0.0
            score = 40.0 + (60.0 * (1.0 - enemy_hp_ratio))
            if enemy.guard_up: score += 30.0
            if self.is_enraged: score += 20.0
            if enemy_hp_ratio < 0.1: score *= 0.5
            if dmg_effectiveness > 1.2: score += 25.0
        elif action == ActionType.HEAVY_ATTACK:
            score = 40.0 * self.aggression
            if enemy.guard_up: score += 40.0
            if enemy_hp_ratio < 0.3: score += 50.0
            if self.combo >= 2: score += 15.0
            if dmg_effectiveness > 1.2: score += 20.0
        elif action == ActionType.LIGHT_ATTACK:
            score = 50.0 * self.aggression
            if mp_ratio < 0.8: score += 20.0
            if enemy.guard_up: score *= 0.2
            if enemy_hp_ratio < 0.4 and enemy.mp >= HEAL_MP_COST: score += 25.0
        elif action == ActionType.BLOCK:
            score = 20.0
            if hp_ratio < 0.4: score += 40.0
            if enemy.is_enraged: score += 30.0
            if self.defense > 15: score += 15.0
            if enemy.mp >= SPECIAL_MP_COST and enemy.special_cooldown <= 0: score += 25.0
            if enemy_hp_ratio < 0.3: score *= 0.3
            if self.is_marked: score += 35.0
        elif action == ActionType.DODGE:
            score = 15.0
            if hp_ratio < 0.4: score += 30.0
            if self.speed > 14: score += 25.0
            if enemy.guard_up: score -= 20.0
            if enemy.mp >= SPECIAL_MP_COST and enemy.special_cooldown <= 0: score += 20.0
            if self.is_marked: score += 25.0

        score *= difficulty_mod
        score += random.uniform(-rand_range, rand_range)
        return max(0.0, score)

    def decide_action(self, enemy: 'Warrior', difficulty: AIDifficulty = AIDifficulty.NORMAL) -> ActionType:
        if self.stun_timer > 0 or self.freeze_timer > 0: return ActionType.BLOCK
        scores = {a: self.calculate_utility(a, enemy, difficulty) for a in ActionType}
        best_action = max(scores, key=scores.get)
        if best_action == ActionType.HEAL and (self.mp < HEAL_MP_COST or self.heal_cooldown > 0): best_action = ActionType.LIGHT_ATTACK
        if best_action == ActionType.BUFF and (self.mp < BUFF_MP_COST or self.buff_cooldown > 0): best_action = ActionType.LIGHT_ATTACK
        if best_action == ActionType.SPECIAL and (self.mp < SPECIAL_MP_COST or self.special_cooldown > 0): best_action = ActionType.LIGHT_ATTACK
        return best_action


# ═══════════════════════════════════════════════════════════════
# MANAGERS (History, Achievements, Tournament, Odds)
# ═══════════════════════════════════════════════════════════════

class MatchHistory:
    def __init__(self):
        self.history: Dict[str, Dict[str, int]] = {}
        self.load()

    def load(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r") as f: self.history = json.load(f)
            except: self.history = {}

    def save(self):
        try:
            with open(HISTORY_FILE, "w") as f: json.dump(self.history, f, indent=2)
        except: pass

    def record_battle(self, winner_name: str, loser_name: str):
        for name, is_win in [(winner_name, True), (loser_name, False)]:
            if name not in self.history: self.history[name] = {"wins": 0, "losses": 0}
            if is_win: self.history[name]["wins"] += 1
            else: self.history[name]["losses"] += 1
        self.save()

    def get_win_rate(self, name: str) -> float:
        if name in self.history:
            h = self.history[name]
            total = h["wins"] + h["losses"]
            return (h["wins"] / total) if total > 0 else 0.5
        return 0.5

class AchievementsManager:
    def __init__(self):
        self.unlocked: Dict[str, str] = {}
        self.load()

    def load(self):
        if os.path.exists(ACHIEVEMENTS_FILE):
            try:
                with open(ACHIEVEMENTS_FILE, "r") as f: self.unlocked = json.load(f)
            except: self.unlocked = {}

    def save(self):
        try:
            with open(ACHIEVEMENTS_FILE, "w") as f: json.dump(self.unlocked, f, indent=2)
        except: pass

    def unlock(self, achievement_id: str) -> bool:
        if achievement_id in ACHIEVEMENTS_DB and achievement_id not in self.unlocked:
            self.unlocked[achievement_id] = datetime.now().isoformat()
            self.save()
            return True
        return False

    def get_recently_unlocked(self) -> List[Tuple[str, dict]]:
        recent = []
        now = datetime.now()
        for aid, ts_str in self.unlocked.items():
            try:
                ts = datetime.fromisoformat(ts_str)
                if (now - ts).total_seconds() < 60:
                    recent.append((aid, ACHIEVEMENTS_DB[aid]))
            except: pass
        return recent

    def get_progress(self) -> Tuple[int, int]:
        return (len(self.unlocked), len(ACHIEVEMENTS_DB))

@dataclass
class TournamentMatch:
    w1: str; w2: str; winner: Optional[str] = None; c1: str = "Fighter"; c2: str = "Fighter"

@dataclass
class TournamentState:
    participants: List[str] = field(default_factory=list)
    classes: Dict[str, str] = field(default_factory=dict)
    bracket: List[List[TournamentMatch]] = field(default_factory=list)
    current_round: int = 0
    current_match: int = 0
    champion: Optional[str] = None
    
    def is_complete(self) -> bool:
        return self.champion is not None

class TournamentManager:
    def __init__(self, achievements: AchievementsManager):
        self.state = TournamentState()
        self.achievements = achievements
        self.active = False

    def start_tournament(self, participants: List[str], classes: Dict[str, str]):
        random.shuffle(participants)
        self.state = TournamentState(
            participants=participants.copy(),
            classes=classes.copy()
        )
        round1 = []
        for i in range(0, len(participants), 2):
            if i+1 < len(participants):
                w1 = participants[i]
                w2 = participants[i+1]
                c1 = classes.get(w1, "Fighter")
                c2 = classes.get(w2, "Fighter")
                round1.append(TournamentMatch(w1=w1, w2=w2, c1=c1, c2=c2))
        self.state.bracket = [round1]
        self.state.current_round = 0
        self.state.current_match = 0
        self.active = True

    def get_current_match(self) -> Optional[TournamentMatch]:
        if not self.active or self.state.is_complete(): return None
        if self.state.current_round >= len(self.state.bracket): return None
        round_matches = self.state.bracket[self.state.current_round]
        if self.state.current_match >= len(round_matches): return None
        return round_matches[self.state.current_match]

    def record_result(self, winner_name: str, loser_name: str):
        match = self.get_current_match()
        if not match: return
        match.winner = winner_name

        self.state.current_match += 1
        round_matches = self.state.bracket[self.state.current_round]
        
        if self.state.current_match >= len(round_matches):
            winners = [m.winner for m in round_matches if m.winner]
            if len(winners) == 1:
                self.state.champion = winners[0]
                self.active = False
                self.achievements.unlock("tournament_champ")
            else:
                next_round = []
                for i in range(0, len(winners), 2):
                    if i+1 < len(winners):
                        w1, w2 = winners[i], winners[i+1]
                        next_round.append(TournamentMatch(
                            w1=w1, w2=w2,
                            c1=self.state.classes.get(w1, "Fighter"),
                            c2=self.state.classes.get(w2, "Fighter")
                        ))
                self.state.bracket.append(next_round)
                self.state.current_round += 1
                self.state.current_match = 0

    def get_bracket_text(self) -> str:
        if not self.state.bracket: return "No tournament active."
        lines = []
        for r, matches in enumerate(self.state.bracket):
            round_name = f"Round {r+1}" if r < len(self.state.bracket)-1 else "Final"
            if r == len(self.state.bracket)-1 and len(matches) == 1: round_name = "FINAL"
            elif r == len(self.state.bracket)-2 and len(matches) == 2: round_name = "Semifinals"
            elif r == 0 and len(matches) == 4: round_name = "Quarterfinals"
            lines.append(f"\n=== {round_name} ===")
            for i, m in enumerate(matches):
                marker = "▶ " if (r == self.state.current_round and i == self.state.current_match) else "  "
                w1_marker = "✅" if m.winner == m.w1 else ("  " if m.winner else "  ")
                w2_marker = "✅" if m.winner == m.w2 else ("  " if m.winner else "  ")
                lines.append(f"{marker}{w1_marker} {m.w1} vs {m.w2} {w2_marker}")
        if self.state.champion:
            lines.append(f"\n🏆 CHAMPION: {self.state.champion} 🏆")
        return "\n".join(lines)

class WinOddsCalculator:
    @staticmethod
    def calculate(w1: Warrior, w2: Warrior, history: MatchHistory) -> Tuple[float, float, str]:
        w1_score = w1.hp * 1.0 + w1.attack * 3.0 + w1.defense * 2.0 + w1.speed * 2.5 + w1.max_mp * 0.3
        w2_score = w2.hp * 1.0 + w2.attack * 3.0 + w2.defense * 2.0 + w2.speed * 2.5 + w2.max_mp * 0.3
        
        w1_dmg_mod_vs_w2 = w2.get_damage_modifier(w1.damage_type)
        w2_dmg_mod_vs_w1 = w1.get_damage_modifier(w2.damage_type)
        w1_score *= w1_dmg_mod_vs_w2
        w2_score *= w2_dmg_mod_vs_w1
        
        w1_wr = history.get_win_rate(w1.name)
        w2_wr = history.get_win_rate(w2.name)
        if w1_wr != 0.5 or w2_wr != 0.5:
            w1_score *= (0.7 + w1_wr * 0.6)
            w2_score *= (0.7 + w2_wr * 0.6)
        
        total = w1_score + w2_score + 0.001
        w1_prob = w1_score / total
        w2_prob = w2_score / total
        
        analysis_parts = []
        if w1_dmg_mod_vs_w2 > 1.1:
            analysis_parts.append(f"{w1.name}'s {w1.damage_type.value} exploits {w2.name}'s weakness")
        elif w1_dmg_mod_vs_w2 < 0.9:
            analysis_parts.append(f"{w2.name} resists {w1.name}'s {w1.damage_type.value}")
        if w2_dmg_mod_vs_w1 > 1.1:
            analysis_parts.append(f"{w2.name}'s {w2.damage_type.value} exploits {w1.name}'s weakness")
        elif w2_dmg_mod_vs_w1 < 0.9:
            analysis_parts.append(f"{w1.name} resists {w2.name}'s {w2.damage_type.value}")
        
        if w1.speed > w2.speed + 3: analysis_parts.append(f"{w1.name} is much faster")
        elif w2.speed > w1.speed + 3: analysis_parts.append(f"{w2.name} is much faster")
        if w1.hp > w2.hp + 30: analysis_parts.append(f"{w1.name} has more HP")
        elif w2.hp > w1.hp + 30: analysis_parts.append(f"{w2.name} has more HP")
        
        analysis = " | ".join(analysis_parts) if analysis_parts else "Evenly matched!"
        return w1_prob, w2_prob, analysis


# ═══════════════════════════════════════════════════════════════
# BATTLE ARENA WIDGET
# ═══════════════════════════════════════════════════════════════

class BattleArena(QWidget):
    battle_log_updated = Signal(str)
    battle_ended = Signal(str, str)
    request_next_battle = Signal()
    stats_updated = Signal()
    achievement_unlocked = Signal(str, str, str)
    commentary_triggered = Signal(str)

    ATTACK_RANGE_MELEE = 85.0

    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(400, 400)
        
        self.warrior1: Optional[Warrior] = None
        self.warrior2: Optional[Warrior] = None
        self.phase = BattlePhase.IDLE
        self.previous_phase = BattlePhase.IDLE
        self.current_arena = "Volcano"

        self.particles: List[Particle] = []
        self.floating_texts: List[FloatingText] = []
        self.slashes: List[SlashEffect] = []
        self.shockwaves: List[ShockwaveEffect] = []
        self.hazards: List[HazardEffect] = []
        self.obstacles: List[Obstacle] = []
        self.projectiles: List[Projectile] = []
        self.pickups: List[Pickup] = []
        self.battle_log: List[str] = []

        self.shake_amount = 0.0; self.flash_amount = 0.0
        self.flash_color = QColor(255, 255, 255)
        self.phase_timer = 0.0; self.countdown_value = 3; self.intro_timer = 0.0
        self.hazard_spawn_timer = HAZARD_INTERVAL
        self.pickup_spawn_timer = 10.0

        self.current_action: Optional[ActionType] = None
        self.action_timer = 0.0; self.action_duration = 1.0
        self.attacker: Optional[Warrior] = None
        self.defender: Optional[Warrior] = None
        self.action_data: Dict = {}
        self.special_banner_text = ""; self.special_banner_timer = 0.0

        self.winner_name = ""; self.loser_name = ""; self.turn_count = 0
        self.hit_stop_timer = 0.0
        self.camera_zoom = 1.0; self.target_camera_zoom = 1.0
        self.watermark_text = "@YourChannel"

        self.auto_queue = False
        self.speed_multiplier = 1.0
        self.ai_difficulty = AIDifficulty.NORMAL

        self.canvas_mode = CanvasMode.SHORT_9_16
        self.show_safe_zones = False
        
        self.slow_mo_timer = 0.0
        self.slow_mo_active = False
        
        self.achievements = AchievementsManager()
        self.history = MatchHistory()
        self.tournament = TournamentManager(self.achievements)
        
        self.w1_odds = 0.5; self.w2_odds = 0.5; self.odds_analysis = ""
        self.last_commentary_timer = 0.0
        self.first_blood_done = False

        self.logical_w, self.logical_h = self.canvas_mode.value
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        self.timer.start(16)

        self.elapsed = QElapsedTimer()
        self.elapsed.start()
        self.last_time = 0
        self.ambient_timer = 0.0
        self.weather_timer = 0.0

        self.bg_cache = None
        self.star_path = self.create_star_path(5)
        self.apply_canvas_mode(self.canvas_mode)

    def apply_canvas_mode(self, mode: CanvasMode):
        self.canvas_mode = mode
        self.logical_w, self.logical_h = mode.value
        self.floor_top = self.logical_h * 0.30
        self.floor_bottom = self.logical_h * 0.88
        self.floor_left = self.logical_w * 0.06
        self.floor_right = self.logical_w * 0.94
        self.generate_background_cache()
        if self.warrior1 and self.warrior2:
            self.setup_battle(self.warrior1.name, self.warrior1.class_name, 
                              self.warrior2.name, self.warrior2.class_name, self.current_arena)
        self.update()

    def create_star_path(self, size):
        path = QPainterPath()
        for i in range(5):
            angle = (i * 72 - 90) * math.pi / 180
            x, y = math.cos(angle) * size, math.sin(angle) * size
            if i == 0: path.moveTo(x, y)
            else: path.lineTo(x, y)
            inner_angle = ((i * 72) - 90 + 36) * math.pi / 180
            ix, iy = math.cos(inner_angle) * (size / 2), math.sin(inner_angle) * (size / 2)
            path.lineTo(ix, iy)
        path.closeSubpath()
        return path

    def generate_background_cache(self):
        w, h = self.logical_w, self.logical_h
        self.bg_cache = QPixmap(w, h)
        self.bg_cache.fill(Qt.transparent)
        painter = QPainter(self.bg_cache)
        painter.setRenderHint(QPainter.Antialiasing)
        arena = ARENAS_DB[self.current_arena]
        h_type = arena.get("hazard_type", "none")

        gradient = QLinearGradient(0, 0, 0, h)
        gradient.setColorAt(0, arena["sky_top"])
        gradient.setColorAt(0.5, arena["sky_bot"].darker(150))
        gradient.setColorAt(1, arena["sky_bot"])
        painter.fillRect(0, 0, w, h, gradient)

        painter.setPen(Qt.NoPen)
        for i in range(30):
            x = (i * 37 + 13) % w
            y = (i * 53 + 7) % (h // 2)
            painter.setBrush(QColor(200, 200, 255, 110))
            painter.drawEllipse(QPointF(x, y), 1.5, 1.5)

        floor_top = h * 0.28
        floor_bottom = h * 0.92
        path = QPainterPath()
        path.moveTo(0, h)
        path.lineTo(0, floor_bottom)

        points = []
        for i in range(11):
            x = (w / 10) * i
            y_var = random.uniform(-15, 15) if 0 < i < 10 else 0
            y = floor_top + y_var
            points.append((x, y))

        for p in points: path.lineTo(p[0], p[1])
        path.lineTo(w, floor_bottom)
        path.closeSubpath()

        f_grad = QLinearGradient(0, floor_top, 0, floor_bottom)
        f_grad.setColorAt(0, arena["floor"].lighter(130))
        f_grad.setColorAt(1, arena["floor"].darker(150))
        painter.fillPath(path, f_grad)

        painter.setPen(QPen(arena["floor_edge"].darker(150), 2))
        for i in range(len(points)-1):
            painter.drawLine(QPointF(points[i][0], points[i][1]), QPointF(points[i+1][0], points[i+1][1]))

        if h_type == "lava":
            painter.setPen(QPen(QColor(255, 100, 0, 200), 2))
            for i in range(5):
                x_start = random.uniform(50, w-50)
                y_start = random.uniform(floor_top+20, floor_bottom-20)
                path_crack = QPainterPath()
                path_crack.moveTo(x_start, y_start)
                path_crack.lineTo(x_start + random.uniform(-30, 30), y_start + random.uniform(10, 40))
                path_crack.lineTo(x_start + random.uniform(-50, 50), y_start + random.uniform(50, 80))
                painter.drawPath(path_crack)
        elif h_type == "ice" or h_type == "blizzard":
            painter.setBrush(QColor(150, 220, 255, 100)); painter.setPen(Qt.NoPen)
            for i in range(4):
                rx = random.uniform(60, w-60)
                ry = floor_top + random.uniform(-5, 15)
                poly = QPolygonF([QPointF(rx, ry), QPointF(rx + 20, ry + 60), QPointF(rx - 20, ry + 60)])
                painter.drawPolygon(poly)
        elif h_type == "blackhole" or h_type == "void":
            painter.setBrush(QColor(80, 50, 100)); painter.setPen(Qt.NoPen)
            for i in range(3):
                rx = random.uniform(80, w-80)
                ry = floor_top + random.uniform(0, 30)
                painter.drawEllipse(QPointF(rx, ry), 30, 15)
        painter.end()

    def setup_battle(self, w1_name: str, w1_class: str, w2_name: str, w2_class: str, arena_name: str):
        self.current_arena = arena_name
        self.generate_background_cache()

        self.warrior1 = Warrior.from_db(w1_name, w1_class, 0)
        self.warrior2 = Warrior.from_db(w2_name, w2_class, 1)

        mods = ARENAS_DB[arena_name].get("stat_modifiers", {})
        self.warrior1.apply_arena_modifiers(mods)
        self.warrior2.apply_arena_modifiers(mods)

        self.warrior1.x = self.floor_left + 60
        self.warrior1.y = (self.floor_top + self.floor_bottom) / 2
        self.warrior1.home_x = self.warrior1.x; self.warrior1.home_y = self.warrior1.y
        self.warrior1.target_x = self.warrior1.x; self.warrior1.target_y = self.warrior1.y
        self.warrior1.facing_angle = 0

        self.warrior2.x = self.floor_right - 60
        self.warrior2.y = (self.floor_top + self.floor_bottom) / 2
        self.warrior2.home_x = self.warrior2.x; self.warrior2.home_y = self.warrior2.y
        self.warrior2.target_x = self.warrior2.x; self.warrior2.target_y = self.warrior2.y
        self.warrior2.facing_angle = math.pi

        self.particles.clear(); self.floating_texts.clear(); self.slashes.clear()
        self.shockwaves.clear(); self.hazards.clear(); self.battle_log.clear()
        self.projectiles.clear(); self.pickups.clear(); self.obstacles.clear()
        
        self.shake_amount = 0; self.flash_amount = 0; self.turn_count = 0
        self.phase = BattlePhase.INTRO; self.phase_timer = 0; self.intro_timer = 0
        self.hit_stop_timer = 0; self.camera_zoom = 1.0; self.target_camera_zoom = 1.0
        self.hazard_spawn_timer = HAZARD_INTERVAL
        self.pickup_spawn_timer = 10.0
        self.slow_mo_active = False; self.slow_mo_timer = 0
        self.first_blood_done = False
        self.last_commentary_timer = 0
        
        self.w1_odds, self.w2_odds, self.odds_analysis = WinOddsCalculator.calculate(
            self.warrior1, self.warrior2, self.history
        )
        
        self.generate_obstacles()
        self.stats_updated.emit()
        
        if self.tournament.active:
            match = self.tournament.get_current_match()
            if match:
                self.add_log(f"🏆 TOURNAMENT: {w1_name} vs {w2_name}")

    def generate_obstacles(self):
        templates = OBSTACLE_TEMPLATES.get(self.current_arena, [])
        if not templates: return
        num_obstacles = random.randint(4, 6)
        attempts = 0
        while len(self.obstacles) < num_obstacles and attempts < 100:
            attempts += 1
            ox = random.uniform(self.floor_left + 80, self.floor_right - 80)
            oy = random.uniform(self.floor_top + 40, self.floor_bottom - 40)
            if abs(oy - (self.floor_top + self.floor_bottom)/2) < 50 and \
               (ox < self.floor_left + 120 or ox > self.floor_right - 120):
                continue
            radius = random.uniform(22, 38)
            ok = True
            for o in self.obstacles:
                if math.hypot(o.x - ox, o.y - oy) < o.radius + radius + 20:
                    ok = False; break
            if not ok: continue
            otype, oemoji, ocolor = random.choice(templates)
            self.obstacles.append(Obstacle(
                x=ox, y=oy, radius=radius, obstacle_type=otype,
                emoji=oemoji, color=ocolor, rotation=random.uniform(0, 360)
            ))
        self.add_log(f"🪨 {len(self.obstacles)} obstacles scattered across the arena!")

    def reset(self):
        self.warrior1 = None; self.warrior2 = None
        self.phase = BattlePhase.IDLE
        self.particles.clear(); self.floating_texts.clear(); self.slashes.clear()
        self.shockwaves.clear(); self.hazards.clear(); self.battle_log.clear()
        self.projectiles.clear(); self.pickups.clear(); self.obstacles.clear()
        self.shake_amount = 0; self.flash_amount = 0
        self.special_banner_timer = 0; self.hit_stop_timer = 0
        self.slow_mo_active = False; self.slow_mo_timer = 0
        self.stats_updated.emit()

    def pause(self):
        if self.phase not in (BattlePhase.BATTLE, BattlePhase.ACTION_ANIM, BattlePhase.INTRO, BattlePhase.COUNTDOWN): return
        self.previous_phase = self.phase
        self.phase = BattlePhase.PAUSED

    def resume(self):
        if self.phase == BattlePhase.PAUSED: self.phase = self.previous_phase

    def trigger_slow_mo(self, duration: float = SLOW_MO_FINISHER_DURATION):
        self.slow_mo_active = True
        self.slow_mo_timer = duration
        self.target_camera_zoom = 1.3

    def step_simulation(self, raw_dt):
        if self.phase == BattlePhase.PAUSED: return
            
        time_scale = 1.0
        if self.slow_mo_active:
            time_scale = 0.3
            self.slow_mo_timer -= raw_dt
            if self.slow_mo_timer <= 0:
                self.slow_mo_active = False
                self.target_camera_zoom = 1.0
        
        dt = raw_dt * self.speed_multiplier * time_scale
        if self.hit_stop_timer > 0:
            self.hit_stop_timer -= raw_dt
            return

        self.update_phase(dt)
        self.update_particles(dt)
        self.update_floating_texts(dt)
        self.update_slashes(dt)
        self.update_shockwaves(dt)
        self.update_hazards(dt)
        self.update_projectiles(dt)
        self.update_pickups(dt)
        self.update_obstacles(dt)
        self.update_warriors(dt)
        self.update_ambient(dt)
        self.update_weather(dt)

        self.shake_amount *= math.exp(-dt * 8)
        self.flash_amount *= math.exp(-dt * 6)
        self.special_banner_timer = max(0, self.special_banner_timer - dt)
        self.last_commentary_timer = max(0, self.last_commentary_timer - dt)

        self.camera_zoom += (self.target_camera_zoom - self.camera_zoom) * dt * 8.0
        if abs(self.camera_zoom - 1.0) < 0.01 and self.target_camera_zoom != 1.0 and not self.slow_mo_active:
            self.target_camera_zoom = 1.0

    def update_game(self):
        raw_dt = (self.elapsed.elapsed() - self.last_time) / 1000.0
        self.last_time = self.elapsed.elapsed()
        raw_dt = min(raw_dt, 0.05)
        self.step_simulation(raw_dt)
        self.update()

    def update_phase(self, dt):
        if self.phase == BattlePhase.INTRO:
            self.intro_timer += dt
            if self.intro_timer > 3.0:
                self.phase = BattlePhase.COUNTDOWN
                self.phase_timer = 0; self.countdown_value = 3
        elif self.phase == BattlePhase.COUNTDOWN:
            self.phase_timer += dt
            if self.phase_timer > 0.8:
                self.phase_timer = 0; self.countdown_value -= 1
                if self.countdown_value <= 0:
                    self.phase = BattlePhase.BATTLE
                    self.add_log("⚔️ FIGHT!")
        elif self.phase == BattlePhase.BATTLE:
            if not self.warrior1.is_alive or not self.warrior2.is_alive:
                self.start_victory(); return

            for w in [self.warrior1, self.warrior2]:
                if w.poison_timer > 0:
                    w.poison_timer -= dt
                    if int(w.poison_timer * 2) > int((w.poison_timer + dt) * 2):
                        dmg = max(1, w.max_hp // 20)
                        w.hp -= dmg; w.stats.damage_taken += dmg
                        self.spawn_floating_text(w.x, w.y - 20, f"-{dmg} ☠️", QColor(100, 200, 50), size=20)
                if w.burn_timer > 0:
                    w.burn_timer -= dt
                    if int(w.burn_timer * 3) > int((w.burn_timer + dt) * 3):
                        dmg = max(1, w.max_hp // 15)
                        w.hp -= dmg; w.stats.damage_taken += dmg
                        self.spawn_floating_text(w.x, w.y - 20, f"-{dmg} 🔥", QColor(255, 100, 0), size=20)
                
                w.knockback_x += (0 - w.knockback_x) * dt * 8.0
                w.knockback_y += (0 - w.knockback_y) * dt * 8.0
                w.hit_stumble = max(0, w.hit_stumble - dt)
                w.displayed_hp += (w.hp - w.displayed_hp) * dt * 10.0
                w.displayed_mp += (w.mp - w.displayed_mp) * dt * 10.0

                if w.hp_percent < RAGE_HP_THRESHOLD and not w.is_enraged and w.is_alive:
                    w.is_enraged = True
                    w.recalculate_attack()
                    self.add_log(f"🔥 {w.name} enters RAGE MODE!")
                    self.spawn_explosion(w.x, w.y, QColor(255, 50, 0), count=20, speed=150)
                    self.flash(QColor(255, 50, 0), 0.4)
                    self.try_commentary("comeback")

            if not self.warrior1.is_alive or not self.warrior2.is_alive:
                self.start_victory(); return
            self.start_action()
        elif self.phase == BattlePhase.ACTION_ANIM:
            self.action_timer += dt
            self.update_action_animation(dt)
            if self.action_timer >= self.action_duration: self.finish_action()
        elif self.phase == BattlePhase.VICTORY:
            self.phase_timer += dt
            if random.random() < 0.3:
                winner = self.warrior1 if self.warrior1.is_winner else self.warrior2
                self.spawn_celebration(winner)
            if self.auto_queue and self.phase_timer > 4.0: self.request_next_battle.emit()

    def try_commentary(self, key: str):
        if self.last_commentary_timer > 0: return
        if key not in COMMENTARY_PHRASES: return
        if random.random() < 0.5:
            text = random.choice(COMMENTARY_PHRASES[key])
            self.commentary_triggered.emit(text)
            self.last_commentary_timer = 3.0

    def update_hazards(self, dt):
        if self.phase in [BattlePhase.BATTLE, BattlePhase.ACTION_ANIM]:
            self.hazard_spawn_timer -= dt
            if self.hazard_spawn_timer <= 0:
                self.hazard_spawn_timer = HAZARD_INTERVAL + random.uniform(-2, 2)
                self.spawn_hazard()

        for h in self.hazards:
            h.timer -= dt
            if h.phase == "warning" and h.timer <= 0:
                h.phase = "active"
                h.timer = 0.4
                self.trigger_hazard(h)
            elif h.phase == "active" and h.timer <= 0:
                h.timer = -1
        self.hazards = [h for h in self.hazards if h.timer > -1]

    def spawn_hazard(self):
        hx = random.uniform(self.floor_left + 60, self.floor_right - 60)
        hy = random.uniform(self.floor_top + 20, self.floor_bottom - 20)
        arena = ARENAS_DB[self.current_arena]
        h_type = arena.get("hazard_type", "none")
        h_color = arena.get("hazard_color", QColor(255, 255, 255))
        self.hazards.append(HazardEffect(x=hx, y=hy, timer=1.5, phase="warning", hazard_type=h_type, color=h_color))
        self.add_log(f"⚠️ Hazard warning!")

    def trigger_hazard(self, h: HazardEffect):
        h_type = h.hazard_type
        h_radius = 60.0
        if h_type == "lava":
            self.add_log("🌋 Lava geyser erupts!")
            self.spawn_explosion(h.x, h.y, QColor(255, 100, 0), count=30, speed=200)
            self.flash(QColor(255, 100, 0), 0.3)
            self.shake(10)
        elif h_type == "ice" or h_type == "blizzard":
            self.add_log("🧊 Ice spikes shatter!")
            self.spawn_hit_particles(h.x, h.y, QColor(150, 220, 255), count=40)
            self.shake(8)
        elif h_type == "blackhole" or h_type == "void":
            self.add_log("🕳️ Void collapses!")
            self.shockwaves.append(ShockwaveEffect(x=h.x, y=h.y, life=0.8, max_life=0.8, color=QColor(150, 0, 255), max_radius=100, width=10))
            self.shake(12)
            h_radius = 120.0
        elif h_type == "poison_swamp":
            self.add_log("🍄 Toxic spores erupt!")
            self.spawn_explosion(h.x, h.y, QColor(150, 50, 200), count=25, speed=150)
            self.shake(8)
        elif h_type == "lightning":
            self.add_log("⚡ Lightning strikes!")
            self.spawn_explosion(h.x, h.y, QColor(255, 255, 0), count=35, speed=250)
            self.flash(QColor(255, 255, 100), 0.4)
            self.shake(14)

        for o in getattr(self, 'obstacles', []):
            if math.hypot(o.x - h.x, o.y - h.y) < h_radius:
                o.hp -= 25
                o.hit_flash = 0.2
                if o.hp <= 0: self.destroy_obstacle(o)

        for w in [self.warrior1, self.warrior2]:
            blocked = False
            for o in getattr(self, 'obstacles', []):
                if self.line_intersects_circle(h.x, h.y, w.x, w.y, o.x, o.y, o.radius):
                    blocked = True; break
            if blocked: continue

            if math.hypot(w.x - h.x, w.y - h.y) < h_radius:
                if w.is_invincible:
                    self.spawn_floating_text(w.x, w.y - 40, "INVINCIBLE! ⭐", QColor(255, 215, 0), size=24)
                    continue
                if h_type == "lava":
                    w.hp -= 15; w.stats.damage_taken += 15; w.burn_timer = 3.0
                    self.spawn_floating_text(w.x, w.y - 40, "-15 🔥", QColor(255, 100, 0), size=28)
                elif h_type == "ice" or h_type == "blizzard":
                    w.hp -= 10; w.stats.damage_taken += 10; w.freeze_timer = 2.0
                    self.spawn_floating_text(w.x, w.y - 40, "FROZEN! 🧊", QColor(150, 220, 255), size=24)
                elif h_type == "blackhole" or h_type == "void":
                    w.hp -= 12; w.stats.damage_taken += 12
                    self.spawn_floating_text(w.x, w.y - 40, "-12 🌌", QColor(200, 100, 255), size=24)
                elif h_type == "lightning":
                    w.hp -= 18; w.stats.damage_taken += 18; w.stun_timer = 1.5
                    self.spawn_floating_text(w.x, w.y - 40, "-18 ⚡", QColor(255, 255, 0), size=28)
                w.hit_flash = 0.3

    def line_intersects_circle(self, x1, y1, x2, y2, cx, cy, r):
        dx, dy = x2 - x1, y2 - y1
        fx, fy = x1 - cx, y1 - cy
        a = dx*dx + dy*dy
        b = 2 * (fx*dx + fy*dy)
        c = fx*fx + fy*fy - r*r
        disc = b*b - 4*a*c
        if disc < 0: return False
        disc = math.sqrt(disc)
        t1 = (-b - disc) / (2*a)
        t2 = (-b + disc) / (2*a)
        return (0 <= t1 <= 1) or (0 <= t2 <= 1)

    def update_ambient(self, dt):
        self.ambient_timer += dt
        if self.ambient_timer > 0.2:
            self.ambient_timer = 0
            arena = ARENAS_DB[self.current_arena]
            self.particles.append(Particle(
                x=random.uniform(0, self.logical_w), y=self.logical_h + 10,
                vx=random.uniform(-10, 10), vy=random.uniform(-30, -60),
                life=random.uniform(3, 5), max_life=5,
                color=arena["ambient_color"], size=random.uniform(4, 8),
                gravity=-20, shape="star", emoji=arena["ambient_emoji"]
            ))

    def update_weather(self, dt):
        weather = ARENAS_DB[self.current_arena].get("weather", "")
        if not weather: return
        self.weather_timer += dt
        spawn_rate = {"rain": 0.02, "snow": 0.05, "ash": 0.1, "fog": 0.1, "sand": 0.08, "void": 0.1, "stars": 0.2}.get(weather, 0.1)
        if self.weather_timer < spawn_rate: return
        self.weather_timer = 0
        
        w, h = self.logical_w, self.logical_h
        if weather == "rain":
            for _ in range(3):
                self.particles.append(Particle(
                    x=random.uniform(0, w), y=-10,
                    vx=random.uniform(-30, -10), vy=random.uniform(400, 600),
                    life=1.0, max_life=1.0, color=QColor(150, 180, 220, 180),
                    size=2, gravity=0, shape="circle", shrink=False
                ))
        elif weather == "snow":
            self.particles.append(Particle(
                x=random.uniform(0, w), y=-10,
                vx=random.uniform(-20, 20), vy=random.uniform(30, 60),
                life=4.0, max_life=4.0, color=QColor(255, 255, 255, 200),
                size=random.uniform(2, 5), gravity=0, shape="circle", shrink=False
            ))
        elif weather == "ash":
            self.particles.append(Particle(
                x=random.uniform(0, w), y=random.uniform(0, h),
                vx=random.uniform(-15, 15), vy=random.uniform(-10, 10),
                life=3.0, max_life=3.0, color=QColor(100, 80, 60, 150),
                size=random.uniform(3, 6), gravity=-10, shape="circle"
            ))
        elif weather == "void":
            self.particles.append(Particle(
                x=random.uniform(0, w), y=random.uniform(0, h),
                vx=random.uniform(-5, 5), vy=random.uniform(-30, -50),
                life=3.0, max_life=3.0, color=QColor(150, 0, 200, 180),
                size=random.uniform(3, 7), gravity=-20, shape="star"
            ))

    def start_action(self):
        s1 = self.warrior1.get_effective_speed()
        s2 = self.warrior2.get_effective_speed()
        if s1 >= s2:
            self.attacker, self.defender = self.warrior1, self.warrior2
        else:
            self.attacker, self.defender = self.warrior2, self.warrior1
        if random.random() < 0.2:
            self.attacker, self.defender = self.defender, self.attacker

        dist = math.hypot(self.attacker.x - self.defender.x, self.attacker.y - self.defender.y)
        is_ranged = self.attacker.class_name in RANGED_CLASSES
        attack_range = 250.0 if is_ranged else self.ATTACK_RANGE_MELEE + 5

        if dist > attack_range:
            self.current_action = ActionType.BLOCK
            self.attacker.move_state = "APPROACH"
            ang = math.atan2(self.defender.y - self.attacker.y, self.defender.x - self.attacker.x)
            stop_dist = attack_range - 30
            self.attacker.target_x = self.defender.x - math.cos(ang) * stop_dist
            self.attacker.target_y = self.defender.y - math.sin(ang) * stop_dist
            self.action_timer = 0; self.action_duration = 0.4
            self.phase = BattlePhase.ACTION_ANIM
            self.action_data = {"effect_applied": True, "approach_turn": True}
            return

        action = self.attacker.decide_action(self.defender, self.ai_difficulty)
        self.current_action = action
        self.action_timer = 0; self.turn_count += 1

        self.attacker.guard_up = False; self.attacker.dodge_ready = False
        self.attacker.blocking = False; self.attacker.dodging = False

        phrase = random.choice(ACTION_PHRASES.get(action.name, ["..."]))
        if self.defender.hp_percent < 0.2 and random.random() < 0.3:
            phrase = random.choice(CONTEXTUAL_BARKS["enemy_low_hp"])
        elif self.attacker.combo >= 3 and random.random() < 0.3:
            phrase = random.choice(CONTEXTUAL_BARKS["high_combo"])
        elif self.attacker.is_marked and random.random() < 0.3:
            phrase = random.choice(CONTEXTUAL_BARKS["marked"])

        self.spawn_floating_text(self.attacker.x, self.attacker.y - 60, phrase, QColor(255, 255, 255), size=16, is_speech=True)

        durations = {ActionType.LIGHT_ATTACK: 0.8, ActionType.HEAVY_ATTACK: 1.2,
                     ActionType.SPECIAL: 1.8, ActionType.BLOCK: 0.6, ActionType.DODGE: 0.6,
                     ActionType.HEAL: 1.2, ActionType.BUFF: 1.2}
        self.action_duration = durations.get(action, 1.0)
        self.phase = BattlePhase.ACTION_ANIM
        self.action_data = {"effect_applied": False}

    def update_action_animation(self, dt):
        if not self.attacker or not self.defender: return
        progress = self.action_timer / self.action_duration
        action = self.current_action
        attacker = self.attacker

        if action in (ActionType.LIGHT_ATTACK, ActionType.HEAVY_ATTACK, ActionType.SPECIAL):
            lunge_dir_x = (self.defender.x - attacker.home_x)
            lunge_dir_y = (self.defender.y - attacker.home_y)
            ld = math.hypot(lunge_dir_x, lunge_dir_y) + 0.001
            lunge_dir_x /= ld; lunge_dir_y /= ld

            if progress < 0.3:
                pull = 20 * (progress / 0.3)
                attacker.x = attacker.home_x - lunge_dir_x * pull + attacker.knockback_x
                attacker.y = attacker.home_y - lunge_dir_y * pull + attacker.knockback_y
                attacker.scale = 1.0 + 0.1 * (progress / 0.3)
                attacker.facing_angle = math.atan2(lunge_dir_y, lunge_dir_x)
            elif progress < 0.5:
                lp = (progress - 0.3) / 0.2
                lunge_dist = 50 * lp
                attacker.x = attacker.home_x + lunge_dir_x * lunge_dist + attacker.knockback_x
                attacker.y = attacker.home_y + lunge_dir_y * lunge_dist + attacker.knockback_y
                attacker.scale = 1.1 - 0.15 * lp
                if not self.action_data["effect_applied"] and progress >= 0.45:
                    if attacker.class_name in RANGED_CLASSES and action != ActionType.SPECIAL:
                        # Predict enemy position (Target Leading)
                        proj_speed = 600
                        dist = math.hypot(self.defender.x - attacker.x, self.defender.y - attacker.y)
                        time_to_hit = dist / proj_speed
                        pred_x = self.defender.x + self.defender.vx * time_to_hit
                        pred_y = self.defender.y + self.defender.vy * time_to_hit
                        
                        ang = math.atan2(pred_y - attacker.y, pred_x - attacker.x)
                        speed = proj_speed
                        dmg = int(attacker.get_effective_attack() * (1.5 if action == ActionType.HEAVY_ATTACK else 1.0))
                        proj_emoji = "🔥" if "Fire" in attacker.special_name or attacker.damage_type == DamageType.FIRE else "✨"
                        self.projectiles.append(Projectile(
                            x=attacker.x, y=attacker.y, 
                            vx=math.cos(ang)*speed, vy=math.sin(ang)*speed,
                            damage=dmg, life=1.5, max_life=1.5, 
                            color=attacker.color, emoji=proj_emoji, size=20, owner=attacker,
                            damage_type=attacker.damage_type
                        ))
                    else:
                        self.apply_attack_damage(action, attacker, self.defender)
                    self.action_data["effect_applied"] = True
                    if action == ActionType.SPECIAL: self.target_camera_zoom = 1.15
            elif progress < 0.7:
                attacker.x = attacker.home_x + lunge_dir_x * 50 + attacker.knockback_x
                attacker.y = attacker.home_y + lunge_dir_y * 50 + attacker.knockback_y
                attacker.scale = 0.95
            else:
                rp = (progress - 0.7) / 0.3
                attacker.x = attacker.home_x + lunge_dir_x * 50 * (1 - rp) + attacker.knockback_x
                attacker.y = attacker.home_y + lunge_dir_y * 50 * (1 - rp) + attacker.knockback_y
                attacker.scale = 0.95 + 0.05 * rp
        elif action == ActionType.BLOCK:
            attacker.blocking = True; attacker.guard_up = True
        elif action == ActionType.DODGE:
            attacker.dodging = True; attacker.dodge_ready = True
        elif action == ActionType.HEAL:
            attacker.scale = 1.0 + 0.2 * math.sin(progress * math.pi)
            if not self.action_data["effect_applied"] and progress >= 0.5:
                self.apply_heal(attacker)
                self.action_data["effect_applied"] = True
        elif action == ActionType.BUFF:
            attacker.scale = 1.0 + 0.2 * math.sin(progress * math.pi)
            if not self.action_data["effect_applied"] and progress >= 0.5:
                self.apply_buff(attacker)
                self.action_data["effect_applied"] = True

    def apply_heal(self, attacker):
        attacker.mp -= HEAL_MP_COST
        attacker.stats.heals_used += 1
        heal_amt = int(attacker.max_hp * HEAL_HP_PERCENT)
        actual_heal = min(heal_amt, attacker.max_hp - attacker.hp)
        attacker.hp = min(attacker.max_hp, attacker.hp + heal_amt)
        attacker.heal_cooldown = 6.0
        self.add_log(f"✨ {attacker.name} casts Heal! (+{actual_heal} HP)")
        self.spawn_floating_text(attacker.x, attacker.y - 40, f"+{actual_heal}", QColor(100, 255, 100), size=32)

    def apply_buff(self, attacker):
        attacker.mp -= BUFF_MP_COST
        attacker.buff_timer = BUFF_DURATION
        attacker.buff_cooldown = 8.0
        attacker.recalculate_attack()
        self.add_log(f"💪 {attacker.name} casts Buff! (ATK {attacker.base_attack} → {attacker.attack})")
        self.spawn_floating_text(attacker.x, attacker.y - 40, "ATK UP!", QColor(255, 200, 0), size=28)

    def apply_attack_damage(self, action, attacker, defender):
        is_crit = random.random() < 0.15
        crit_mult = 1.5 if is_crit else 1.0
        attacker_atk = attacker.get_effective_attack()

        if action == ActionType.LIGHT_ATTACK:
            attacker.mp = min(attacker.max_mp, attacker.mp + LIGHT_MP_GAIN)
            dmg = int(attacker_atk * random.uniform(0.8, 1.2) * crit_mult)
            knockback = 5
        elif action == ActionType.HEAVY_ATTACK:
            attacker.mp = min(attacker.max_mp, attacker.mp + HEAVY_MP_GAIN)
            dmg = int(attacker_atk * 1.7 * random.uniform(0.9, 1.3) * crit_mult)
            knockback = 20
            if random.random() < 0.15:
                defender.stun_timer = 1.0
                self.add_log(f"💫 {defender.name} is stunned!")
        elif action == ActionType.SPECIAL:
            attacker.mp -= SPECIAL_MP_COST
            attacker.stats.specials_used += 1
            dmg = int(attacker_atk * 2.5 * random.uniform(1.0, 1.5) * crit_mult)
            attacker.special_cooldown = SPECIAL_COOLDOWN
            self.special_banner_text = f"{attacker.special_emoji} {attacker.special_name}!"
            self.special_banner_timer = 1.5
            self.flash(attacker.color, 0.6); self.shake(15)
            knockback = 35
            
            if attacker.damage_type == DamageType.FIRE:
                defender.burn_timer = 3.0
                self.add_log(f"🔥 {defender.name} is burning!")
            elif attacker.damage_type == DamageType.ICE:
                defender.freeze_timer = 2.0
                self.add_log(f"🧊 {defender.name} is frozen!")
            elif attacker.damage_type == DamageType.LIGHTNING:
                defender.stun_timer = 1.5
                self.add_log(f"⚡ {defender.name} is shocked!")
            elif attacker.damage_type == DamageType.POISON:
                defender.poison_timer = 4.0
                self.add_log(f"☠️ {defender.name} is poisoned!")
        else: return

        if defender.dodge_ready:
            dodge_chance = DODGE_CHANCE_BASE + max(0, (defender.get_effective_speed() - attacker.get_effective_speed()) * 0.02)
            if random.random() < dodge_chance:
                defender.stats.dodges += 1
                self.add_log(f"{defender.emoji} dodged the attack!")
                self.spawn_floating_text(defender.x, defender.y - 50, "DODGED! 💨", QColor(100, 255, 100))
                attacker.combo = 0
                defender.dodge_ready = False
                if defender.stats.dodges == 5:
                    self.achievements.unlock("dodge_master")
                    self.try_commentary("dodge_master")
                
                # Counter-Attack chance
                if random.random() < 0.25 and defender.is_alive:
                    counter_dmg = max(1, int(defender.get_effective_attack() * 0.4) - attacker.defense // 2)
                    attacker.hp = max(0, attacker.hp - counter_dmg)
                    attacker.stats.damage_taken += counter_dmg
                    defender.stats.damage_dealt += counter_dmg
                    self.add_log(f"↩️ {defender.emoji} counter-attacks for {counter_dmg}!")
                    self.spawn_floating_text(attacker.x, attacker.y - 40, f"↩️ -{counter_dmg}", QColor(255, 200, 0), size=28)
                    self.slashes.append(SlashEffect(x=attacker.x, y=attacker.y, angle=random.uniform(-30, 30),
                        life=0.2, max_life=0.2, color=QColor(255, 200, 0), length=70, width=5))
                    attacker.hit_flash = 0.3; attacker.hit_stumble = 0.2
                    self.shake(5)
                    self.spawn_hit_particles(attacker.x, attacker.y, QColor(255, 200, 0), count=8)
                return

        if defender.guard_up:
            dmg = int(dmg * BLOCK_DAMAGE_REDUCTION)
            defender.stats.blocks += 1
            self.add_log(f"{defender.emoji} blocked! Damage reduced.")
            self.spawn_floating_text(defender.x, defender.y - 50, "BLOCKED 🛡️", QColor(150, 200, 255))
            attacker.combo = 0
            if defender.stats.blocks == 5:
                self.achievements.unlock("block_master")
                self.try_commentary("block_master")
            defender.guard_up = False
            if dmg <= 0: return

        attacker.combo += 1
        attacker.stats.max_combo = max(attacker.stats.max_combo, attacker.combo)
        if attacker.combo == OVERDRIVE_THRESHOLD and attacker.overdrive_timer <= 0:
            attacker.overdrive_timer = 5.0
            attacker.recalculate_attack()
            self.add_log(f"⚡ {attacker.name} enters OVERDRIVE!")
        if attacker.combo == 5:
            self.achievements.unlock("combo_master")
            self.try_commentary("combo_5")
        if attacker.combo > 1:
            dmg = int(dmg * (1.0 + 0.1 * attacker.combo))

        dmg_type_mod = defender.get_damage_modifier(attacker.damage_type)
        original_dmg = dmg
        dmg = int(dmg * dmg_type_mod)
        
        if attacker.damage_type not in attacker.stats.damage_by_type:
            attacker.stats.damage_by_type[attacker.damage_type] = 0
        attacker.stats.damage_by_type[attacker.damage_type] += dmg
        
        if not self.first_blood_done and dmg > 0:
            self.first_blood_done = True
            attacker.first_blood_dealt = True
            self.try_commentary("first_blood")
        if dmg >= 50:
            self.try_commentary("big_hit")

        dmg = max(1 if dmg_type_mod > 0 else 0, dmg - defender.defense // 2)
        
        if defender.is_invincible:
            dmg = 0
            self.spawn_floating_text(defender.x, defender.y - 40, "INVINCIBLE! ⭐", QColor(255, 215, 0), size=32)
        
        defender.hp = max(0, defender.hp - dmg)
        defender.hit_flash = 0.3; defender.hit_stumble = 0.3
        
        ang = math.atan2(defender.y - attacker.y, defender.x - attacker.x)
        defender.knockback_x = math.cos(ang) * knockback
        defender.knockback_y = math.sin(ang) * knockback
        
        defender.stats.damage_taken += dmg
        attacker.stats.damage_dealt += dmg
        if is_crit: attacker.stats.crits += 1

        type_colors = {
            DamageType.PHYSICAL: QColor(255, 80, 80),
            DamageType.FIRE: QColor(255, 100, 0),
            DamageType.ICE: QColor(150, 220, 255),
            DamageType.LIGHTNING: QColor(255, 255, 0),
            DamageType.POISON: QColor(100, 200, 50),
            DamageType.HOLY: QColor(255, 255, 200),
        }
        hit_color = type_colors.get(attacker.damage_type, QColor(255, 80, 80))
        text_color = type_colors.get(attacker.damage_type, QColor(255, 80, 80))
        
        self.spawn_hit_particles(defender.x, defender.y, hit_color, count=25 if action == ActionType.SPECIAL else 12)
        if is_crit:
            self.spawn_floating_text(defender.x, defender.y - 40, f"💥 CRIT! -{dmg}", QColor(255, 50, 50), size=40)
            self.hit_stop_timer = 0.08; self.shake(20)
        else:
            self.spawn_floating_text(defender.x, defender.y - 40, f"-{dmg}", text_color, size=36)

        self.shake({ActionType.LIGHT_ATTACK: 5, ActionType.HEAVY_ATTACK: 10, ActionType.SPECIAL: 20}.get(action, 5))
        if action == ActionType.SPECIAL: self.flash(hit_color, 0.8)

        if defender.hp <= 0 and not self.slow_mo_active:
            self.trigger_slow_mo(1.5)
            self.try_commentary("low_hp_clutch")
            if defender.is_marked:
                self.achievements.unlock("mark_and_finish")
                
            # Overkill Bloodthirst
            overkill = -defender.hp
            if overkill > defender.max_hp * 0.2:
                heal_amt = overkill // 2
                attacker.hp = min(attacker.max_hp, attacker.hp + heal_amt)
                self.spawn_floating_text(attacker.x, attacker.y - 60, f"BLOODTHIRST! +{heal_amt}", QColor(255, 0, 100), size=24)
                self.add_log(f"🩸 {attacker.name} gets Bloodthirst! (+{heal_amt} HP)")
                self.spawn_explosion(attacker.x, attacker.y, QColor(255, 0, 100), count=20, speed=150)

    def finish_action(self):
        self.attacker.x = self.attacker.home_x + self.attacker.knockback_x
        self.attacker.y = self.attacker.home_y + self.attacker.knockback_y
        self.attacker.scale = 1.0
        self.attacker.blocking = False; self.attacker.dodging = False
        self.attacker.special_cooldown = max(0, self.attacker.special_cooldown - 1)
        self.attacker.heal_cooldown = max(0, self.attacker.heal_cooldown - 1)
        self.attacker.buff_cooldown = max(0, self.attacker.buff_cooldown - 1)
        self.defender.special_cooldown = max(0, self.defender.special_cooldown - 1)
        self.defender.heal_cooldown = max(0, self.defender.heal_cooldown - 1)
        self.defender.buff_cooldown = max(0, self.defender.buff_cooldown - 1)
        self.attacker.mp = min(self.attacker.max_mp, self.attacker.mp + PASSIVE_MP_REGEN)
        self.defender.mp = min(self.defender.max_mp, self.defender.mp + PASSIVE_MP_REGEN)
        self.target_camera_zoom = 1.0
        self.stats_updated.emit()
        if not self.defender.is_alive or not self.attacker.is_alive: self.start_victory()
        else: self.phase = BattlePhase.BATTLE

    def start_victory(self):
        winner = self.warrior1 if self.warrior1.is_alive else self.warrior2
        loser = self.warrior2 if winner is self.warrior1 else self.warrior1
        winner.is_winner = True
        loser.alpha = 0.4; loser.scale = 0.8; loser.combo = 0
        self.phase = BattlePhase.VICTORY; self.phase_timer = 0
        self.winner_name = winner.name; self.loser_name = loser.name
        self.add_log(f"🏆 {winner.emoji} {winner.name} WINS!")
        self.battle_ended.emit(winner.name, loser.name)
        self.flash(QColor(255, 215, 0), 1.0)
        self.target_camera_zoom = 1.2
        self.slow_mo_active = False
        for _ in range(40): self.spawn_celebration(winner)
        
        self.achievements.unlock("first_win")
        if winner.stats.damage_dealt >= 100: self.achievements.unlock("big_dmg")
        if winner.stats.specials_used >= 3: self.achievements.unlock("specialist")
        if winner.stats.damage_taken == 0: self.achievements.unlock("untouchable")
        if winner.hp / winner.max_hp < 0.1: self.achievements.unlock("comeback_king")
        
        for aid, adata in self.achievements.get_recently_unlocked():
            self.achievement_unlocked.emit(aid, adata["name"], adata["emoji"])
        
        self.stats_updated.emit()

    def add_log(self, text):
        self.battle_log.append(text)
        self.battle_log_updated.emit(text)

    def shake(self, amount): self.shake_amount = max(self.shake_amount, amount)
    def flash(self, color, amount):
        self.flash_color = color
        self.flash_amount = max(self.flash_amount, amount)

    def spawn_hit_particles(self, x, y, color, count=12):
        if len(self.particles) > MAX_PARTICLES: return
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi); speed = random.uniform(100, 300); life = random.uniform(0.3, 0.6)
            self.particles.append(Particle(x=x, y=y, vx=math.cos(angle)*speed, vy=math.sin(angle)*speed,
                life=life, max_life=life, color=color, size=random.uniform(3, 8),
                shape=random.choice(["circle", "star"]), vr=random.uniform(-360, 360)))

    def spawn_explosion(self, x, y, color, count=30, speed=200):
        if len(self.particles) > MAX_PARTICLES - count: return
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi); spd = random.uniform(speed * 0.5, speed); life = random.uniform(0.5, 1.0)
            self.particles.append(Particle(x=x, y=y, vx=math.cos(angle)*spd, vy=math.sin(angle)*spd,
                life=life, max_life=life, color=color, size=random.uniform(4, 10),
                shape=random.choice(["circle", "star", "square"]), gravity=100, vr=random.uniform(-720, 720)))

    def spawn_celebration(self, warrior):
        if len(self.particles) > MAX_PARTICLES: return
        for _ in range(5):
            x = warrior.x + random.uniform(-40, 40); y = warrior.y + random.uniform(-30, 30)
            angle = random.uniform(-math.pi * 0.8, -math.pi * 0.2); speed = random.uniform(150, 350)
            life = random.uniform(0.5, 1.2)
            colors = [QColor(255, 215, 0), QColor(255, 100, 100), QColor(100, 255, 100), QColor(100, 200, 255)]
            self.particles.append(Particle(x=x, y=y, vx=math.cos(angle)*speed, vy=math.sin(angle)*speed,
                life=life, max_life=life, color=random.choice(colors), size=random.uniform(4, 10),
                emoji=random.choice(["⭐", "✨", "🎉", "💫"]), gravity=200))

    def spawn_floating_text(self, x, y, text, color, size=28, is_speech=False):
        self.floating_texts.append(FloatingText(x=x, y=y, text=text, color=color, life=1.0, max_life=1.0, size=size, is_speech=is_speech))

    def update_particles(self, dt):
        for p in self.particles:
            p.x += p.vx * dt; p.y += p.vy * dt; p.vy += p.gravity * dt
            p.life -= dt; p.rotation += p.vr * dt
        self.particles = [p for p in self.particles if p.life > 0]

    def update_floating_texts(self, dt):
        for ft in self.floating_texts:
            ft.life -= dt; ft.y += ft.vy * dt
        self.floating_texts = [ft for ft in self.floating_texts if ft.life > 0]

    def update_slashes(self, dt):
        for s in self.slashes: s.life -= dt
        self.slashes = [s for s in self.slashes if s.life > 0]

    def update_shockwaves(self, dt):
        for sw in self.shockwaves: sw.life -= dt
        self.shockwaves = [sw for sw in self.shockwaves if sw.life > 0]

    def update_projectiles(self, dt):
        for p in self.projectiles:
            p.x += p.vx * dt; p.y += p.vy * dt; p.life -= dt
        self.projectiles = [p for p in self.projectiles if p.life > 0]

    def update_pickups(self, dt):
        self.pickup_spawn_timer -= dt
        if self.pickup_spawn_timer <= 0 and len(self.pickups) < 3:
            self.pickup_spawn_timer = random.uniform(8.0, 12.0)
            types = ["health", "health", "mana", "haste", "rage", "shield", "invincibility"]
            ptype = random.choice(types)
            px = random.uniform(self.floor_left + 50, self.floor_right - 50)
            py = random.uniform(self.floor_top + 50, self.floor_bottom - 50)
            emojis = {"health": "💖", "mana": "🔮", "haste": "⚡", "rage": "🔱", "shield": "🛡️", "invincibility": "⭐"}
            colors = {"health": QColor(255, 100, 150), "mana": QColor(100, 150, 255),
                      "haste": QColor(255, 255, 0), "rage": QColor(255, 50, 50),
                      "shield": QColor(100, 200, 255), "invincibility": QColor(255, 215, 0)}
            self.pickups.append(Pickup(x=px, y=py, pickup_type=ptype, emoji=emojis[ptype], color=colors[ptype]))
        for pk in self.pickups: pk.life -= dt; pk.bob_offset += dt * 4
        self.pickups = [pk for pk in self.pickups if pk.life > 0]

    def update_obstacles(self, dt):
        for o in self.obstacles: o.hit_flash = max(0, o.hit_flash - dt)

    def apply_pickup_effect(self, w: Warrior, pk: Pickup):
        w.stats.pickups_collected += 1
        if pk.pickup_type == "health":
            heal = int(w.max_hp * 0.25)
            w.hp = min(w.max_hp, w.hp + heal)
            self.spawn_floating_text(w.x, w.y - 40, f"+{heal}", QColor(100, 255, 100), size=28)
        elif pk.pickup_type == "mana":
            mana = int(w.max_mp * 0.4)
            w.mp = min(w.max_mp, w.mp + mana)
            self.spawn_floating_text(w.x, w.y - 40, f"+{mana} MP", QColor(100, 150, 255), size=24)
        elif pk.pickup_type == "haste":
            w.haste_timer = HASTE_DURATION
            self.spawn_floating_text(w.x, w.y - 40, "HASTE! ⚡", QColor(255, 255, 0), size=28)
        elif pk.pickup_type == "rage":
            w.rage_pickup_timer = RAGE_PICKUP_DURATION
            w.recalculate_attack()
            self.spawn_floating_text(w.x, w.y - 40, "RAGE! 🔱", QColor(255, 50, 50), size=28)
        elif pk.pickup_type == "shield":
            w.shield_timer = SHIELD_DURATION
            self.spawn_floating_text(w.x, w.y - 40, "SHIELD! 🛡️", QColor(100, 200, 255), size=28)
        elif pk.pickup_type == "invincibility":
            w.invincibility_timer = INVINCIBILITY_DURATION
            self.spawn_floating_text(w.x, w.y - 40, "INVINCIBLE! ⭐", QColor(255, 215, 0), size=32)
            self.flash(QColor(255, 215, 0), 0.5)
        self.spawn_explosion(pk.x, pk.y, pk.color, count=15, speed=100)

    def update_warrior_movement(self, w: Warrior, enemy: Warrior, dt: float):
        if w.stun_timer > 0 or w.freeze_timer > 0: return
        w.move_repath_timer -= dt
        if w.move_repath_timer <= 0:
            w.move_repath_timer = random.uniform(0.4, 0.8)
            dist = math.hypot(enemy.x - w.x, enemy.y - w.y)
            if dist < self.ATTACK_RANGE_MELEE + 10:
                w.move_state = "STRAFE"
                w.strafe_dir *= -1 if random.random() < 0.3 else 1
                ang = math.atan2(enemy.y - w.y, enemy.x - w.x) + (math.pi/2) * w.strafe_dir
                w.target_x = w.x + math.cos(ang) * 70
                w.target_y = w.y + math.sin(ang) * 70
            else:
                w.move_state = "APPROACH"
                ang = math.atan2(enemy.y - w.y, enemy.x - w.x)
                w.target_x = enemy.x - math.cos(ang) * (self.ATTACK_RANGE_MELEE - 15)
                w.target_y = enemy.y - math.sin(ang) * (self.ATTACK_RANGE_MELEE - 15)

        dx = w.target_x - w.x; dy = w.target_y - w.y
        dist = math.hypot(dx, dy) + 0.001
        base_speed = 50 + w.get_effective_speed() * 5
        w.vx += ((dx / dist) * base_speed - w.vx) * min(1.0, dt * 8)
        w.vy += ((dy / dist) * base_speed - w.vy) * min(1.0, dt * 8)
        
        new_x = w.x + w.vx * dt
        new_y = w.y + w.vy * dt

        # Obstacle Collision & Crash Damage
        for o in self.obstacles:
            od_new = math.hypot(new_x - o.x, new_y - o.y)
            min_dist = o.radius + 18
            if od_new < min_dist:
                nx = (new_x - o.x) / (od_new + 0.001)
                ny = (new_y - o.y) / (od_new + 0.001)
                new_x = o.x + nx * min_dist
                new_y = o.y + ny * min_dist
                
                impact_speed = math.hypot(w.vx, w.vy)
                if (impact_speed > 250 or w.knockback_x != 0 or w.knockback_y != 0) and w._crash_cooldown <= 0:
                    crash_dmg = max(1, int(impact_speed / 40))
                    w.hp -= crash_dmg
                    w.stats.damage_taken += crash_dmg
                    self.spawn_floating_text(w.x, w.y - 30, f"-{crash_dmg} 💥", QColor(200, 200, 200), size=18)
                    w._crash_cooldown = 0.5
                    o.hp -= crash_dmg
                    o.hit_flash = 0.2
                    if o.hp <= 0: self.destroy_obstacle(o)
                    self.shake(3)
                    self.spawn_hit_particles(w.x, w.y, QColor(200, 200, 200), count=5)
                
                w.vx *= -0.3; w.vy *= -0.3

        new_x = max(self.floor_left + 20, min(self.floor_right - 20, new_x))
        new_y = max(self.floor_top + 20, min(self.floor_bottom - 20, new_y))
        
        for pk in self.pickups[:]:
            if math.hypot(new_x - pk.x, new_y - pk.y) < 30:
                self.apply_pickup_effect(w, pk)
                self.pickups.remove(pk)
                break

        w.x = new_x
        w.y = new_y
        w.home_x = w.x; w.home_y = w.y
        if math.hypot(w.vx, w.vy) > 5: w.facing_angle = math.atan2(w.vy, w.vx)
        if math.hypot(w.vx, w.vy) > 40: w.walk_bob += dt * 12

    def update_warriors(self, dt):
        for w in [self.warrior1, self.warrior2]:
            if not w: continue
            w.hit_flash = max(0, w.hit_flash - dt)
            if hasattr(w, '_crash_cooldown'):
                w._crash_cooldown = max(0, w._crash_cooldown - dt)
        if self.phase == BattlePhase.BATTLE and self.warrior1 and self.warrior2:
            self.update_warrior_movement(self.warrior1, self.warrior2, dt)
            self.update_warrior_movement(self.warrior2, self.warrior1, dt)

    # ── RENDERING ──

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        painter.fillRect(self.rect(), QColor(10, 10, 15))
        
        scale = min(self.width() / self.logical_w, self.height() / self.logical_h)
        draw_w = self.logical_w * scale
        draw_h = self.logical_h * scale
        offset_x = (self.width() - draw_w) / 2
        offset_y = (self.height() - draw_h) / 2
        
        painter.translate(offset_x, offset_y)
        painter.scale(scale, scale)
        painter.setClipRect(QRectF(0, 0, self.logical_w, self.logical_h))
        
        self.render_to_painter(painter)
        painter.end()

    def render_to_painter(self, painter):
        painter.save()
        painter.translate(self.logical_w/2, self.logical_h/2)
        painter.scale(self.camera_zoom, self.camera_zoom)
        painter.translate(-self.logical_w/2, -self.logical_h/2)

        if self.shake_amount > 0.1:
            painter.translate(random.uniform(-1, 1) * self.shake_amount, random.uniform(-1, 1) * self.shake_amount)

        if self.bg_cache: painter.drawPixmap(0, 0, self.bg_cache)

        for o in self.obstacles: self.draw_obstacle(painter, o)
        for pk in self.pickups: self.draw_pickup(painter, pk)
        if self.warrior2: self.draw_warrior(painter, self.warrior2)
        if self.warrior1: self.draw_warrior(painter, self.warrior1)
        for p in self.particles: self.draw_particle(painter, p)
        for ft in self.floating_texts: self.draw_floating_text(painter, ft)

        self.draw_health_bars(painter)
        self.draw_battle_log(painter)

        if self.special_banner_timer > 0: self.draw_special_banner(painter)
        if self.phase == BattlePhase.INTRO: self.draw_intro(painter)
        elif self.phase == BattlePhase.COUNTDOWN: self.draw_countdown(painter)
        elif self.phase == BattlePhase.VICTORY: self.draw_victory(painter)
        elif self.phase == BattlePhase.PAUSED: self.draw_pause_overlay(painter)

        if self.flash_amount > 0.01:
            fc = QColor(self.flash_color); fc.setAlpha(int(self.flash_amount * 180))
            painter.fillRect(QRectF(0, 0, self.logical_w, self.logical_h), fc)

        self.draw_vignette(painter)
        self.draw_watermark(painter)
        if self.show_safe_zones: self.draw_safe_zones(painter)
        painter.restore()

    def draw_cooldown_indicator(self, painter, x, y, color, current_cd, max_cd):
        if current_cd > 0:
            ratio = max(0, min(1, current_cd / max_cd))
            painter.setBrush(QColor(0, 0, 0, 150))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(x, y), 6, 6)
            painter.setPen(QPen(color, 2))
            painter.setBrush(Qt.NoBrush)
            start_angle = 90 * 16
            span_angle = int(-360 * 16 * (1 - ratio))
            painter.drawArc(QRectF(x-6, y-6, 12, 12), start_angle, span_angle)

    def draw_obstacle(self, painter, o: Obstacle):
        painter.save()
        painter.setBrush(QColor(0, 0, 0, 90))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(o.x + 4, o.y + 6), o.radius * 0.95, o.radius * 0.4)
        painter.translate(o.x, o.y); painter.rotate(o.rotation)
        color = QColor(255, 255, 255) if o.hit_flash > 0 else o.color
        grad = QRadialGradient(0, -o.radius * 0.3, o.radius * 1.2)
        grad.setColorAt(0, color.lighter(150)); grad.setColorAt(1, color.darker(180))
        painter.setBrush(grad); painter.setPen(QPen(o.color.darker(220), 2))
        pts = []
        for i in range(7):
            ang = (i / 7) * 2 * math.pi
            r = o.radius * (0.85 + 0.2 * math.sin(i * 1.7))
            pts.append(QPointF(math.cos(ang) * r, math.sin(ang) * r))
        painter.drawPolygon(QPolygonF(pts))
        font = QFont("Arial", int(o.radius * 0.9)); painter.setFont(font)
        painter.setPen(QColor(255, 255, 255, 230))
        painter.drawText(QRectF(-o.radius, -o.radius, o.radius*2, o.radius*2), Qt.AlignCenter, o.emoji)
        painter.restore()

    def draw_pickup(self, painter, pk: Pickup):
        painter.save()
        glow_alpha = int(100 + 50 * math.sin(pk.bob_offset * 2))
        painter.setBrush(QColor(pk.color.red(), pk.color.green(), pk.color.blue(), glow_alpha))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(pk.x, pk.y), 25, 25)
        y_offset = math.sin(pk.bob_offset) * 5
        font = QFont("Arial", 24); painter.setFont(font)
        painter.drawText(QRectF(pk.x - 20, pk.y - 20 + y_offset, 40, 40), Qt.AlignCenter, pk.emoji)
        painter.restore()

    def draw_warrior(self, painter, warrior):
        painter.save()
        painter.setBrush(QColor(0, 0, 0, int(80 * warrior.alpha)))
        painter.setPen(Qt.NoPen)
        shadow_y = warrior.y + 55 * warrior.scale
        painter.drawEllipse(QPointF(warrior.x, shadow_y), 35 * warrior.scale, 8 * warrior.scale)

        if warrior.invincibility_timer > 0:
            t = self.elapsed.elapsed() / 50.0
            for i in range(5):
                radius = 45 + i * 8 + 5 * math.sin(t + i * 2)
                alpha = int(80 - i * 12)
                painter.setBrush(QColor(255, 215, 0, alpha))
                painter.setPen(QPen(QColor(255, 255, 255, alpha), 2))
                painter.drawEllipse(QPointF(warrior.x, warrior.y), radius, radius)
        if warrior.shield_timer > 0:
            t = self.elapsed.elapsed() / 80.0
            radius = 50 + 3 * math.sin(t)
            painter.setBrush(QColor(100, 200, 255, 40))
            painter.setPen(QPen(QColor(100, 200, 255, 180), 3))
            painter.drawEllipse(QPointF(warrior.x, warrior.y), radius, radius)
        if warrior.haste_timer > 0:
            t = self.elapsed.elapsed() / 30.0
            for i in range(3):
                offset = (t + i * 0.5) % 1.0
                alpha = int(100 * (1 - offset))
                radius = 40 + offset * 20
                painter.setBrush(QColor(255, 255, 0, alpha))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(QPointF(warrior.x, warrior.y), radius, radius)
        if warrior.guard_up:
            painter.setPen(QPen(QColor(100, 200, 255, 120), 3, Qt.DashLine))
            painter.setBrush(QColor(100, 200, 255, 30))
            painter.drawEllipse(QPointF(warrior.x, warrior.y), 60, 60)

        painter.save()
        painter.translate(warrior.x, warrior.y + math.sin(warrior.walk_bob) * 3)
        if warrior.hit_stumble > 0:
            painter.translate(random.uniform(-3, 3), random.uniform(-3, 3))
        painter.scale(warrior.scale, warrior.scale)
        if math.cos(warrior.facing_angle) < 0: painter.scale(-1, 1)
            
        font = QFont(); font.setPointSize(58); painter.setFont(font)
        if warrior.hit_flash > 0: painter.setPen(QColor(255, 80, 80, int(255 * warrior.alpha)))
        else: painter.setPen(QColor(255, 255, 255, int(255 * warrior.alpha)))
        painter.drawText(QRectF(-50, -50, 100, 100), Qt.AlignCenter, warrior.emoji)
        painter.restore()

        icon_y = warrior.y - 70
        status_effects = []
        if warrior.stun_timer > 0: status_effects.append(("💫", QColor(255, 255, 100)))
        if warrior.freeze_timer > 0: status_effects.append(("🧊", QColor(150, 220, 255)))
        if warrior.poison_timer > 0: status_effects.append(("☠️", QColor(100, 200, 50)))
        if warrior.burn_timer > 0: status_effects.append(("🔥", QColor(255, 100, 0)))
        if warrior.slow_timer > 0: status_effects.append(("🐌", QColor(150, 200, 255)))
        if warrior.weaken_timer > 0: status_effects.append(("🔻", QColor(200, 100, 100)))
        if warrior.mark_timer > 0: status_effects.append(("🎯", QColor(255, 50, 50)))
        if warrior.buff_timer > 0: status_effects.append(("💪", QColor(255, 200, 0)))
        if warrior.haste_timer > 0: status_effects.append(("⚡", QColor(255, 255, 0)))
        if warrior.rage_pickup_timer > 0: status_effects.append(("🔱", QColor(255, 50, 50)))
        if warrior.shield_timer > 0: status_effects.append(("🛡️", QColor(100, 200, 255)))
        if warrior.invincibility_timer > 0: status_effects.append(("⭐", QColor(255, 215, 0)))
        
        for emoji, color in status_effects:
            font = QFont("Arial", 14); painter.setFont(font)
            painter.setPen(color)
            painter.drawText(QRectF(warrior.x - 15, icon_y, 30, 25), Qt.AlignCenter, emoji)
            icon_y -= 22

        painter.setPen(QColor(255, 255, 255, int(220 * warrior.alpha)))
        font = QFont("Arial", 10, QFont.Bold); painter.setFont(font)
        painter.drawText(QRectF(warrior.x - 60, warrior.y + 45, 120, 20), Qt.AlignCenter, f"{warrior.name} ({warrior.class_name})")

        if warrior.combo > 1:
            font = QFont("Arial", 12, QFont.Bold); painter.setFont(font)
            painter.setPen(QColor(255, 215, 0))
            painter.drawText(QRectF(warrior.x - 60, warrior.y + 60, 120, 20), Qt.AlignCenter, f"🔥 x{warrior.combo}")
            
        # Action Cooldown Indicators
        cd_y = warrior.y + 80
        cd_spacing = 16
        cd_start_x = warrior.x - cd_spacing
        self.draw_cooldown_indicator(painter, cd_start_x, cd_y, QColor(180, 0, 255), warrior.special_cooldown, SPECIAL_COOLDOWN)
        self.draw_cooldown_indicator(painter, cd_start_x + cd_spacing, cd_y, QColor(0, 255, 100), warrior.heal_cooldown, HEAL_COOLDOWN_MAX)
        self.draw_cooldown_indicator(painter, cd_start_x + cd_spacing * 2, cd_y, QColor(255, 200, 0), warrior.buff_cooldown, BUFF_COOLDOWN_MAX)
        
        painter.restore()

    def draw_particle(self, painter, p):
        alpha = int(255 * (p.life / p.max_life))
        size = p.size * (p.life / p.max_life) if p.shrink else p.size
        if p.emoji:
            font = QFont("Arial", int(size * 2)); painter.setFont(font)
            painter.setPen(QColor(255, 255, 255, alpha))
            painter.drawText(QRectF(p.x - size, p.y - size, size * 2, size * 2), Qt.AlignCenter, p.emoji)
        else:
            color = QColor(p.color); color.setAlpha(alpha)
            painter.setBrush(color); painter.setPen(Qt.NoPen)
            painter.save()
            painter.translate(p.x, p.y); painter.rotate(p.rotation)
            if p.shape == "circle": painter.drawEllipse(QPointF(0, 0), size, size)
            elif p.shape == "square": painter.drawRect(QRectF(-size, -size, size*2, size*2))
            elif p.shape == "star":
                painter.scale(size/5, size/5)
                painter.drawPath(self.star_path)
            painter.restore()

    def draw_floating_text(self, painter, ft):
        alpha = int(255 * (ft.life / ft.max_life))
        color = QColor(ft.color); color.setAlpha(alpha)
        font = QFont("Arial", ft.size, QFont.Bold); painter.setFont(font)
        if ft.is_speech:
            rect = painter.boundingRect(QRectF(ft.x-100, ft.y-20, 200, 40), Qt.AlignCenter, ft.text)
            painter.setBrush(QColor(0, 0, 0, int(alpha * 0.7)))
            painter.setPen(QPen(color, 1))
            painter.drawRoundedRect(rect.adjusted(-5, -5, 5, 5), 5, 5)
            painter.setPen(color)
            painter.drawText(rect, Qt.AlignCenter, ft.text)
        else:
            painter.setPen(QColor(0, 0, 0, alpha))
            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                painter.drawText(QRectF(ft.x - 60 + dx, ft.y - 20 + dy, 120, 40), Qt.AlignCenter, ft.text)
            painter.setPen(color)
            painter.drawText(QRectF(ft.x - 60, ft.y - 20, 120, 40), Qt.AlignCenter, ft.text)

    def draw_health_bars(self, painter):
        if not self.warrior1 or not self.warrior2: return
        margin = 15
        bar_w = min(220, self.logical_w * 0.35)
        bar_h = 20
        self.draw_health_bar(painter, margin, margin, bar_w, bar_h, self.warrior1, True)
        self.draw_health_bar(painter, self.logical_w - margin - bar_w, margin, bar_w, bar_h, self.warrior2, False)
        if self.phase in (BattlePhase.INTRO, BattlePhase.COUNTDOWN, BattlePhase.BATTLE, BattlePhase.ACTION_ANIM, BattlePhase.PAUSED):
            self.draw_win_odds(painter)

    def draw_health_bar(self, painter, x, y, w, h, warrior, align_left=True):
        painter.setBrush(QColor(0, 0, 0, 180)); painter.setPen(QPen(QColor(255, 255, 255, 80), 1))
        painter.drawRoundedRect(QRectF(x, y, w, h), 4, 4)
        hp_ratio = max(0.0, warrior.displayed_hp / warrior.max_hp)
        fill_w = w * hp_ratio
        if hp_ratio > 0.5: color = QColor(80, 220, 80)
        elif hp_ratio > 0.25: color = QColor(220, 200, 80)
        else: color = QColor(220, 60, 60)
        fill_x = x if align_left else (x + w - fill_w)
        painter.setBrush(color); painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(QRectF(fill_x, y, fill_w, h), 4, 4)
        painter.setPen(QColor(255, 255, 255)); font = QFont("Arial", 9, QFont.Bold); painter.setFont(font)
        painter.drawText(QRectF(x, y, w, h), Qt.AlignCenter, f"{warrior.hp}/{warrior.max_hp}")
        
        mp_y = y + h + 4; mp_h = 6
        painter.setBrush(QColor(0, 0, 0, 180)); painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(QRectF(x, mp_y, w, mp_h), 2, 2)
        mp_fill_w = w * max(0.0, warrior.displayed_mp / warrior.max_mp)
        mp_fill_x = x if align_left else (x + w - mp_fill_w)
        painter.setBrush(QColor(0, 150, 255))
        painter.drawRoundedRect(QRectF(mp_fill_x, mp_y, mp_fill_w, mp_h), 2, 2)

    def draw_win_odds(self, painter):
        if not self.warrior1 or not self.warrior2: return
        bar_w = min(self.logical_w - 40, 300)
        bar_h = 12
        bar_x = (self.logical_w - bar_w) / 2
        bar_y = 160
        
        painter.setBrush(QColor(0, 0, 0, 180)); painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(QRectF(bar_x, bar_y, bar_w, bar_h), 4, 4)
        
        w1_fill = bar_w * self.w1_odds
        painter.setBrush(self.warrior1.color)
        painter.drawRoundedRect(QRectF(bar_x, bar_y, w1_fill, bar_h), 4, 4)
        
        painter.setPen(QColor(255, 255, 255, 200))
        font = QFont("Arial", 8, QFont.Bold); painter.setFont(font)
        painter.drawText(QRectF(bar_x, bar_y - 14, bar_w, 12), Qt.AlignCenter, 
                         f"Win Odds: {self.w1_odds*100:.0f}% vs {self.w2_odds*100:.0f}%")

    def draw_battle_log(self, painter):
        if not self.battle_log: return
        log_w = min(self.logical_w - 40, 400)
        log_h = 80
        log_x = (self.logical_w - log_w) / 2
        log_y = 180 if self.w1_odds != 0.5 else 70
        
        painter.setBrush(QColor(0, 0, 0, 130)); painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(QRectF(log_x, log_y, log_w, log_h), 6, 6)
        recent = self.battle_log[-4:]; font = QFont("Arial", 9); painter.setFont(font)
        for i, msg in enumerate(reversed(recent)):
            alpha = int(255 * (1.0 - i * 0.22))
            painter.setPen(QColor(240, 240, 240, alpha))
            painter.drawText(QRectF(log_x + 8, log_y + 5 + i * 18, log_w - 16, 18), Qt.AlignCenter, msg)

    def draw_safe_zones(self, painter):
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 0, 0, 40))
        if self.canvas_mode == CanvasMode.SHORT_9_16:
            painter.drawRect(QRectF(0, self.logical_h * 0.80, self.logical_w, self.logical_h * 0.20))
            painter.drawRect(QRectF(self.logical_w * 0.85, 0, self.logical_w * 0.15, self.logical_h))

    def draw_special_banner(self, painter):
        alpha = min(1.0, self.special_banner_timer / 0.3) * min(1.0, (1.5 - self.special_banner_timer) / 0.3 + 0.3)
        alpha = max(0, min(1, alpha))
        painter.fillRect(QRectF(0, 0, self.logical_w, self.logical_h), QColor(80, 40, 120, int(60 * alpha)))
        font = QFont("Arial", 28, QFont.Bold); painter.setFont(font)
        painter.setPen(QColor(255, 255, 255, int(255 * alpha)))
        painter.drawText(QRectF(0, self.logical_h // 2 - 30, self.logical_w, 60), Qt.AlignCenter, self.special_banner_text)

    def draw_intro(self, painter):
        painter.fillRect(QRectF(0, 0, self.logical_w, self.logical_h), QColor(0, 0, 0, 160))
        pulse = 1.0 + 0.15 * math.sin(self.intro_timer * 5)
        painter.save()
        painter.translate(self.logical_w / 2, self.logical_h / 2)
        painter.scale(pulse, pulse)
        painter.setPen(QColor(255, 215, 0)); font = QFont("Arial", 64, QFont.Bold); painter.setFont(font)
        painter.drawText(QRectF(-120, -60, 240, 120), Qt.AlignCenter, "VS")
        painter.restore()
        if self.warrior1 and self.warrior2:
            font = QFont("Arial", 48); painter.setFont(font); painter.setPen(QColor(255, 255, 255))
            painter.drawText(QRectF(0, self.logical_h * 0.28, self.logical_w // 2, 80), Qt.AlignCenter, self.warrior1.emoji)
            painter.drawText(QRectF(self.logical_w // 2, self.logical_h * 0.28, self.logical_w // 2, 80), Qt.AlignCenter, self.warrior2.emoji)
            if self.intro_timer > 1.0:
                alpha = int(255 * min(1.0, (self.intro_timer - 1.0) / 0.5))
                font = QFont("Arial", 11, QFont.Bold); painter.setFont(font)
                painter.setPen(QColor(255, 215, 0, alpha))
                painter.drawText(QRectF(0, self.logical_h * 0.80, self.logical_w, 20), Qt.AlignCenter,
                                 f"Win Odds: {self.w1_odds*100:.0f}% vs {self.w2_odds*100:.0f}%")
                font = QFont("Arial", 10); painter.setFont(font)
                painter.setPen(QColor(200, 200, 200, alpha))
                painter.drawText(QRectF(10, self.logical_h * 0.83, self.logical_w - 20, 30), Qt.AlignCenter, self.odds_analysis)

    def draw_countdown(self, painter):
        painter.fillRect(QRectF(0, 0, self.logical_w, self.logical_h), QColor(0, 0, 0, 100))
        text = str(self.countdown_value) if self.countdown_value > 0 else "FIGHT!"
        font = QFont("Arial", int(80 * (2.5 - (self.phase_timer / 0.8) * 1.5)), QFont.Bold); painter.setFont(font)
        color = QColor(255, 215, 0) if self.countdown_value > 0 else QColor(255, 50, 50)
        painter.setPen(color)
        painter.drawText(QRectF(0, 0, self.logical_w, self.logical_h), Qt.AlignCenter, text)

    def draw_victory(self, painter):
        painter.fillRect(QRectF(0, 0, self.logical_w, self.logical_h), QColor(255, 215, 0, min(40, int(self.phase_timer * 30))))
        winner = self.warrior1 if self.warrior1.is_winner else self.warrior2
        font = QFont("Arial", 48); painter.setFont(font); painter.setPen(QColor(255, 215, 0))
        painter.drawText(QRectF(0, self.logical_h * 0.2, self.logical_w, 80), Qt.AlignCenter, "🏆")
        font = QFont("Arial", 24, QFont.Bold); painter.setFont(font); painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRectF(0, self.logical_h * 0.32, self.logical_w, 50), Qt.AlignCenter, "VICTORY!")
        font = QFont("Arial", 72); painter.setFont(font); painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRectF(0, self.logical_h * 0.42, self.logical_w, 100), Qt.AlignCenter, winner.emoji)
        font = QFont("Arial", 22, QFont.Bold); painter.setFont(font); painter.setPen(QColor(255, 215, 0))
        painter.drawText(QRectF(0, self.logical_h * 0.55, self.logical_w, 40), Qt.AlignCenter, winner.name)
        
        if self.phase_timer > 1.0:
            stats_alpha = min(255, int((self.phase_timer - 1.0) * 200))
            font = QFont("Arial", 10); painter.setFont(font)
            painter.setPen(QColor(200, 200, 200, stats_alpha))
            stats_y = self.logical_h * 0.65
            stats_text = (f"DMG Dealt: {winner.stats.damage_dealt}  |  Max Combo: {winner.stats.max_combo}  |  "
                         f"Crits: {winner.stats.crits}  |  Blocks: {winner.stats.blocks}  |  Dodges: {winner.stats.dodges}")
            painter.drawText(QRectF(0, stats_y, self.logical_w, 20), Qt.AlignCenter, stats_text)
            
            if winner.stats.damage_by_type:
                bar_y = stats_y + 25
                bar_w = min(self.logical_w * 0.6, 400)
                bar_x = (self.logical_w - bar_w) / 2
                total_dmg = sum(winner.stats.damage_by_type.values()) + 0.001
                x_off = 0
                type_colors = {
                    DamageType.PHYSICAL: QColor(200, 200, 200), DamageType.FIRE: QColor(255, 100, 0),
                    DamageType.ICE: QColor(150, 220, 255), DamageType.LIGHTNING: QColor(255, 255, 0),
                    DamageType.POISON: QColor(100, 200, 50), DamageType.HOLY: QColor(255, 255, 200),
                }
                for dt, d in winner.stats.damage_by_type.items():
                    seg_w = (d / total_dmg) * bar_w
                    painter.setBrush(type_colors.get(dt, QColor(150)))
                    painter.setPen(Qt.NoPen)
                    painter.drawRect(QRectF(bar_x + x_off, bar_y, seg_w, 8))
                    x_off += seg_w

    def draw_pause_overlay(self, painter):
        painter.fillRect(QRectF(0, 0, self.logical_w, self.logical_h), QColor(0, 0, 0, 160))
        font = QFont("Arial", 48, QFont.Bold); painter.setFont(font)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRectF(0, 0, self.logical_w, self.logical_h), Qt.AlignCenter, "⏸ PAUSED")

    def draw_vignette(self, painter):
        gradient = QRadialGradient(self.logical_w/2, self.logical_h/2, self.logical_w*0.8)
        gradient.setColorAt(0.6, QColor(0, 0, 0, 0))
        gradient.setColorAt(1.0, QColor(0, 0, 0, 150))
        painter.fillRect(QRectF(0, 0, self.logical_w, self.logical_h), gradient)

    def draw_watermark(self, painter):
        if self.watermark_text:
            font = QFont("Arial", 10, QFont.Bold); painter.setFont(font)
            painter.setPen(QColor(255, 255, 255, 100))
            painter.drawText(QRectF(15, self.logical_h - 30, self.logical_w//2, 15), Qt.AlignLeft, self.watermark_text)

    def capture_screenshot(self, filename: str, scale=2.0):
        pixmap = QPixmap(int(self.logical_w * scale), int(self.logical_h * scale))
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.scale(scale, scale)
        self.render_to_painter(painter)
        painter.end()
        pixmap.save(filename)


# ═══════════════════════════════════════════════════════════════
# VIDEO EXPORTER (True Resolution Independence)
# ═══════════════════════════════════════════════════════════════

class VideoExporter:
    @staticmethod
    def export_battle(w1_name, w1_class, w2_name, w2_class, arena_name, output_dir, canvas_mode: CanvasMode, export_scale: int, parent=None):
        arena = BattleArena()
        arena.apply_canvas_mode(canvas_mode)
        arena.setup_battle(w1_name, w1_class, w2_name, w2_class, arena_name)
        arena.timer.stop() 
        
        fps = 60; max_frames = fps * 30; dt = 1.0 / fps
        logical_w, logical_h = canvas_mode.value
        
        out_w = logical_w * export_scale
        out_h = logical_h * export_scale

        progress = QProgressDialog(f"Rendering & Encoding Video ({out_w}x{out_h})...", "Cancel", 0, max_frames, parent)
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle("YouTube Video Export")
        progress.setMinimumDuration(0)
        
        os.makedirs(output_dir, exist_ok=True)
        output_mp4 = os.path.join(output_dir, f"battle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")

        ffmpeg_path = shutil.which("ffmpeg")
        process = None
        output_dir_frames = None
        
        if ffmpeg_path:
            cmd = [
                ffmpeg_path, "-y",
                "-f", "rawvideo", "-vcodec", "rawvideo",
                "-s", f"{out_w}x{out_h}", "-pix_fmt", "rgba",
                "-r", str(fps), "-i", "-",
                "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                "-bf", "2", "-g", str(fps * 2),
                output_mp4
            ]
            try:
                process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                QMessageBox.warning(parent, "FFmpeg Error", f"Failed to start FFmpeg:\n{e}\n\nFalling back to PNG sequence.")
                process = None

        if not process:
            output_dir_frames = os.path.join(output_dir, f"battle_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            os.makedirs(output_dir_frames, exist_ok=True)

        frame_count = 0; battle_over_timer = 0.0

        for i in range(max_frames):
            if progress.wasCanceled(): 
                if process: process.kill()
                break
                
            arena.step_simulation(dt)
            
            pixmap = QPixmap(out_w, out_h)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.TextAntialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            painter.scale(export_scale, export_scale)
            arena.render_to_painter(painter)
            painter.end()

            if process:
                img = pixmap.toImage().convertToFormat(QImage.Format_RGBA8888)
                ptr = img.constBits()
                ptr.setsize(img.sizeInBytes())
                process.stdin.write(bytes(ptr))
            else:
                frame_path = os.path.join(output_dir_frames, f"frame_{frame_count:05d}.png")
                pixmap.save(frame_path, "PNG")

            frame_count += 1
            progress.setValue(frame_count)
            QApplication.processEvents()

            if arena.phase == BattlePhase.VICTORY:
                battle_over_timer += dt
                if battle_over_timer > 4.0: break

        if process:
            process.stdin.close()
            process.wait()
            
        progress.close()
        arena.timer.start() 
        
        if progress.wasCanceled():
            QMessageBox.warning(parent, "Canceled", "Export was canceled. Partial files may exist.")
            return

        if not process:
            script_path = os.path.join(output_dir_frames, "convert_to_mp4.bat")
            ffmpeg_cmd = f'ffmpeg -framerate {fps} -i frame_%05d.png -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p -movflags +faststart "{output_mp4}"'
            with open(script_path, "w") as f: f.write(ffmpeg_cmd)
            QMessageBox.information(parent, "Fallback Export Complete", 
                f"FFmpeg not found in system PATH!\n\nRendered {frame_count} PNG frames to:\n{output_dir_frames}\n\nTo create the MP4 video:\n1. Download FFmpeg.\n2. Run: {script_path}")
        else:
            QMessageBox.information(parent, "Export Complete!", f"Successfully rendered and encoded {frame_count} frames directly to MP4!\n\nSaved to: {output_mp4}")


# ═══════════════════════════════════════════════════════════════
# RIGHT PANEL (Modern Tabbed UI)
# ═══════════════════════════════════════════════════════════════

class RightPanel(QWidget):
    battle_started = Signal(str, str, str, str, str)
    battle_reset = Signal(); screenshot_requested = Signal()
    settings_changed = Signal(dict); export_requested = Signal()
    pause_toggled = Signal(); next_battle_requested = Signal()
    canvas_changed = Signal(object)
    safe_zone_toggled = Signal(bool)
    difficulty_changed = Signal(object)
    tournament_started = Signal(list, dict)

    def __init__(self):
        super().__init__()
        self.setFixedWidth(360)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("⚔️ AI BATTLE ARENA V20")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFD700; padding: 15px; background-color: #11111a;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.tabs = QTabWidget()
        
        # ── Battle Tab ──
        battle_tab = QWidget()
        bt_layout = QVBoxLayout(battle_tab)
        
        layout_group = QGroupBox("Video Layout")
        l_layout = QVBoxLayout(layout_group)
        fmt_layout = QHBoxLayout()
        fmt_layout.addWidget(QLabel("Format:"))
        self.canvas_combo = QComboBox()
        self.canvas_combo.addItem("Short (9:16)", CanvasMode.SHORT_9_16)
        self.canvas_combo.addItem("Video (16:9)", CanvasMode.VIDEO_16_9)
        self.canvas_combo.addItem("Square (1:1)", CanvasMode.SQUARE_1_1)
        self.canvas_combo.currentIndexChanged.connect(self.emit_canvas_change)
        fmt_layout.addWidget(self.canvas_combo)
        l_layout.addLayout(fmt_layout)
        self.safe_zone_cb = QCheckBox("Show Safe Zones")
        self.safe_zone_cb.stateChanged.connect(self.emit_safe_zone)
        l_layout.addWidget(self.safe_zone_cb)
        bt_layout.addWidget(layout_group)

        arena_group = QGroupBox("Arena")
        ag_layout = QVBoxLayout(arena_group)
        self.arena_combo = QComboBox()
        self.arena_combo.addItems(list(ARENAS_DB.keys()))
        ag_layout.addWidget(self.arena_combo)
        bt_layout.addWidget(arena_group)

        warrior_group = QGroupBox("Warriors & Classes")
        wlayout = QGridLayout(warrior_group)
        names = list(WARRIORS_DB.keys())
        classes = list(CLASSES_DB.keys())
        wlayout.addWidget(QLabel(" Fighter 1:"), 0, 0)
        self.w1_combo = QComboBox(); self.w1_combo.addItems(names); self.w1_combo.setCurrentText("Ninja")
        wlayout.addWidget(self.w1_combo, 0, 1)
        wlayout.addWidget(QLabel(" Class:"), 1, 0)
        self.c1_combo = QComboBox(); self.c1_combo.addItems(classes); self.c1_combo.setCurrentText("Fighter")
        wlayout.addWidget(self.c1_combo, 1, 1)
        wlayout.addWidget(QLabel(" Fighter 2:"), 2, 0)
        self.w2_combo = QComboBox(); self.w2_combo.addItems(names); self.w2_combo.setCurrentText("Knight")
        wlayout.addWidget(self.w2_combo, 2, 1)
        wlayout.addWidget(QLabel(" Class:"), 3, 0)
        self.c2_combo = QComboBox(); self.c2_combo.addItems(classes); self.c2_combo.setCurrentText("Fighter")
        wlayout.addWidget(self.c2_combo, 3, 1)
        random_btn = QPushButton("🎲 Random Matchup"); random_btn.clicked.connect(self.randomize)
        wlayout.addWidget(random_btn, 4, 0, 1, 2)
        bt_layout.addWidget(warrior_group)

        diff_group = QGroupBox("AI Difficulty")
        dg_layout = QVBoxLayout(diff_group)
        self.diff_combo = QComboBox()
        for d in AIDifficulty:
            self.diff_combo.addItem(d.value, d)
        self.diff_combo.currentIndexChanged.connect(self.emit_difficulty)
        dg_layout.addWidget(self.diff_combo)
        bt_layout.addWidget(diff_group)

        ctrl_group = QGroupBox("Controls")
        ctrl_layout = QVBoxLayout(ctrl_group)
        self.start_btn = QPushButton("▶️  START BATTLE  [Space]")
        self.start_btn.setStyleSheet("QPushButton { font-size: 14px; font-weight: bold; padding: 12px; background-color: #2d7a2d; color: white; border-radius: 4px; } QPushButton:hover { background-color: #3a9a3a; }")
        self.start_btn.clicked.connect(self.emit_start)
        ctrl_layout.addWidget(self.start_btn)

        btn_row1 = QHBoxLayout()
        self.pause_btn = QPushButton("⏸ Pause [P]")
        self.pause_btn.clicked.connect(self.pause_toggled.emit)
        btn_row1.addWidget(self.pause_btn)
        self.reset_btn = QPushButton("🔄 Reset [R]")
        self.reset_btn.clicked.connect(self.battle_reset.emit)
        btn_row1.addWidget(self.reset_btn)
        ctrl_layout.addLayout(btn_row1)

        btn_row2 = QHBoxLayout()
        self.screenshot_btn = QPushButton("📸 Shot [S]")
        self.screenshot_btn.clicked.connect(self.screenshot_requested.emit)
        btn_row2.addWidget(self.screenshot_btn)
        self.next_btn = QPushButton("⏭ Next [N]")
        self.next_btn.clicked.connect(self.next_battle_requested.emit)
        btn_row2.addWidget(self.next_btn)
        ctrl_layout.addLayout(btn_row2)
        bt_layout.addWidget(ctrl_group)
        bt_layout.addStretch()
        self.tabs.addTab(battle_tab, "⚔️ Battle")

        # ── Tournament Tab ──
        tourney_tab = QWidget()
        tt_layout = QVBoxLayout(tourney_tab)
        tt_layout.addWidget(QLabel("🏆 Tournament Mode\n8-warrior single elimination"))
        self.tourney_list = QTextEdit()
        self.tourney_list.setReadOnly(True)
        self.tourney_list.setMinimumHeight(200)
        tt_layout.addWidget(self.tourney_list)
        
        add_random_btn = QPushButton("🎲 Add 8 Random Warriors")
        add_random_btn.clicked.connect(self.add_random_tournament)
        tt_layout.addWidget(add_random_btn)
        
        clear_btn = QPushButton("🧹 Clear Participants")
        clear_btn.clicked.connect(self.clear_tournament)
        tt_layout.addWidget(clear_btn)
        
        self.start_tourney_btn = QPushButton("🚀 Start Tournament")
        self.start_tourney_btn.setStyleSheet("QPushButton { font-size: 13px; font-weight: bold; padding: 10px; background-color: #8a6a2a; color: white; border-radius: 4px; }")
        self.start_tourney_btn.clicked.connect(self.emit_start_tournament)
        tt_layout.addWidget(self.start_tourney_btn)
        
        self.tourney_participants: List[str] = []
        self.tourney_classes: Dict[str, str] = {}
        tt_layout.addStretch()
        self.tabs.addTab(tourney_tab, "🏆 Tournament")

        # ── Export Tab ──
        export_tab = QWidget()
        ex_layout = QVBoxLayout(export_tab)
        
        export_group = QGroupBox("Video Export")
        eg_layout = QVBoxLayout(export_group)
        
        eg_layout.addWidget(QLabel("Export Resolution:"))
        self.quality_combo = QComboBox()
        for q in ExportQuality:
            self.quality_combo.addItem(q.value[0], q.value[1])
        eg_layout.addWidget(self.quality_combo)
        
        self.export_btn = QPushButton("📹 Export MP4")
        self.export_btn.setStyleSheet("QPushButton { font-size: 13px; font-weight: bold; padding: 10px; background-color: #8a4a8a; color: white; border-radius: 4px; } QPushButton:hover { background-color: #aa6aaa; }")
        self.export_btn.clicked.connect(self.export_requested.emit)
        eg_layout.addWidget(self.export_btn)
        
        ex_layout.addWidget(export_group)
        ex_layout.addStretch()
        self.tabs.addTab(export_tab, "📹 Export")

        # ── Stats & Log Tab ──
        stats_tab = QWidget()
        st_layout = QVBoxLayout(stats_tab)
        
        stats_group = QGroupBox("📊 Battle Statistics")
        stats_layout = QVBoxLayout(stats_group)
        self.stats_label = QLabel("Start a battle to see stats...")
        self.stats_label.setStyleSheet("QLabel { background-color: #11111a; color: #88ccff; font-family: 'Consolas', 'Monaco', monospace; font-size: 11px; padding: 10px; border-radius: 4px; border: 1px solid #252535; }")
        self.stats_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)
        st_layout.addWidget(stats_group)
        
        log_group = QGroupBox("📜 Live Battle Log")
        log_layout = QVBoxLayout(log_group)
        self.log_display = QLabel("Select warriors and press Start!")
        self.log_display.setStyleSheet("QLabel { background-color: #11111a; color: #00ff88; font-family: 'Consolas', 'Monaco', monospace; font-size: 11px; padding: 10px; border-radius: 4px; border: 1px solid #252535; }")
        self.log_display.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.log_display.setWordWrap(True)
        log_layout.addWidget(self.log_display)
        st_layout.addWidget(log_group)
        st_layout.addStretch()
        self.tabs.addTab(stats_tab, "📊 Stats & Log")

        # ── Settings Tab ──
        settings_tab = QWidget()
        se_layout = QVBoxLayout(settings_tab)
        settings_group = QGroupBox("Recording Settings")
        s_layout = QVBoxLayout(settings_group)
        self.auto_queue_cb = QCheckBox("♾️ Auto-Queue Next Battle")
        self.auto_queue_cb.stateChanged.connect(self.emit_settings)
        s_layout.addWidget(self.auto_queue_cb)
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("🐢 Speed:"))
        self.speed_slider = QSlider(Qt.Horizontal); self.speed_slider.setMinimum(50); self.speed_slider.setMaximum(200); self.speed_slider.setValue(100)
        self.speed_slider.valueChanged.connect(self.emit_settings)
        speed_layout.addWidget(self.speed_slider)
        self.speed_label = QLabel("1.0x"); speed_layout.addWidget(self.speed_label)
        s_layout.addLayout(speed_layout)
        wm_layout = QHBoxLayout()
        wm_layout.addWidget(QLabel("🏷️ Watermark:"))
        self.wm_input = QLineEdit("@YourChannel"); self.wm_input.textChanged.connect(self.emit_settings)
        wm_layout.addWidget(self.wm_input)
        s_layout.addLayout(wm_layout)
        se_layout.addWidget(settings_group)
        se_layout.addStretch()
        self.tabs.addTab(settings_tab, "⚙️ Settings")
        
        layout.addWidget(self.tabs)
        self.tourney_list_text = "Add participants to begin."

    def add_random_tournament(self):
        names = random.sample(list(WARRIORS_DB.keys()), 8)
        classes_list = list(CLASSES_DB.keys())
        self.tourney_participants = names
        self.tourney_classes = {n: random.choice(classes_list) for n in names}
        self.update_tourney_display()

    def clear_tournament(self):
        self.tourney_participants.clear()
        self.tourney_classes.clear()
        self.update_tourney_display()

    def update_tourney_display(self):
        if not self.tourney_participants:
            self.tourney_list.setText("No participants yet. Click 'Add 8 Random'.")
        else:
            text = "Participants:\n"
            for i, n in enumerate(self.tourney_participants, 1):
                cls = self.tourney_classes.get(n, "Fighter")
                text += f"  {i}. {n} ({cls})\n"
            self.tourney_list.setText(text)

    def emit_start_tournament(self):
        if len(self.tourney_participants) >= 2:
            self.tournament_started.emit(self.tourney_participants.copy(), self.tourney_classes.copy())

    def randomize(self):
        names = list(WARRIORS_DB.keys())
        classes = list(CLASSES_DB.keys())
        n1 = random.choice(names); n2 = random.choice(names)
        while n2 == n1: n2 = random.choice(names)
        self.w1_combo.setCurrentText(n1); self.w2_combo.setCurrentText(n2)
        self.c1_combo.setCurrentText(random.choice(classes))
        self.c2_combo.setCurrentText(random.choice(classes))

    def emit_start(self):
        self.battle_started.emit(
            self.w1_combo.currentText(), self.c1_combo.currentText(),
            self.w2_combo.currentText(), self.c2_combo.currentText(),
            self.arena_combo.currentText()
        )

    def get_settings(self) -> dict:
        speed = self.speed_slider.value() / 100.0
        return {"auto_queue": self.auto_queue_cb.isChecked(), "speed": speed, "watermark": self.wm_input.text()}

    def emit_settings(self):
        speed = self.speed_slider.value() / 100.0
        self.speed_label.setText(f"{speed:.1f}x")
        self.settings_changed.emit(self.get_settings())

    def emit_canvas_change(self):
        self.canvas_changed.emit(self.canvas_combo.currentData())

    def emit_safe_zone(self):
        self.safe_zone_toggled.emit(self.safe_zone_cb.isChecked())

    def emit_difficulty(self):
        self.difficulty_changed.emit(self.diff_combo.currentData())


# ═══════════════════════════════════════════════════════════════
# MAIN WINDOW
# ═══════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⚔️ AI Battle Arena V20 — Bloodthirst & Tactics")
        self.resize(1000, 700)
        self.setStyleSheet("""
            QMainWindow { background-color: #12121a; }
            QWidget { color: #ddd; font-family: 'Segoe UI', 'Arial', sans-serif; }
            QFrame#ArenaFrame { background-color: #050508; border: 1px solid #1a1a2e; border-radius: 8px; }
            QGroupBox { color: #ccc; border: 1px solid #2a2a3e; border-radius: 6px; margin-top: 14px; padding-top: 16px; font-weight: bold; background-color: #1a1a24; }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 5px; }
            QLabel { color: #ddd; background: transparent; }
            QComboBox, QLineEdit, QTextEdit, QSpinBox { background-color: #252535; color: white; padding: 6px; border: 1px solid #3a3a4e; border-radius: 4px; min-height: 22px; }
            QComboBox::drop-down { border: none; width: 20px; }
            QComboBox QAbstractItemView { background-color: #252535; color: white; selection-background-color: #4a4a6e; outline: none; }
            QCheckBox { color: #ddd; spacing: 8px; }
            QSlider::groove:horizontal { border: 1px solid #3a3a4e; height: 6px; background: #252535; border-radius: 3px; }
            QSlider::handle:horizontal { background: #FFD700; border: 2px solid #e6c300; width: 16px; margin: -6px 0; border-radius: 8px; }
            QSlider::handle:horizontal:hover { background: #FFF700; }
            QPushButton { background-color: #2a2a3e; color: white; border: 1px solid #3a3a4e; padding: 8px 12px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #3a3a4e; border-color: #4a4a6e; }
            QPushButton:pressed { background-color: #22222e; }
            QTabWidget::pane { border: 1px solid #2a2a3e; border-radius: 6px; background: transparent; }
            QTabBar::tab { background: #1a1a24; color: #888; padding: 8px 16px; border: 1px solid #2a2a3e; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; margin-right: 2px; }
            QTabBar::tab:selected { background: #252535; color: #fff; border-color: #3a3a4e; }
        """)

        self.arena = BattleArena()
        self.log_lines = []

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.arena_frame = QFrame()
        self.arena_frame.setObjectName("ArenaFrame")
        arena_layout = QVBoxLayout(self.arena_frame)
        arena_layout.setContentsMargins(0, 0, 0, 0)
        arena_layout.addWidget(self.arena, alignment=Qt.AlignCenter)
        layout.addWidget(self.arena_frame, stretch=1)

        right_side = QWidget()
        right_layout = QVBoxLayout(right_side)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.right_panel = RightPanel()
        right_layout.addWidget(self.right_panel)

        # Achievement progress
        ach_group = QGroupBox("🏅 Achievements")
        ach_layout = QVBoxLayout(ach_group)
        self.ach_label = QLabel()
        self.ach_label.setStyleSheet("QLabel { background-color: #0d0d1a; color: #FFD700; font-family: 'Consolas', 'Monaco', monospace; font-size: 10px; padding: 8px; border-radius: 4px; border: 1px solid #333; }")
        self.ach_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.ach_label.setWordWrap(True)
        self.update_achievements_display()
        ach_layout.addWidget(self.ach_label)
        right_layout.addWidget(ach_group)
        
        layout.addWidget(right_side)

        # Connect signals
        self.right_panel.battle_started.connect(self.start_battle)
        self.right_panel.battle_reset.connect(self.reset_battle)
        self.right_panel.screenshot_requested.connect(self.save_screenshot)
        self.right_panel.settings_changed.connect(self.apply_settings)
        self.right_panel.export_requested.connect(self.export_video)
        self.right_panel.pause_toggled.connect(self.toggle_pause)
        self.right_panel.next_battle_requested.connect(self.auto_next_battle)
        self.right_panel.canvas_changed.connect(self.arena.apply_canvas_mode)
        self.right_panel.safe_zone_toggled.connect(lambda x: setattr(self.arena, 'show_safe_zones', x))
        self.right_panel.difficulty_changed.connect(self.set_difficulty)
        self.right_panel.tournament_started.connect(self.start_tournament)

        self.arena.battle_log_updated.connect(self.on_log_updated)
        self.arena.battle_ended.connect(self.on_battle_ended)
        self.arena.request_next_battle.connect(self.auto_next_battle)
        self.arena.stats_updated.connect(self.update_stats_display)
        self.arena.achievement_unlocked.connect(self.on_achievement_unlocked)

        self.apply_settings(self.right_panel.get_settings())
        self.right_panel.emit_canvas_change()

        # Shortcuts
        QShortcut(QKeySequence("Space"), self, activated=self.right_panel.emit_start)
        QShortcut(QKeySequence("P"), self, activated=self.toggle_pause)
        QShortcut(QKeySequence("R"), self, activated=self.reset_battle)
        QShortcut(QKeySequence("S"), self, activated=self.save_screenshot)
        QShortcut(QKeySequence("N"), self, activated=self.right_panel.randomize)

    def apply_settings(self, settings: dict):
        self.arena.auto_queue = settings.get("auto_queue", False)
        self.arena.speed_multiplier = settings.get("speed", 1.0)
        self.arena.watermark_text = settings.get("watermark", "")

    def set_difficulty(self, diff: AIDifficulty):
        self.arena.ai_difficulty = diff

    def toggle_pause(self):
        if self.arena.phase == BattlePhase.PAUSED: self.arena.resume()
        else: self.arena.pause()

    def start_battle(self, w1, c1, w2, c2, arena_name):
        self.log_lines.clear()
        self.right_panel.log_display.setText("Battle starting...")
        self.arena.setup_battle(w1, c1, w2, c2, arena_name)

    def start_tournament(self, participants: list, classes: dict):
        self.arena.tournament.start_tournament(participants, classes)
        match = self.arena.tournament.get_current_match()
        if match:
            self.start_battle(match.w1, match.c1, match.w2, match.c2, self.right_panel.arena_combo.currentText())
            QMessageBox.information(self, "Tournament Started", f"8-warrior tournament begins!\nFirst match: {match.w1} vs {match.w2}")

    def auto_next_battle(self):
        self.right_panel.randomize()
        self.start_battle(
            self.right_panel.w1_combo.currentText(), self.right_panel.c1_combo.currentText(),
            self.right_panel.w2_combo.currentText(), self.right_panel.c2_combo.currentText(),
            self.right_panel.arena_combo.currentText()
        )
        self.right_panel.tourney_list.setText(self.arena.tournament.get_bracket_text())

    def reset_battle(self):
        self.arena.reset()
        self.log_lines.clear()
        self.right_panel.log_display.setText("Arena reset. Select warriors and start!")
        self.right_panel.stats_label.setText("Start a battle to see stats...")

    def on_log_updated(self, text):
        self.log_lines.append(text)
        self.log_lines = self.log_lines[-20:]
        self.right_panel.log_display.setText("\n".join(self.log_lines))

    def on_battle_ended(self, winner, loser):
        self.arena.history.record_battle(winner, loser)
        if self.arena.tournament.active:
            self.arena.tournament.record_result(winner, loser)
            self.right_panel.tourney_list.setText(self.arena.tournament.get_bracket_text())
            if self.arena.tournament.state.champion:
                QMessageBox.information(self, "🏆 Tournament Champion!", 
                    f"{self.arena.tournament.state.champion} is the CHAMPION!")
        self.update_achievements_display()

    def on_achievement_unlocked(self, aid: str, name: str, emoji: str):
        QMessageBox.information(self, "🏅 Achievement Unlocked!", f"{emoji} {name}\n\nID: {aid}")
        self.update_achievements_display()

    def update_achievements_display(self):
        unlocked, total = self.arena.achievements.get_progress()
        text = f"Progress: {unlocked}/{total}\n\n"
        for aid, adata in ACHIEVEMENTS_DB.items():
            mark = "✅" if aid in self.arena.achievements.unlocked else "❌"
            text += f"{mark} {adata['emoji']} {adata['name']}\n"
        self.right_panel.ach_label.setText(text)

    def update_stats_display(self):
        if not self.arena.warrior1 or not self.arena.warrior2: return
        w1, w2 = self.arena.warrior1, self.arena.warrior2
        def fmt(w, name):
            dmg_breakdown = ""
            if w.stats.damage_by_type:
                parts = [f"{dt.value[0]}:{d}" for dt, d in w.stats.damage_by_type.items()]
                dmg_breakdown = "\n  DmgTypes: " + ", ".join(parts)
            return (f"{w.emoji} {name}:\n"
                    f"  DMG Dealt: {w.stats.damage_dealt}\n"
                    f"  DMG Taken: {w.stats.damage_taken}\n"
                    f"  Max Combo: {w.stats.max_combo}\n"
                    f"  Crits: {w.stats.crits} | Blocks: {w.stats.blocks} | Dodges: {w.stats.dodges}\n"
                    f"  Specials: {w.stats.specials_used} | Heals: {w.stats.heals_used}\n"
                    f"  Pickups: {w.stats.pickups_collected}{dmg_breakdown}")
        text = fmt(w1, "Fighter 1") + "\n\n" + fmt(w2, "Fighter 2")
        self.right_panel.stats_label.setText(text)

    def save_screenshot(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Screenshot", f"battle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png", "PNG Images (*.png)")
        if filename:
            self.arena.capture_screenshot(filename, scale=2.0)
            QMessageBox.information(self, "Saved", f"Screenshot saved to:\n{filename}")

    def export_video(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory for Video")
        if dir_path:
            export_scale = self.right_panel.quality_combo.currentData()
            VideoExporter.export_battle(
                self.right_panel.w1_combo.currentText(), self.right_panel.c1_combo.currentText(),
                self.right_panel.w2_combo.currentText(), self.right_panel.c2_combo.currentText(),
                self.right_panel.arena_combo.currentText(), dir_path, self.arena.canvas_mode, export_scale, self
            )

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("AI Battle Arena V20")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()