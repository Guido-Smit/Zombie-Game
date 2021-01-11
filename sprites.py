import pygame as pg
from settings import *
from random import uniform, choice, randint, random
from tilemap import collide_hit_rect_to_rect, collide_hit_rects
from itertools import chain
import pytweening as tween
vec = pg.math.Vector2


def collide_with_walls(sprite, group, dir):
    if dir == "x":
        x_hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect_to_rect)
        if x_hits:
            if x_hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = x_hits[0].rect.left - sprite.hit_rect.width / 2
            if x_hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = x_hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == "y":
        y_hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect_to_rect)
        if y_hits:
            if y_hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = y_hits[0].rect.top - sprite.hit_rect.height / 2
            if y_hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = y_hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.rot = 0
        self.last_shot = 0
        self.last_hit = 0
        self.health = PLAYER_HEALTH
        self.weapon = 'pistol'
        self.damaged = False


    def get_keys(self):
        self.rot_speed = 0
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.rot_speed = PLAYER_ROT_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rot_speed = -PLAYER_ROT_SPEED
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rot)
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel = vec(-PLAYER_SPEED / 2, 0).rotate(-self.rot)
        if keys[pg.K_RETURN]:
            self.shoot()

    def shoot(self):
        now = pg.time.get_ticks()
        if now - self.last_shot > WEAPONS[self.weapon]['bullet_firerate']:
            self.last_shot = now
            dir = vec(1, 0).rotate(-self.rot)
            pos = self.pos + WEAPONS[self.weapon]['barrel_offset'].rotate(-self.rot)
            self.vel = vec(-(WEAPONS[self.weapon]['recoil']), 0).rotate(-self.rot)
            for i in range(WEAPONS[self.weapon]['bullet_count']):
                spread = uniform(-(100 - WEAPONS[self.weapon]['accuracy']), (100 - WEAPONS[self.weapon]['accuracy']))
                Bullet(self.game, pos, dir.rotate(spread), WEAPONS[self.weapon]['damage'])
                sound = choice(self.game.weapon_sounds[self.weapon])
                if sound.get_num_channels() > 2:
                    sound.stop()
                sound.play()
            Muzzleflash(self.game, pos)

    def hit(self):
        self.damaged = True
        self.damage_alpha = chain(DAMAGE_ALPHA * 3)

    def update(self):
        self.get_keys()
        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
        self.image = pg.transform.rotate(self.game.player_img, self.rot)
        if self.damaged:
            try:
                self.image.fill((255, 255, 255, next(self.damage_alpha)), special_flags=pg.BLEND_RGBA_MULT)
            except:
                self.damaged = False
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, "x")
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, "y")
        self.rect.center = self.hit_rect.center

    def add_health(self, amount):
        self.health += amount
        if self.health > PLAYER_HEALTH:
            self.health = PLAYER_HEALTH

class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir, damage):
        self._layer = BULLET_LAYER
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.bullet_images[WEAPONS[game.player.weapon]['bullet_size']]
        self.rect = self.image.get_rect()
        self.hit_rect = WEAPONS[game.player.weapon]['hit_rect'].copy()
        self.hit_rect.center = self.rect.center
        self.pos = vec(pos)
        self.rect.center = pos
        # spread = uniform(-(100-ACCURACY), (100-ACCURACY))
        self.vel = dir * WEAPONS[game.player.weapon]['bullet_speed']
        if game.player.weapon == 'shotgun':
            self.vel = self.vel * uniform(0.9, 1.1)
        self.spawn_time = pg.time.get_ticks()
        self.damage = damage

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        self.hit_rect.center = self.rect.center
        if pg.sprite.spritecollideany(self, self.game.walls, collide_hit_rect_to_rect):
            self.kill()
        if pg.time.get_ticks() - self.spawn_time > WEAPONS[self.game.player.weapon]['bullet_lifetime']:
            self.kill()


