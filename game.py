from sprites import *
import pygame
import pandas as pd
import uuid


class Game():
    def __init__(self):
        pygame.init()
        size = width, height = 480, 416
        self._display_surf = pygame.display.set_mode(size)
        self._FpsClock = pygame.time.Clock()
        self._running = True  # game running status
        self._playing = True  # game playing status
        self._newLevel = True  # whether it's time to start a new level game
        self.font = pygame.font.Font(
            "/Users/Jeff/Documents/pygame/mytank/fonts/prstart.ttf", 16)
        self.level = 1
        # pre-render game over text
        self.im_game_over = pygame.Surface((64, 40))
        self.im_game_over.set_colorkey((0, 0, 0))
        self.im_game_over.blit(self.font.render(
            "GAME", False, (127, 64, 64)), [0, 0])
        self.im_game_over.blit(self.font.render(
            "OVER", False, (127, 64, 64)), [0, 20])
        self.game_over_y = 416 + 40

        # enemy list in each level
        self.levelsEnemy = (
            (18, 2, 0, 0), (14, 4, 0, 2), (14, 4,
                                           0, 2), (2, 5, 10, 3), (8, 5, 5, 2),
            (9, 2, 7, 2), (7, 4, 6, 3), (7, 4,
                                         7, 2), (6, 4, 7, 3), (12, 2, 4, 2),
            (5, 5, 4, 6), (0, 6, 8, 6), (0, 8,
                                         8, 4), (0, 4, 10, 6), (0, 2, 10, 8),
            (16, 2, 0, 2), (8, 2, 8, 2), (2, 8,
                                          6, 4), (4, 4, 4, 8), (2, 8, 2, 8),
            (6, 2, 8, 4), (6, 8, 2, 4), (0, 10,
                                         4, 6), (10, 4, 4, 2), (0, 8, 2, 10),
            (4, 6, 4, 6), (2, 8, 2, 8), (15, 2,
                                         2, 1), (0, 4, 10, 6), (4, 8, 4, 4),
            (3, 8, 3, 6), (6, 4, 2, 8), (4, 4,
                                         4, 8), (0, 10, 4, 6), (0, 6, 4, 10)
        )
        # side bar icon image
        SPRITES = pygame.transform.scale(pygame.image.load(
            "/Users/Jeff/Documents/pygame/mytank/images/sprites.gif"), [192, 224])

        self.enemy_life_image = SPRITES.subsurface(
            81 * 2, 57 * 2, 7 * 2, 7 * 2)
        self.player_life_image = SPRITES.subsurface(
            89 * 2, 56 * 2, 7 * 2, 8 * 2)
        self.flag_image = SPRITES.subsurface(64 * 2, 49 * 2, 16 * 2, 15 * 2)
        self.font = pygame.font.Font("fonts/prstart.ttf", 16)

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        # check space key down to fire
        self.myPlayer.on_event(event)

    def check_collision(self):
        # check collision between player bullet and map tiles
        hit = pygame.sprite.groupcollide(
            self.mapGroup, self.myPlayer.bulletGroup, False, False)
        for map, bullets in hit.items():
            if bullets[0].state == bullets[0].STATE_ACTIVE:
                if map.sign == '#':
                    self.obstacle_rects.remove(map)
                    self.mapGroup.remove(map)
                elif map.sign in ['~', '%']:
                    return
                bullets[0].explode(self.gtimer)
        # check collision between player bullet and Castle
        hit = pygame.sprite.groupcollide(
            self.myCastileGroup, self.myPlayer.bulletGroup, False, False)
        for castle, bullets in hit.items():
            if bullets[0].state == bullets[0].STATE_ACTIVE:
                castle.destroy(self.gtimer)
                bullets[0].explode(self.gtimer)
        # check collision between enemy bullet and map tiles
        for enemyTank in self.enemyGroup.sprites():
            hit = pygame.sprite.groupcollide(
                self.mapGroup, enemyTank.bulletGroup, False, False)
            for map, bullets in hit.items():
                if bullets[0].state == bullets[0].STATE_ACTIVE:
                    if map.sign == '#':
                        self.obstacle_rects.remove(map)
                        self.mapGroup.remove(map)
                    elif map.sign == '@':
                        if enemyTank.type == enemyTank.TYPE_POWER:
                            self.obstacle_rects.remove(map)
                            self.mapGroup.remove(map)
                    elif map.sign in ['~', '%']:
                        return
                    bullets[0].explode(self.gtimer)
        # check collision between enemy bullet and Castle
        for enemyTank in self.enemyGroup.sprites():
            hit = pygame.sprite.groupcollide(
                self.myCastileGroup, enemyTank.bulletGroup, False, False)
            for castle, bullets in hit.items():
                if bullets[0].state == bullets[0].STATE_ACTIVE:
                    castle.destroy(self.gtimer)
                    bullets[0].explode(self.gtimer)
        # player bullet hit enemy
        hit = pygame.sprite.groupcollide(
            self.myPlayer.bulletGroup, self.enemyGroup, False, False)
        for bullets, enemyTank in hit.items():
            if bullets.state == bullets.STATE_ACTIVE:
                if enemyTank[0].health <= 0:
                    self.enemyGroup.remove(enemyTank[0])
                    bullets.explode(self.gtimer)
                else:
                    enemyTank[0].health -= 100

        # check collision between enemy bullet and player
        for enemyTank in self.enemyGroup.sprites():
            hit = pygame.sprite.groupcollide(
                self.playerGroup, enemyTank.bulletGroup, False, False)
            for playerTank, enemyBullets in hit.items():
                if enemyBullets[0].state == enemyBullets[0].STATE_ACTIVE:
                    playerTank.getHit(self.gtimer)
                    enemyBullets[0].explode(self.gtimer)

        # check collision between enemy and player
        hit = pygame.sprite.groupcollide(
            self.playerGroup, self.enemyGroup, False, False)
        for playerTank, enemyTank in hit.items():
            if playerTank.state == playerTank.STATE_ALIVE:
                playerTank.getHit(self.gtimer)

    def on_loop(self):
        self.myCastileGroup.update()
        self.playerGroup.update(self.obstacle_rects)
        self.myPlayer.bulletGroup.update(self.gtimer)
        self.enemyGroup.update(self.obstacle_rects)
        for enemy in self.enemyGroup.sprites():
            enemy.bulletGroup.update(self.gtimer)
        self.check_collision()

    def drawSidebar(self):

        x = 416
        y = 0
        self._display_surf.fill(
            [100, 100, 100], pygame.Rect([416, 0], [64, 416]))

        xpos = x + 16
        ypos = y + 16

        # draw enemy lives
        for n in range(len(self.enemies_left) + len(self.enemyGroup.sprites())):
            self._display_surf.blit(self.enemy_life_image, [xpos, ypos])
            if n % 2 == 1:
                xpos = x + 16
                ypos += 17
            else:
                xpos += 17

        # players' lives
        if pygame.font.get_init():
            text_color = pygame.Color('black')
            for n in range(len(self.playerGroup.sprites())):
                if n == 0:
                    self._display_surf.blit(self.font.render(str(n + 1) + "P",
                                                             False, text_color), [x + 16, y + 200])
                    self._display_surf.blit(self.font.render(
                        str(self.playerGroup.sprites()[n].lives), False, text_color), [x + 31, y + 215])
                    self._display_surf.blit(
                        self.player_life_image, [x + 17, y + 215])
                else:
                    self._display_surf.blit(self.font.render(str(n + 1) + "P",
                                                             False, text_color), [x + 16, y + 240])
                    self._display_surf.blit(self.font.render(
                        str(self.playerGroup.sprites()[n].lives), False, text_color), [x + 31, y + 255])
                    self._display_surf.blit(
                        self.player_life_image, [x + 17, y + 255])

            self._display_surf.blit(self.flag_image, [x + 17, y + 280])
            self._display_surf.blit(self.font.render(str(self.level),
                                                     False, text_color), [x + 17, y + 312])

    def on_render(self):
        self._display_surf.fill((0, 0, 0))
        self.mapGroup.draw(self._display_surf)
        self.myCastileGroup.draw(self._display_surf)
        self.playerGroup.draw(self._display_surf)
        self.myPlayer.bulletGroup.draw(self._display_surf)
        self.enemyGroup.draw(self._display_surf)

        for enemy in self.enemyGroup.sprites():
            enemy.bulletGroup.draw(self._display_surf)
        # show game over text
        if not self._playing:
            if self.game_over_y > 188:
                self.game_over_y -= 4
            # 176=(416-64)/2
            self._display_surf.blit(self.im_game_over, [176, self.game_over_y])

        self.drawSidebar()

        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()

    def loadLevel(self, level, gtimer):
        # create map
        # tile width/height in px
        TILE_SIZE = 16
        map_sign_df = pd.read_fwf(
            '/Users/Jeff/Documents/pygame/mytank/levels/' + str(level), widths=[1] * 26, header=None)
        # create map group
        for r in range(map_sign_df.shape[0]):
            for c in range(map_sign_df.shape[1]):
                if map_sign_df.iloc[c, r] != '.':
                    p = mapTile(map_sign_df.iloc[c, r],
                                r * TILE_SIZE, c * TILE_SIZE, gtimer)
                    self.mapGroup.add(p)
                    if map_sign_df.iloc[c, r] in ['@', '~', '#']:
                        self.obstacle_rects.append(p)
        # create castle
        self.myCastle = Castle()
        self.myCastileGroup.add(self.myCastle)
        # reset new level status
        self._newLevel = False

    def addEnemys(self):

        if len(self.enemyGroup.sprites()) < 4 and len(self.enemies_left) > 0:
            obstacle_rects_list = self.mapGroup.sprites()
            obstacle_rects_list.append(self.myPlayer)
            self.enemyGroup.add(
                enemyTank(self.gtimer, self.enemies_left.pop(), obstacle_rects_list))
        if len(self.enemies_left) <= 0 and len(self.enemyGroup.sprites()) == 0:
            self._newLevel = True
            if self.level == 35:
                self.level = 1
            else:
                self.level += 1

    def checkGameOver(self):
        if self.myCastle.state == self.myCastle.STATE_DESTROYED:
            self._playing = False
        if self.myPlayer.state == self.myPlayer.STATE_DEAD:
            self._playing = False

    def on_execute(self):
        while self._running:
            time_passed = self._FpsClock.tick(40)
            if self._playing:
                if self._newLevel:
                    self.mapGroup = pygame.sprite.Group()
                    self.obstacle_rects = []  # maptile tank cannot passthrough
                    self.myCastileGroup = pygame.sprite.Group()
                    self.gtimer = Timer()
                    self.playerGroup = pygame.sprite.Group()
                    self.myPlayer = playerTank(self.gtimer)
                    self.playerGroup.add(self.myPlayer)
                    self.enemyGroup = pygame.sprite.Group()
                    self.loadLevel(self.level, self.gtimer)
                    enemies_l = self.levelsEnemy[self.level - 1]
                    self.enemies_left = [0] * enemies_l[0] + [1] * \
                        enemies_l[1] + [2] * enemies_l[2] + [3] * enemies_l[3]
                    random.shuffle(self.enemies_left)
                # add new enemy tank
                self.addEnemys()
                # handle event
                for event in pygame.event.get():
                    self.on_event(event)
                # update game data
                self.on_loop()
                # update timer
                self.gtimer.update(time_passed)
                self.checkGameOver()
                # draw to display
                self.on_render()
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self._running = False
                # game over images
                self.on_render()

        self.on_cleanup()


class Timer():
    def __init__(self):
        self.timers = []

    def add(self, interval, f, repeat=-1):
        options = {
            "interval"	: interval,
            "callback"	: f,
            "repeat"		: repeat,
            "times"			: 0,
            "time"			: 0,
            "uuid"			: uuid.uuid4()
        }
        self.timers.append(options)

        return options["uuid"]

    def destroy(self, uuid_nr):
        for timer in self.timers:
            if timer["uuid"] == uuid_nr:
                self.timers.remove(timer)
                return

    def update(self, time_passed):
        for timer in self.timers:
            timer["time"] += time_passed
            if timer["time"] > timer["interval"]:
                timer["time"] -= timer["interval"]
                timer["times"] += 1
                if timer["repeat"] > -1 and timer["times"] == timer["repeat"]:
                    self.timers.remove(timer)
                try:
                    timer["callback"]()
                except:
                    try:
                        self.timers.remove(timer)
                    except:
                        pass
