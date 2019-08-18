import pygame
import random


class mapTile(pygame.sprite.Sprite):
    'individual tile object that constitute the map'

    def __init__(self, sign, x, y, gtimer):
        super().__init__()
        # tile width/height in px
        TILE_SIZE = 16
        # tile type
        self.sign = sign

        SPRITES = pygame.transform.scale(pygame.image.load(
            "/Users/Jeff/Documents/pygame/mytank/images/sprites.gif"), [192, 224])

        self.tile_empty = pygame.Surface((8 * 2, 8 * 2))
        self.tile_brick = SPRITES.subsurface(48 * 2, 64 * 2, 8 * 2, 8 * 2)
        self.tile_steel = SPRITES.subsurface(48 * 2, 72 * 2, 8 * 2, 8 * 2)
        self.tile_grass = SPRITES.subsurface(56 * 2, 72 * 2, 8 * 2, 8 * 2)
        self.tile_water = SPRITES.subsurface(64 * 2, 64 * 2, 8 * 2, 8 * 2)
        self.tile_water1 = SPRITES.subsurface(64 * 2, 64 * 2, 8 * 2, 8 * 2)
        self.tile_water2 = SPRITES.subsurface(72 * 2, 64 * 2, 8 * 2, 8 * 2)
        self.tile_froze = SPRITES.subsurface(64 * 2, 72 * 2, 8 * 2, 8 * 2)

        TILE_dic = {
            '#': self.tile_brick,
            '@': self.tile_steel,
            '~': self.tile_water,
            '%': self.tile_grass,
            '-': self.tile_froze
        }

        self.image = TILE_dic[self.sign]
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

        gtimer.add(400, lambda: self.toggleWaves())

    def toggleWaves(self):
        # toggle water tile
        if self.sign == '~':
            if self.image == self.tile_water1:
                self.image = self.tile_water2
            else:
                self.image = self.tile_water1


class Castle(pygame.sprite.Sprite):
    'players castle/fortress object'

    def __init__(self):
        super().__init__()

        # three state of the Castle
        (self.STATE_STANDING, self.STATE_DESTROYED, self.STATE_EXPLODING) = range(3)

        SPRITES = pygame.transform.scale(pygame.image.load(
            "/Users/Jeff/Documents/pygame/mytank/images/sprites.gif"), [192, 224])

        # images
        self.img_undamaged = SPRITES.subsurface(0, 15 * 2, 16 * 2, 16 * 2)
        self.img_destroyed = SPRITES.subsurface(16 * 2, 15 * 2, 16 * 2, 16 * 2)

        # init position
        self.rect = pygame.Rect(12 * 16, 24 * 16, 32, 32)

        self.rebuild()

    def rebuild(self):
        # start w/ undamaged and shiny castle
        """ Reset castle """
        self.state = self.STATE_STANDING
        self.image = self.img_undamaged

    def destroy(self, gtimer):
        """ Destroy castle """
        self.state = self.STATE_EXPLODING
        self.explosion = Explosion(self.rect.topleft, gtimer)

    def update(self):
        if self.state == self.STATE_EXPLODING:
            if not self.explosion.active:
                self.state = self.STATE_DESTROYED
                del self.explosion
                self.image = self.img_destroyed
                self.rect = pygame.Rect(12 * 16, 24 * 16, 32, 32)
            else:
                self.image = self.explosion.image
                self.rect = pygame.Rect(
                    self.explosion.position[0], self.explosion.position[1], 32 * 2, 32 * 2)


class Explosion():
    def __init__(self, position, gtimer, interval=None, images=None):

        self.position = [position[0] - 16, position[1] - 16]

        self.active = True

        SPRITES = pygame.transform.scale(pygame.image.load(
            "/Users/Jeff/Documents/pygame/mytank/images/sprites.gif"), [192, 224])

        if interval == None:
            interval = 100

        if images == None:
            images = [
                SPRITES.subsurface(0, 80 * 2, 32 * 2, 32 * 2),
                SPRITES.subsurface(32 * 2, 80 * 2, 32 * 2, 32 * 2),
                SPRITES.subsurface(64 * 2, 80 * 2, 32 * 2, 32 * 2)
            ]

        images.reverse()

        self.images = [] + images

        self.image = self.images.pop()

        gtimer.add(interval, lambda: self.update(), len(self.images) + 1)

    def update(self):
        """ Advace to the next image """
        if len(self.images) > 0:
            self.image = self.images.pop()
        else:
            self.active = False