class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mob_img.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = MOB_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.rot = 0
        self.health = MOB_HEALTH
        self.chasing = False
        self.spotted = False
        self.waittime = 0
        self.speed = choice(MOB_SPEED)
        self.target = game.player
        self.target_dist = 0

    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < AVOID_RADIUS:
                    self.acc += dist.normalize()

    def update(self):
        self.target_dist = self.target.pos - self.pos
        if self.target_dist.length_squared() < DETECT_RADIUS**2:
            self.chase()
            self.chasing = True
        else:
            self.chasing = False
            self.spotted = False
            self.image = pg.transform.rotate(self.game.mob_img, self.rot)

            self.acc = vec(0, 0).rotate(-self.rot)
            self.rect = self.image.get_rect()
            self.rect.center = self.pos

            self.avoid_mobs()
            self.acc += self.vel * -1
            self.vel += self.acc * self.game.dt
            if -5 < self.vel[0] < 5:
                self.vel = vec(0, 0)
            self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
            self.hit_rect.centerx = self.pos.x
            collide_with_walls(self, self.game.walls, "x")
            self.hit_rect.centery = self.pos.y
            collide_with_walls(self, self.game.walls, "y")
            self.rect.center = self.hit_rect.center


            if self.waittime > 0:
                self.waittime -= (60/FPS) * 17
                if self.waittime < 0:
                    self.waittime = 0

        if self.chasing == True and self.spotted == False and self.waittime == 0:
            choice(self.game.zombie_chase_sounds).play()
            self.spotted = True
            self.waittime = 5000

        if self.health <= 0:
            choice(self.game.zombie_death_sounds).play()
            self.kill()
            Zombiedeath(self.game, self.pos)
            self.game.map_img.blit(pg.transform.rotate(self.game.mob_death, self.rot), self.pos - vec(32,32))

    def chase(self):
        if random() < 0.0005:
            choice(self.game.zombie_sounds).play()
        self.rot = self.target_dist.angle_to(vec(1, 0))
        self.acc = vec(1, 0).rotate(-self.rot)
        self.acc.scale_to_length(self.speed)

        self.image = pg.transform.rotate(self.game.mob_img, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

        self.avoid_mobs()


        self.acc += self.vel * -1
        self.vel += self.acc * self.game.dt
        self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, "x")
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, "y")
        self.rect.center = self.hit_rect.center

    def draw_health(self):
        if self.health > 60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED

        width = int(self.rect.width * self.health / MOB_HEALTH)
        self.health_bar = pg.Rect(0, 0, width, 7)
        if self.health < MOB_HEALTH:
            pg.draw.rect(self.image, col, self.health_bar)


class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = WALL_LAYER
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.wall_img
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

class Muzzleflash(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self._layer = EFFECTS_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        size = randint(10, 30)
        self.image = pg.transform.scale(choice(game.gun_flashes), (size, size))
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = pos
        self.rect.center = pos
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        if pg.time.get_ticks() - self.spawn_time > MUZZLE_FLASH_DURATION:
            self.kill()

class Zombiedeath(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self._layer = EFFECTS_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        size = randint(40, 60)
        self.image = pg.transform.scale(choice(game.zombie_puffs), (size, size))
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = pos
        self.rect.center = pos
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        if pg.time.get_ticks() - self.spawn_time > ZOMBIE_DEATHPUFF_DURATION:
            self.kill()

class Item(pg.sprite.Sprite):
    def __init__(self, game, pos, type):
        self._layer = ITEM_LAYER
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.transform.scale(game.item_images[type], (ITEM_SIZE, ITEM_SIZE))
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.type = type
        self.pos = pos
        self.rect.center = pos
        self.tween = tween.easeInOutSine
        self.step = 0
        self.dir = 1

    def update(self):
        # Itembounce motion
        offset = BOUNCE_RANGE * (self.tween(self.step / BOUNCE_RANGE) - 0.5)
        self.rect.centery = self.pos.y + offset * self.dir
        self.step += BOUNCE_SPEED
        if self.step > BOUNCE_RANGE:
            self.step = 0
            self.dir *= -1

