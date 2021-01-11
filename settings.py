import pygame as pg
import itertools
vec = pg.math.Vector2

# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (106, 55, 5)

# game settings
WIDTH = 1056  # 16 * 64 or 32 * 32 or 64 * 16
HEIGHT = 800  # 16 * 48 or 32 * 24 or 64 * 12
FPS = 60
TITLE = "Zombs"
BGCOLOR = BLACK
GAMEFONT = "Basic.TTF"
HUDFONT = "Basic.TTF"

TILESIZE = 64
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

WALL_IMAGE = "rpgTile052.png"

# Player Settings
PLAYER_SPEED = 250
PLAYER_ROT_SPEED = 250
PLAYER_IMAGE = "manBlue_gun.png"
PLAYER_HIT_RECT = pg.Rect(0, 0, 35, 35)
PLAYER_HEALTH = 100

# Weapon Settings
BULLET_IMAGE = "Bullet.png"
WEAPONS = {}
WEAPONS['pistol'] = {'bullet_speed': 500,
                     'bullet_lifetime': 1000,
                     'bullet_firerate': 500,
                     'barrel_offset': vec(30,10),
                     'recoil': 0,
                     'accuracy': 95,
                     'damage': 25,
                     'knockback': 100,
                     'bullet_size': 'large',
                     'hit_rect': pg.Rect(0, 0, 10, 10),
                     'bullet_count': 1}

WEAPONS['shotgun'] = {'bullet_speed' : 500,
                     'bullet_lifetime': 750,
                     'bullet_firerate': 1000,
                     'barrel_offset': vec(30,10),
                     'recoil': 0,
                     'accuracy': 80,
                     'damage': 8,
                     'knockback': 25,
                     'bullet_size': 'small',
                     'hit_rect': pg.Rect(0, 0, 7, 7),
                     'bullet_count': 12}


#Mob Settings
MOB_IMAGE = "zoimbie1_hold.png"
MOB_DEATH = "zoimbie1_death.png"
MOB_SPEED = [175, 200, 225]
MOB_HIT_RECT = pg.Rect(0, 0, 30, 30)
MOB_HEALTH = 100
MOB_DAMAGE = 10
MOB_KNOCKBACK = 20
AVOID_RADIUS = 50
DETECT_RADIUS = 300

# EFFECTS
MUZZLE_FLASH = ["whitePuff15.png", "whitePuff16.png", "whitePuff17.png"]
MUZZLE_FLASH_DURATION = 50
ZOMBIE_DEATHPUFF = ["fart01.png", "fart05.png", "fart08.png"]
ZOMBIE_DEATHPUFF_DURATION = 100
DAMAGE_ALPHA = [i for i in range(0, 255, 25)]

# Layers
WALL_LAYER = 1
PLAYER_LAYER = 2
BULLET_LAYER = 3
MOB_LAYER = 2
EFFECTS_LAYER = 4
ITEM_LAYER = 1

# Items
ITEM_IMAGES = {"health":"healthpack.png",
               "shotgun": "sg2.png"}
ITEM_SIZE = 30
HEALTH_PACK_AMOUNT = 30
BOUNCE_RANGE = 15
BOUNCE_SPEED = 0.3

# Sounds
BG_MUSIC = 'Stasis.mp3'
ZOMBIE_SOUNDS = ['Zombie Sound 2.wav']
ZOMBIE_DEATH_SOUNDS = ['Zombie Sound 3.wav']
ZOMBIE_CHASE_SOUNDS = ['Zombie Sound.wav']
PLAYER_HIT_SOUNDS = ['Grunt.wav']
PLAYER_DEATH_SOUNDS = ['Death.wav']
WEAPON_SOUNDS = {'pistol': ["Pistolshot.wav"],
                           'shotgun': ["Shotgun.wav"]}
EFFECT_SOUNDS = {'health': 'Health.wav',
                 'start': 'Start1.wav',
                 'gun_pickup': 'gun_pickup.wav'}