class playerTank(pygame.sprite.Sprite):
    def __init__(self, gtimer):

        super().__init__()

        '------------------general tank variables-----------------------'

        SPRITES = pygame.transform.scale(pygame.image.load(
            "/Users/Jeff/Documents/pygame/mytank/images/sprites.gif"), [192, 224])

        # states
        (self.STATE_SPAWNING, self.STATE_DEAD,
         self.STATE_ALIVE, self.STATE_EXPLODING) = range(4)
        # list all possible direction
        (self.DIR_UP, self.DIR_RIGHT, self.DIR_DOWN, self.DIR_LEFT) = range(4)
        # player life
        self.lives = 1
        # px per move
        self.speed = 4
        # image when spawning
        self.spawn_images = [
            SPRITES.subsurface(32 * 2, 48 * 2, 16 * 2, 16 * 2),
            SPRITES.subsurface(48 * 2, 48 * 2, 16 * 2, 16 * 2)
        ]
        self.spawn_index = 0
        self.spawn_image = self.spawn_images[0]

        self.state = self.STATE_SPAWNING
        self.gtimer = gtimer
        # spawning animation
        self.timer_uuid_spawn = self.gtimer.add(
            100, lambda: self.toggleSpawnImage())

        # duration of spawning
        self.timer_uuid_spawn_end = self.gtimer.add(
            1000, lambda: self.endSpawning())

        self.bulletGroup = pygame.sprite.Group()

        '---------------player variable------------------'
        self.player_image = SPRITES.subsurface(
            (0, 0, 16 * 2 - 4.5, 16 * 2 - 4.5))

        self.rect = self.player_image.get_rect()
        self.direction = self.DIR_UP
        self.image_up = self.player_image
        self.image_left = pygame.transform.rotate(self.player_image, 90)
        self.image_down = pygame.transform.rotate(self.player_image, 180)
        self.image_right = pygame.transform.rotate(self.player_image, 270)

    def toggleSpawnImage(self):
        """ advance to the next spawn image """
        if self.state != self.STATE_SPAWNING:
            self.gtimer.destroy(self.timer_uuid_spawn)
            return
        self.spawn_index += 1
        if self.spawn_index >= len(self.spawn_images):
            self.spawn_index = 0
        self.spawn_image = self.spawn_images[self.spawn_index]

    def endSpawning(self):
        """ End spawning
        Player becomes operational
        """
        self.state = self.STATE_ALIVE
        self.gtimer.destroy(self.timer_uuid_spawn_end)

    def move(self, obstacle_rects):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.direction = self.DIR_UP
            new_position = [self.rect.left, self.rect.top - self.speed]
            if new_position[1] < 0:
                return
        elif keys[pygame.K_RIGHT]:
            self.direction = self.DIR_RIGHT
            new_position = [self.rect.left + self.speed, self.rect.top]
            if new_position[0] > (416 - 26):
                return
        elif keys[pygame.K_DOWN]:
            self.direction = self.DIR_DOWN
            new_position = [self.rect.left, self.rect.top + self.speed]
            if new_position[1] > (416 - 26):
                return
        elif keys[pygame.K_LEFT]:
            self.direction = self.DIR_LEFT
            new_position = [self.rect.left - self.speed, self.rect.top]
            if new_position[0] < 0:
                return

        if (keys[pygame.K_UP] | keys[pygame.K_RIGHT] | keys[pygame.K_DOWN] | keys[pygame.K_LEFT]):
            # check if collide with obstacle. if collide do not update rect position
            temp_rect = self.rect.copy()
            temp_rect.topleft = (new_position[0], new_position[1])
            if temp_rect.collidelist(obstacle_rects) != -1:
                return
            self.rect.topleft = (new_position[0], new_position[1])

    def update(self, obstacle_rects):
        if self.state == self.STATE_SPAWNING:
            self.image = self.spawn_image
        elif self.state == self.STATE_ALIVE:
            self.move(obstacle_rects)
            if self.direction == self.DIR_UP:
                self.image = self.image_up
            elif self.direction == self.DIR_RIGHT:
                self.image = self.image_right
            elif self.direction == self.DIR_DOWN:
                self.image = self.image_down
            elif self.direction == self.DIR_LEFT:
                self.image = self.image_left
        elif self.state == self.STATE_EXPLODING:
            if not self.explosion.active:
                self.state = self.STATE_DEAD

                del self.explosion

                if self.direction == self.DIR_UP:
                    self.image = self.image_up
                elif self.direction == self.DIR_RIGHT:
                    self.image = self.image_right
                elif self.direction == self.DIR_DOWN:
                    self.image = self.image_down
                elif self.direction == self.DIR_LEFT:
                    self.image = self.image_left

                self.rect = pygame.Rect(
                    self.topleft_before_explosion, [16 * 2 - 4.5, 16 * 2 - 4.5])
            else:
                self.image = self.explosion.image
                self.rect = pygame.Rect(
                    self.explosion.position[0], self.explosion.position[1], 32 * 2, 32 * 2)

    def getHit(self, gtimer):
        # player get hit and explode
        self.state = self.STATE_EXPLODING
        self.topleft_before_explosion = self.rect.topleft
        self.explosion = Explosion(self.rect.topleft, gtimer)

    def on_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.fire()

    def fire(self):
        self.bulletGroup.add(Bullet(self.rect.topleft, self.direction))


