import pygame as pg
import sys
from settings import *
from os import path
from sprites import *
from tilemap import *

# HUD functions

def draw_player_health(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 20
    fill = pct * BAR_LENGTH
    outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
    if pct > 0.6:
        col = GREEN
    elif pct > 0.3:
        col = YELLOW
    else:
        col = RED

    pg.draw.rect(surf, col, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 2)



class Game:
    def __init__(self):
        pg.mixer.pre_init(44100, -16, 4, 2048)
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.load_data()

    def draw_text(self, text, font_name, size, color, x, y, align="nw"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x, y)
        if align == "ne":
            text_rect.topright = (x, y)
        if align == "sw":
            text_rect.bottomleft = (x, y)
        if align == "se":
            text_rect.bottomright = (x, y)
        if align == "n":
            text_rect.midtop = (x, y)
        if align == "s":
            text_rect.midbottom = (x, y)
        if align == "e":
            text_rect.midright = (x, y)
        if align == "w":
            text_rect.midleft = (x, y)
        if align == "center":
            text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def load_data(self):
        game_folder = path.dirname(__file__)
        PNG_folder = path.join(game_folder, "Artwork", "PNG")
        SOUND_folder = path.join(game_folder, "Sounds")
        MUSIC_folder = path.join(game_folder, "Music")
        FONT_folder = path.join(game_folder, "Artwork", "Fonts")
        self.map_folder = path.join(game_folder, "maps")
        blueman_folder = path.join(PNG_folder, "Man Blue")
        mob_folder = path.join(PNG_folder, "Zombie 1")
        wall_folder1 = path.join(PNG_folder, "RPG_Tiles")
        wall_folder2 = path.join(PNG_folder, "Tiles")
        effect_folder = path.join(game_folder, "Artwork", "PNG", "Effects")
        ITEMS_FOLDER = path.join(PNG_folder, "Items")

        self.title_font = path.join(FONT_folder, GAMEFONT)
        self.hud_font = path.join(FONT_folder, HUDFONT)
        self.dim = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim.fill((0, 0, 0, 180))



        self.player_img = pg.image.load(path.join(blueman_folder, PLAYER_IMAGE)).convert_alpha()
        self.mob_img = pg.image.load(path.join(mob_folder, MOB_IMAGE)).convert_alpha()
        self.mob_death = pg.image.load(path.join(mob_folder, MOB_DEATH)).convert_alpha()


        self.bullet_images = {}
        self.bullet_images['large'] = pg.image.load(path.join(wall_folder2, BULLET_IMAGE)).convert_alpha()
        self.bullet_images['small'] = pg.transform.scale(self.bullet_images['large'], (10, 10))



        self.wall_img = pg.image.load(path.join(wall_folder1, WALL_IMAGE)).convert_alpha()
        self.wall_img = pg.transform.scale(self.wall_img, (TILESIZE, TILESIZE))

        self.gun_flashes = []
        for img in MUZZLE_FLASH:
            self.gun_flashes.append(pg.image.load(path.join(effect_folder, img)).convert_alpha())
        self.zombie_puffs = []
        for img in ZOMBIE_DEATHPUFF:
            self.zombie_puffs.append(pg.image.load(path.join(effect_folder, img)).convert_alpha())

        self.item_images = {}
        for item in ITEM_IMAGES:
            self.item_images[item] = pg.image.load(path.join(ITEMS_FOLDER, ITEM_IMAGES[item])).convert_alpha()

        # sound loading
        pg.mixer.music.load(path.join(MUSIC_folder, BG_MUSIC))

        self.effects_sounds = {}
        for type in EFFECT_SOUNDS:
            self.effects_sounds[type] = pg.mixer.Sound(path.join(SOUND_folder, EFFECT_SOUNDS[type]))

        self.weapon_sounds = {}
        for weapon in WEAPON_SOUNDS:
            self.weapon_sounds[weapon] = []
            for sound in WEAPON_SOUNDS[weapon]:
                s = pg.mixer.Sound(path.join(SOUND_folder, sound))
                s.set_volume(0.3)
                self.weapon_sounds[weapon].append(s)


        self.zombie_sounds = []
        for sound in ZOMBIE_SOUNDS:
            s = pg.mixer.Sound(path.join(SOUND_folder, sound))
            s.set_volume(0.1)
            self.zombie_sounds.append(s)

        self.player_hit_sounds = []
        for sound in PLAYER_HIT_SOUNDS:
            self.player_hit_sounds.append(pg.mixer.Sound(path.join(SOUND_folder, sound)))

        self.zombie_chase_sounds = []
        for sound in ZOMBIE_CHASE_SOUNDS:
            self.zombie_chase_sounds.append(pg.mixer.Sound(path.join(SOUND_folder, sound)))

        self.zombie_death_sounds = []
        for sound in ZOMBIE_DEATH_SOUNDS:
            self.zombie_death_sounds.append(pg.mixer.Sound(path.join(SOUND_folder, sound)))

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()

        self.map = TiledMap(path.join(self.map_folder, "Testmap.tmx"))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()

        # load txt file maps
        # for row, tiles in enumerate(self.map.data):
        #     for col, tile in enumerate(tiles):
        #         if tile == "x":
        #             Wall(self, col, row)
        #         if tile == "M":
        #             Mob(self, col, row)
        #         if tile == "S":
        #             self.player = Player(self, col, row)

        # Load tiled maps
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width / 2, tile_object.y + tile_object.height / 2)
            if tile_object.name == "player":
                self.player = Player(self, obj_center.x, obj_center.y)
            if tile_object.name == "wall":
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name == "zombie":
                Mob(self, obj_center.x, obj_center.y)
            if tile_object.name in ["health", "shotgun"]:
                Item(self, obj_center, tile_object.name)


        self.camera = Camera(self.map.width, self.map.height)
        self.draw_debug = False
        self.paused = False
        self.effects_sounds['start'].set_volume(0.2)
        self.effects_sounds['start'].play()

    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        pg.mixer.music.play(loops=-1)
        pg.mixer.music.set_volume(0.05)
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            if not self.paused:
                self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # update portion of the game loop
        self.all_sprites.update()
        self.camera.update(self.player)

        #Game completed
        if len(self.mobs) == 0:
            self.playing = False

        # player hits items
        hits = pg.sprite.spritecollide(self.player, self.items, False)
        for hit in hits:
            if hit.type == "health" and self.player.health < PLAYER_HEALTH:
                hit.kill()
                self.effects_sounds['health'].play()
                self.player.add_health(HEALTH_PACK_AMOUNT)
            if hit.type == "shotgun":
                hit.kill()
                self.effects_sounds['gun_pickup'].play()
                self.player.weapon = 'shotgun'

        # Mobs hit player
        hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect_to_rect)
        for hit in hits:
            current_hit = pg.time.get_ticks()
            if current_hit > self.player.last_hit + 250:
                choice(self.player_hit_sounds).play()
                self.player.last_hit = current_hit
                self.player.health -= MOB_DAMAGE
                hit.vel = vec (0, 0)
            if self.player.health <= 0:
                self.playing = False

            if hits:
                self.player.hit()
                self.player.pos += vec(MOB_KNOCKBACK, 0).rotate(-hits[0].rot)

        # bullets hit mobs
        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True, collide_hit_rects)
        for mob in hits:
            # hit.health -= WEAPONS[self.player.weapon]['damage'] * len(hits[hit])
            for bullet in hits[mob]:
                mob.health -= bullet.damage
                mob.vel = vec((WEAPONS[self.player.weapon]['knockback'] * len(hits[mob])), 0).rotate(-self.player.rot)


    # Draws a grid on the screen when called to display tilesize with grey lines
    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def draw(self):
        # Draw the map
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))

        # Draw the sprites
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                sprite.draw_health()
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            if self.draw_debug:
                pg.draw.rect(self.screen, GREEN, self.camera.apply_rect(sprite.hit_rect), 1)
        if self.draw_debug:
            for wall in self.walls:
                pg.draw.rect(self.screen, GREEN, self.camera.apply_rect(wall.rect), 1)
            for mob in self.mobs:
                self.draw_text(str(mob.acc), self.title_font, 20 , RED, mob.pos.x, mob.pos.y, align="center")

        # Check the FPS of the game
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))

        # Displays a grid with the tile-sizes
        # self.draw_grid()

        # Check rect of player
        # pg.draw.rect(self.screen, WHITE, self.player.hit_rect, 2)

        # HUD Drawing
        draw_player_health(self.screen, 10, 10, self.player.health / PLAYER_HEALTH)
        self.draw_text('Zombies: {}'.format(len(self.mobs)), self.hud_font, 30, WHITE, WIDTH - 10, 10, align="ne")
        if self.paused:
            self.screen.blit(self.dim, (0, 0))
            self.draw_text("Paused", self.title_font, 105, RED, WIDTH / 2, HEIGHT / 2, align="center")
        # Command to display all the drawn parts, almost always comes last
        pg.display.flip()

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_h:
                    self.draw_debug = not self.draw_debug
                if event.key == pg.K_p:
                    self.paused = not self.paused



    def show_start_screen(self):
        self.screen.fill(BLACK)
        self.draw_text("Zombie Game Thingy", self.title_font, 100, RED, WIDTH / 2, HEIGHT / 2, align="center")
        self.draw_text("Press any key to start", self.title_font, 75, WHITE, WIDTH / 2, HEIGHT * 3 / 4,
                       align="center")

        pg.display.flip()
        self.wait_for_key()

    def show_go_screen(self):
        self.screen.fill(BLACK)
        self.draw_text("GAME OVER", self.title_font, 100, RED, WIDTH / 2, HEIGHT / 2, align="center")
        self.draw_text("Press a key to start again", self.title_font, 75, WHITE, WIDTH / 2, HEIGHT * 3/4, align="center")

        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        pg.event.wait()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP:
                    waiting = False

# create the game object
g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()
    g.show_go_screen()