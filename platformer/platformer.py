import pygame
from pygame import mixer
import pickle
from os import path

player_name = input("hello, welcome to platformer! what is your name?: ")
intro = input(
    f'welcome {player_name} you are going to play through a series of levels. each level increases with difficulty. '
    f'are you read?: ')
if intro.lower() == "yes":
    print("we wish you luck")

    pygame.mixer.pre_init(44100, -16, 2, 512)
    mixer.init()
    pygame.init()

    timer = pygame.time.Clock()
    fps = 60

    screen_breadth = 700
    screen_height = 700

    screen = pygame.display.set_mode((screen_breadth, screen_height))
    pygame.display.set_caption("platformer.py")

    # defining font
    font = pygame.font.SysFont('Bauhaus 93', 70)
    font_score = pygame.font.SysFont('Bauhaus 93', 30)

    # block variable
    block_size = 35
    game_over = 0
    main_menu = True
    level = 0
    max_levels = 7
    score = 0

    # defining colors for the font
    white = (255, 255, 255)
    blue = (0, 0, 255)

    # load images
    sun_img = pygame.image.load("sun (2).png")
    bg_img = pygame.image.load("background.png.jpg")
    restart = pygame.image.load("RestartButton.png")
    exit = pygame.image.load("ExitButton.png")
    start = pygame.image.load("PlayButton.png")

    sun_size = 50
    sky_size = 700

    sun_png = pygame.transform.scale(sun_img, (sun_size, sun_size))
    sky_png = pygame.transform.scale(bg_img, (sky_size, sky_size))
    restart_img = pygame.transform.scale(restart, (100, 50))
    start_img = pygame.transform.scale(start, (100, 100))
    exit_img = pygame.transform.scale(exit, (100, 100))


    def draw_text(text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        screen.blit(img, (x, y))


    # function to reset level
    def reset_level(level):
        global world_data
        player.restart(50, screen_height - 85)
        blob_group.empty()
        platform_group.empty()
        coin_group.empty()
        lava_group.empty()
        exit_group.empty()

        # loading pickle and world_data
        if path.exists(f'level{level}_data'):
            pickle_in = open(f'level{level}_data', 'rb')
            world_data = pickle.load(pickle_in)
        map = Map(world_data)
        # creating coin for showing score
        score_coin = Coin(block_size // 2, block_size // 2)
        coin_group.add(score_coin)
        return map


    class Reset:
        def __init__(self, x, y, image):
            self.image = image
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.click = False

        def draw_button(self):  # image of the restart button
            action = False
            # getting position of the mouse
            position = pygame.mouse.get_pos()  # getting position of the mouse on screen

            # check mouse position and clicking conditions
            if self.rect.collidepoint(position):  # if image is colliding with the mouse point
                if pygame.mouse.get_pressed()[0] == 1 and self.click == False:
                    action = True
                    self.click = True

            if pygame.mouse.get_pressed()[0] == 0:
                self.click = False

            # draw button
            screen.blit(self.image, self.rect)

            return action


    class Player:
        def __init__(self, x, y):
            self.restart(x, y)

        def pl_draw(self, game_over):
            dx = 0
            dy = 0
            walk_cooldown = 7
            col_thresh = 20

            # controls of the game
            if game_over == 0:

                key = pygame.key.get_pressed()
                if key[pygame.K_s] and self.jump == False and self.mid_air == False:
                    self.vel_y = -10.5  # gravity of pulling the player down
                    self.jump = True
                if not key[pygame.K_s]:
                    self.jump = False
                if key[pygame.K_a]:
                    dx -= 3.5  # if left key is pressed, the player moves back by 3.5 paces
                    self.counter += 1
                    self.direction = -1
                if key[pygame.K_d]:
                    dx += 3.5  # if right key is pressed, the player moves forward by 3.5 paces
                    self.counter += 1
                    self.direction = 1
                if key[pygame.K_d] == False and key[pygame.K_a] == False:
                    self.counter = 0
                    self.index = 0
                    if self.direction == 1:
                        self.image = self.images_right[self.index]
                    if self.direction == -1:
                        self.image = self.images_left[self.index]

                # walking animation
                if self.counter > walk_cooldown:
                    self.counter = 0
                    self.index += 1
                    if self.index >= len(self.images_right):
                        self.index = 0
                    if self.direction == 1:
                        self.image = self.images_right[self.index]
                    if self.direction == -1:
                        self.image = self.images_left[self.index]

                # gravity
                self.vel_y += 0.7  # how high the player will jump
                if self.vel_y > 7:
                    self.vel_y = 7
                dy += self.vel_y

                # checking for collision
                self.mid_air = True
                for block in map.block_list:
                    # check for collision in x co-ordinate
                    if block[1].colliderect(self.rect.x + dx, self.rect.y, self.breadth, self.height):
                        dx = 0
                    # collision in y co-ordinate
                    if block[1].colliderect(self.rect.x, self.rect.y + dy, self.breadth, self.height):
                        # check if you're below. ex, jumping
                        if self.vel_y < 0:
                            dy = block[1].bottom - self.rect.top
                            self.vel_y = 0
                        # check if you're above. ex, falling down
                        elif self.vel_y >= 0:
                            dy = block[1].top - self.rect.bottom
                            self.vel_y = 0
                            self.mid_air = False

                # collision with enemy
                if pygame.sprite.spritecollide(self, blob_group, False):
                    game_over = -1
                # collision with lava
                if pygame.sprite.spritecollide(self, lava_group, False):
                    game_over = -1
                # collision with gate
                if pygame.sprite.spritecollide(self, exit_group, False):
                    game_over = 1

                    # check for collision with platforms
                for platform in platform_group:
                    # collision in the x direction
                    if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.breadth, self.height):
                        dx = 0
                    # collision in the y direction
                    if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.breadth, self.height):
                        # check if below platform
                        if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                            self.vel_y = 0
                            dy = platform.rect.bottom - self.rect.top
                        # check if above platform
                        elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                            self.rect.bottom = platform.rect.top - 1
                            self.mid_air = False
                            dy = 0
                        # move sideways with the platform
                        if platform.move_x != 0:
                            self.rect.x += platform.move_direction

                # player co-ordinates
                self.rect.x += dx
                self.rect.y += dy

            elif game_over == -1:
                self.image = self.dead_image
                draw_text('GAME OVER!', font, blue, (screen_breadth // 2) - 200, screen_height // 2)
                if self.rect.y > 100:
                    self.rect.y -= 5

            # drawing the player on the screen
            screen.blit(self.image, self.rect)
            pygame.draw.rect(screen, (250, 250, 250), self.rect, 2)

            return game_over

        def restart(self, x, y):
            self.images_right = []
            self.images_left = []
            self.index = 0
            self.counter = 0
            for pl in range(1, 5):  # loading in walking images (1-4)
                img_right = pygame.image.load(f'player{pl}.png')
                img_right = pygame.transform.scale(img_right, (30, 40))  # scaling player height
                img_left = pygame.transform.flip(img_right, True, False)
                self.images_right.append(img_right)
                self.images_left.append(img_left)
            self.image = self.images_right[self.index]
            dead = pygame.image.load("ghost.png")
            self.dead_image = pygame.transform.scale(dead, (100, 100))
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.breadth = self.image.get_width()
            self.height = self.image.get_height()
            self.vel_y = 0
            self.jump = False
            self.direction = 0
            self.mid_air = True


    class Map:
        def __init__(self, data):
            self.block_list = []

            # load images
            dirt = pygame.image.load("land2.png")
            grass = pygame.image.load("land.png")

            row_count = 0
            for row in data:
                col_count = 0
                for block in row:
                    if block == 1:
                        img = pygame.transform.scale(dirt, (block_size, block_size))
                        img_rect = img.get_rect()
                        img_rect.x = col_count * block_size
                        img_rect.y = row_count * block_size
                        block = (img, img_rect)
                        self.block_list.append(block)
                    if block == 2:
                        img = pygame.transform.scale(grass, (block_size, block_size))
                        img_rect = img.get_rect()
                        img_rect.x = col_count * block_size
                        img_rect.y = row_count * block_size
                        block = (img, img_rect)
                        self.block_list.append(block)
                    if block == 3:
                        blob = Enemy(col_count * block_size, row_count * block_size + 4)
                        blob_group.add(blob)
                    if block == 4:
                        platform = Platform(col_count * block_size, row_count * block_size, 1, 0)
                        platform_group.add(platform)
                    if block == 5:
                        platform = Platform(col_count * block_size, row_count * block_size, 0, 1)
                        platform_group.add(platform)
                    if block == 6:
                        lava = Lava(col_count * block_size, row_count * block_size + 17.5)
                        lava_group.add(lava)
                    if block == 7:
                        coin = Coin(col_count * block_size + (block_size // 2),
                                    row_count * block_size + (block_size // 2))
                        coin_group.add(coin)
                    if block == 8:
                        exit = Exit(col_count * block_size, row_count * block_size - 17.5 + 4)
                        exit_group.add(exit)
                    col_count += 1
                row_count += 1

        def draw(self):
            for block in self.block_list:
                screen.blit(block[0], block[1])


    class Enemy(pygame.sprite.Sprite):
        def __init__(self, x, y):
            pygame.sprite.Sprite.__init__(self)
            blob = pygame.image.load("michael_blob.png")
            blob_size = 30
            self.image = pygame.transform.scale(blob, (blob_size, blob_size))
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.move_direction = 1
            self.move_count = 0

        def update(self):
            self.rect.x += self.move_direction
            self.move_count += 1
            if abs(self.move_count) > 35:
                self.move_direction *= -1
                self.move_count *= -1


    class Platform(pygame.sprite.Sprite):
        def __init__(self, x, y, move_x, move_y):
            pygame.sprite.Sprite.__init__(self)
            img = pygame.image.load('land2.png')
            self.image = pygame.transform.scale(img, (block_size, block_size))
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.move_counter = 0
            self.move_direction = 1
            self.move_x = move_x
            self.move_y = move_y

        def update(self):
            self.rect.x += self.move_direction * self.move_x
            self.rect.y += self.move_direction * self.move_y
            self.move_counter += 1
            if abs(self.move_counter) > 35:
                self.move_direction *= -1
                self.move_counter *= -1


    class Lava(pygame.sprite.Sprite):
        def __init__(self, x, y):
            pygame.sprite.Sprite.__init__(self)
            lava = pygame.image.load("lava.png")
            self.image = pygame.transform.scale(lava, (block_size, block_size // 2))
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y


    class Coin(pygame.sprite.Sprite):
        def __init__(self, x, y):
            pygame.sprite.Sprite.__init__(self)
            img = pygame.image.load('coin.png')
            self.image = pygame.transform.scale(img, (block_size // 2, block_size // 2))
            self.rect = self.image.get_rect()
            self.rect.center = (x, y)


    class Exit(pygame.sprite.Sprite):
        def __init__(self, x, y):
            pygame.sprite.Sprite.__init__(self)
            gate = pygame.image.load("door.png")
            self.image = pygame.transform.scale(gate, (block_size, int(block_size * 1.5)))
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y


    player = Player(50, screen_height - 85)

    blob_group = pygame.sprite.Group()
    platform_group = pygame.sprite.Group()
    lava_group = pygame.sprite.Group()
    exit_group = pygame.sprite.Group()
    coin_group = pygame.sprite.Group()

    # coins for showing he score
    score_coin = Coin(block_size // 2, block_size // 2)
    coin_group.add(score_coin)

    # loading pickle and world_data
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    map = Map(world_data)

    # creating buttons
    restart_button = Reset(350, 350, restart_img)
    start_button = Reset(150, 300, start_img)
    exit_button = Reset(450, 300, exit_img)

    screen_time = True
    while screen_time:
        timer.tick(fps)

        screen.blit(sky_png, (0, 0))
        screen.blit(sun_png, (30, 30))

        if main_menu:
            if exit_button.draw_button():
                screen_time = False
            if start_button.draw_button():
                main_menu = False
        else:
            map.draw()

            if game_over == 0:
                blob_group.update()
                platform_group.update()
                # updating score and checking if score has been added
                if pygame.sprite.spritecollide(player, coin_group, True):
                    score += 1
                    draw_text('X ' + str(score), font_score, white, block_size - 10, 10)

            blob_group.draw(screen)
            platform_group.draw(screen)
            lava_group.draw(screen)
            coin_group.draw(screen)
            exit_group.draw(screen)

            game_over = player.pl_draw(game_over)

            # when player has died
            if game_over == -1:
                if restart_button.draw_button():
                    world_data = []
                    map = reset_level(level)
                    game_over = 0
                    score = 0

            # if player has won the level
            if game_over == 1:
                # restart game and move to next level
                level += 1

                if level <= max_levels:
                    # reset level
                    world_data = []
                    map = reset_level(level)
                    game_over = 0
                else:
                    draw_text(f'YOU WIN! {player_name}', font, blue, (screen_breadth // 2) - 140, screen_height // 2)
                    if restart_button.draw_button():
                        level = 1
                        # reset level
                        world_data = []
                        map = reset_level(level)
                        game_over = 0
                        score = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                screen_time = False

        pygame.display.update()
    pygame.quit()
else:
    quit()