class enemyTank(pygame.sprite.Sprite):
    def __init__(self, gtimer, type, obstacle_rects):

        super().__init__()

        '------------------general tank variables-----------------------'

        SPRITES = pygame.transform.scale(pygame.image.load(
            "/Users/Jeff/Documents/pygame/mytank/images/sprites.gif"), [192, 224])

        # states
        (self.STATE_SPAWNING, self.STATE_DEAD,
         self.STATE_ALIVE, self.STATE_EXPLODING) = range(4)
        # list all possible direction
        (self.DIR_UP, self.DIR_RIGHT, self.DIR_DOWN, self.DIR_LEFT) = range(4)

        # image when spawning
        self.spawn_images = [
            SPRITES.subsurface(32 * 2, 48 * 2, 16 * 2, 16 * 2),
            SPRITES.subsurface(48 * 2, 48 * 2, 16 * 2, 16 * 2)
        ]
        self.spawn_index = 0
        self.spawn_image = self.spawn_images[0]

        self.state = self.STATE_SPAWNING
        self.gtimer = gtimer
        # spawning animation
        self.timer_uuid_spawn = self.gtimer.add(
            100, lambda: self.toggleSpawnImage())

        # duration of spawning
        self.timer_uuid_spawn_end = self.gtimer.add(
            1000, lambda: self.endSpawning())

        self.bulletGroup = pygame.sprite.Group()

        '---------------enemy variable------------------'

        (self.TYPE_BASIC, self.TYPE_FAST, self.TYPE_POWER, self.TYPE_ARMOR) = range(4)

        images = [
            SPRITES.subsurface(32 * 2, 0, 13 * 2, 15 * 2),
            SPRITES.subsurface(48 * 2, 0, 13 * 2, 15 * 2),
            SPRITES.subsurface(64 * 2, 0, 13 * 2, 15 * 2),
            SPRITES.subsurface(80 * 2, 0, 13 * 2, 15 * 2),
            SPRITES.subsurface(32 * 2, 16 * 2, 13 * 2, 15 * 2),
            SPRITES.subsurface(48 * 2, 16 * 2, 13 * 2, 15 * 2),
            SPRITES.subsurface(64 * 2, 16 * 2, 13 * 2, 15 * 2),
            SPRITES.subsurface(80 * 2, 16 * 2, 13 * 2, 15 * 2)
        ]

        self.type = type

        if self.type % 4 == self.TYPE_BASIC:
            self.speed = 1
            self.health = 100
        elif self.type % 4 == self.TYPE_FAST:
            self.speed = 3
            self.health = 100
        elif self.type % 4 == self.TYPE_POWER:
            self.speed = 1
            self.health = 100
        elif self.type % 4 == self.TYPE_ARMOR:
            self.speed = 1
            self.health = 400

        self.enemy_image = images[self.type + 0]

        self.rect = self.enemy_image.get_rect()
        self.direction = random.choice(
            (self.DIR_UP, self.DIR_RIGHT, self.DIR_DOWN, self.DIR_LEFT))
        self.image_up = self.enemy_image
        self.image_left = pygame.transform.rotate(self.enemy_image, 90)
        self.image_down = pygame.transform.rotate(self.enemy_image, 180)
        self.image_right = pygame.transform.rotate(self.enemy_image, 270)

        self.rect.topleft = self.getSpawningPosition(obstacle_rects)

        # 1000 is duration between shots
        self.timer_uuid_fire = gtimer.add(1000, lambda: self.fire())

    def toggleSpawnImage(self):
        """ advance to the next spawn image """
        if self.state != self.STATE_SPAWNING:
            self.gtimer.destroy(self.timer_uuid_spawn)
            return
        self.spawn_index += 1
        if self.spawn_index >= len(self.spawn_images):
            self.spawn_index = 0
        self.spawn_image = self.spawn_images[self.spawn_index]

    def endSpawning(self):
        """ End spawning
        Player becomes operational
        """
        self.state = self.STATE_ALIVE
        self.gtimer.destroy(self.timer_uuid_spawn_end)

    def getSpawningPosition(self, obstacle_rects):
        # map tile size
        TILE_SIZE = 16
        # default initial spawning position choice
        available_positions = [
            [(TILE_SIZE * 2 - self.rect.width) / 2,
             (TILE_SIZE * 2 - self.rect.height) / 2],
            [12 * TILE_SIZE + (TILE_SIZE * 2 - self.rect.width) / 2,
             (TILE_SIZE * 2 - self.rect.height) / 2],
            [24 * TILE_SIZE + (TILE_SIZE * 2 - self.rect.width) / 2,
             (TILE_SIZE * 2 - self.rect.height) / 2]
        ]
        random.shuffle(available_positions)

        for pos in available_positions:
            enemy_temp_rect = pygame.Rect(
                pos, [self.rect.width, self.rect.height])
            if enemy_temp_rect.collidelist(obstacle_rects) == -1:
                return pos

    def move(self, obstacle_rects):
        if self.direction == self.DIR_UP:
            new_position = [self.rect.left, self.rect.top - self.speed]
            if new_position[1] < 0:
                all_directions = list(range(4))
                all_directions.remove(self.direction)
                self.direction = random.choice(all_directions)
                return
        elif self.direction == self.DIR_RIGHT:
            new_position = [self.rect.left + self.speed, self.rect.top]
            if new_position[0] > (416 - 26):
                all_directions = list(range(4))
                all_directions.remove(self.direction)
                self.direction = random.choice(all_directions)
                return
        elif self.direction == self.DIR_DOWN:
            new_position = [self.rect.left, self.rect.top + self.speed]
            if new_position[1] > (416 - 26):
                all_directions = list(range(4))
                all_directions.remove(self.direction)
                self.direction = random.choice(all_directions)
                return
        elif self.direction == self.DIR_LEFT:
            new_position = [self.rect.left - self.speed, self.rect.top]
            if new_position[0] < 0:
                all_directions = list(range(4))
                all_directions.remove(self.direction)
                self.direction = random.choice(all_directions)
                return

        temp_rect = self.rect.copy()
        temp_rect.topleft = (new_position[0], new_position[1])

        if temp_rect.collidelist(obstacle_rects) != -1:
            all_directions = list(range(4))
            all_directions.remove(self.direction)
            self.direction = random.choice(all_directions)
            return

        self.rect.topleft = (new_position[0], new_position[1])

    def update(self, obstacle_rects):
        if self.state == self.STATE_SPAWNING:
            self.image = self.spawn_image
        elif self.state == self.STATE_ALIVE:
            self.move(obstacle_rects)
            if self.direction == self.DIR_UP:
                self.image = self.image_up
            elif self.direction == self.DIR_RIGHT:
                self.image = self.image_right
            elif self.direction == self.DIR_DOWN:
                self.image = self.image_down
            elif self.direction == self.DIR_LEFT:
                self.image = self.image_left

    def fire(self):
        self.bulletGroup.add(Bullet(self.rect.topleft, self.direction))


class Bullet(pygame.sprite.Sprite):

    # bullet's stated

    def __init__(self, position, direction, speed=5):

        super().__init__()

        (self.DIR_UP, self.DIR_RIGHT, self.DIR_DOWN, self.DIR_LEFT) = range(4)
        (self.STATE_REMOVED, self.STATE_ACTIVE, self.STATE_EXPLODING) = range(3)

        SPRITES = pygame.transform.scale(pygame.image.load(
            "/Users/Jeff/Documents/pygame/mytank/images/sprites.gif"), [192, 224])

        self.direction = direction

        self.image = SPRITES.subsurface(75 * 2, 74 * 2, 3 * 2, 4 * 2)

        # image to pass into explosion object. when bullet hit something
        self.explosion_images = [
            SPRITES.subsurface(0, 80 * 2, 32 * 2, 32 * 2),
            SPRITES.subsurface(32 * 2, 80 * 2, 32 * 2, 32 * 2)
        ]

        # position is player's top left corner, so we'll need to
        # recalculate a bit. also rotate image itself.
        if direction == self.DIR_UP:
            self.rect = pygame.Rect(position[0] + 11, position[1] - 8, 6, 8)
        elif direction == self.DIR_RIGHT:
            self.image = pygame.transform.rotate(self.image, 270)
            self.rect = pygame.Rect(position[0] + 26, position[1] + 11, 8, 6)
        elif direction == self.DIR_DOWN:
            self.image = pygame.transform.rotate(self.image, 180)
            self.rect = pygame.Rect(position[0] + 11, position[1] + 26, 6, 8)
        elif direction == self.DIR_LEFT:
            self.image = pygame.transform.rotate(self.image, 90)
            self.rect = pygame.Rect(position[0] - 8, position[1] + 11, 8, 6)

        self.speed = speed

        self.state = self.STATE_ACTIVE

    def update(self, gtimer):

        if self.state == self.STATE_EXPLODING:
            if not self.explosion.active:
                self.destroy()
                del self.explosion
            else:
                self.image = self.explosion.image
                self.rect = pygame.Rect(
                    self.explosion.position[0], self.explosion.position[1], 32 * 2, 32 * 2)

        elif self.state == self.STATE_REMOVED:
            self.kill()

        elif self.state == self.STATE_ACTIVE:
            """ move bullet """
            if self.direction == self.DIR_UP:
                self.rect.topleft = [self.rect.left,
                                     self.rect.top - self.speed]
                if self.rect.top < 0:
                    self.explode(gtimer)
                    return
            elif self.direction == self.DIR_RIGHT:
                self.rect.topleft = [
                    self.rect.left + self.speed, self.rect.top]
                if self.rect.left > (416 - self.rect.width):
                    self.explode(gtimer)
                    return
            elif self.direction == self.DIR_DOWN:
                self.rect.topleft = [self.rect.left,
                                     self.rect.top + self.speed]
                if self.rect.top > (416 - self.rect.height):
                    self.explode(gtimer)
                    return
            elif self.direction == self.DIR_LEFT:
                self.rect.topleft = [
                    self.rect.left - self.speed, self.rect.top]
                if self.rect.left < 0:
                    self.explode(gtimer)
                    return

    def explode(self, gtimer):
        """ start bullets's explosion """
        if self.state != self.STATE_REMOVED:
            self.state = self.STATE_EXPLODING
            self.explosion = Explosion(
                [self.rect.left - 13, self.rect.top - 13], gtimer, None, self.explosion_images)

    def destroy(self):
        self.state = self.STATE_REMOVED
