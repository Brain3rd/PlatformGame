import pygame
import random
import pickle
import sys

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()
pygame.font.init()

# Window
WIDTH = 800
HEIGHT = 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Platform')
FPS = 60

# Fonts
RESTART_FONT = pygame.font.SysFont('tahoma', 70)
SCORE_FONT = pygame.font.SysFont('tahoma', 20)
FINISH_FONT = pygame.font.SysFont('tahoma', 30)

# Colors
WHITE = (255, 255, 255)
ORANGE = (255, 102, 0)
BLACK = (0, 0, 0)

# Images
SUN = pygame.image.load('images/sun.png')
BG = pygame.image.load('images/backgroundForest.png')
DIRT = pygame.image.load('images/snow0.png')
GRASS = pygame.image.load('images/snow1.png')
PLATFORM = pygame.image.load('images/snowhalf.png')
PLAYER = {
    'stand': [pygame.image.load(f'images/stand{n}.png') for n in range(6)],
    'walk': [pygame.image.load(f'images/walk{n}.png') for n in range(8)],
    'jump': pygame.image.load('images/jump0.png'),
    'duck': pygame.image.load('images/duck.png')
}
WORM = [
    [pygame.image.load('images/worm0.png'), pygame.image.load('images/worm1.png')],
    [pygame.image.load('images/barnacle0.png'), pygame.image.load('images/barnacle1.png')],
    [pygame.image.load('images/frog.png'), pygame.image.load('images/frog_move.png')],
    [pygame.image.load('images/ladybug.png'), pygame.image.load('images/ladybug_move.png')],
    [pygame.image.load('images/mouse.png'), pygame.image.load('images/mouse_move.png')],
    [pygame.image.load('images/sawHalf.png'), pygame.image.load('images/sawHalf_move.png')],
    [pygame.image.load('images/slimeBlock.png'), pygame.image.load('images/slimeBlock_move.png')],
    [pygame.image.load('images/snail.png'), pygame.image.load('images/snail_move.png')],
]
FLY = [
    [pygame.image.load('images/bee.png'), pygame.image.load('images/bee_move.png')],
    [pygame.image.load('images/fly.png'), pygame.image.load('images/fly_move.png')],
]
WATER = [pygame.image.load(f'images/water{n}.png') for n in range(2)]
DIVE = pygame.image.load('images/dive.png')
FELL = pygame.image.load('images/fell.png')
ANGEL = pygame.image.load('images/angel.png')
RESTART = pygame.image.load('images/restartbtn.png')
FLOWER = [pygame.image.load(f'images/flower{n}.png') for n in range(7)]
DOOR = pygame.image.load('images/door.png')
HEALTH = pygame.image.load('images/bar.png')

# Sounds
SCORE_FX = pygame.mixer.Sound('sounds/score.wav')
SCORE_FX.set_volume(0.5)
JUMP_FX = pygame.mixer.Sound('sounds/jump.wav')
JUMP_FX.set_volume(0.5)
GAME_OVER_FX = pygame.mixer.Sound('sounds/game_over.wav')
GAME_OVER_FX.set_volume(0.5)

# Music
# pygame.mixer.music.load('sounds/music.wav')
# pygame.mixer.music.play(-1, 0.0, 5000)

# Tile settings
TILE_SIZE = 50


class World:
    def __init__(self, data):
        self.tiles = []

        # Sprite groups
        self.worm_group = pygame.sprite.Group()
        self.fly_group = pygame.sprite.Group()
        self.water_group = pygame.sprite.Group()
        self.under_water_group = pygame.sprite.Group()
        self.flower_group = pygame.sprite.Group()
        self.platform_group = pygame.sprite.Group()
        self.door_group = pygame.sprite.Group()

        # World items
        rows = 0
        for row in data:
            columns = 0
            for tile in row:
                if tile == 0:
                    img = pygame.transform.scale(DIRT, (TILE_SIZE, TILE_SIZE))
                    img_rect = img.get_rect()
                    img_rect.x = columns * TILE_SIZE
                    img_rect.y = rows * TILE_SIZE
                    tile = (img, img_rect)
                    self.tiles.append(tile)
                if tile == 1:
                    img = pygame.transform.scale(GRASS, (TILE_SIZE, TILE_SIZE))
                    img_rect = img.get_rect()
                    img_rect.x = columns * TILE_SIZE
                    img_rect.y = rows * TILE_SIZE
                    tile = (img, img_rect)
                    self.tiles.append(tile)
                if tile == 2:
                    water = Water(columns * TILE_SIZE, rows * TILE_SIZE)
                    self.water_group.add(water)
                if tile == 3:
                    water = DeepWater(columns * TILE_SIZE, rows * TILE_SIZE)
                    self.water_group.add(water)
                if tile == 4:
                    water = DeepWater(columns * TILE_SIZE, rows * TILE_SIZE)
                    self.under_water_group.add(water)
                if tile == 5:
                    worm = Worm(columns * TILE_SIZE + 20, rows * TILE_SIZE + 20)
                    self.worm_group.add(worm)
                if tile == 6:
                    flower = Flower(columns * TILE_SIZE + TILE_SIZE // 2, rows * TILE_SIZE + TILE_SIZE - 8)
                    self.flower_group.add(flower)
                if tile == 7:
                    # Tile move x axis
                    platform = Platform(columns * TILE_SIZE, rows * TILE_SIZE, True, False)
                    self.platform_group.add(platform)
                if tile == 8:
                    # Tile move y axis
                    platform = Platform(columns * TILE_SIZE, rows * TILE_SIZE, False, True)
                    self.platform_group.add(platform)
                if tile == 9:
                    # Fly move x axis
                    fly = Fly(columns * TILE_SIZE + 20, rows * TILE_SIZE + 20, True, False)
                    self.fly_group.add(fly)
                if tile == 10:
                    door = Door(columns * TILE_SIZE, rows * TILE_SIZE)
                    self.door_group.add(door)
                if tile == 11:
                    # Fly move y axis
                    fly = Fly(columns * TILE_SIZE + 20, rows * TILE_SIZE + 20, False, True)
                    self.fly_group.add(fly)
                columns += 1
            rows += 1

    def draw(self, window):
        for tile in self.tiles:
            window.blit(tile[0], tile[1])

            # Grid lines
            # pygame.draw.rect(window, (255, 255, 255), tile[1], 2)


def grid_lines():
    for line in range(0, 20):
        pygame.draw.line(WIN, (255, 255, 255), (0, line * TILE_SIZE), (WIDTH, line * TILE_SIZE))
        pygame.draw.line(WIN, (255, 255, 255), (line * TILE_SIZE, 0), (line * TILE_SIZE, HEIGHT))


class Character:
    def __init__(self, health=50):
        # Images
        self.health = health
        self.walk_right = []
        self.walk_left = []
        self.stand = []
        self.char_size = (40, 50)
        self.jump = pygame.transform.scale(PLAYER['jump'], self.char_size)
        self.dive = pygame.transform.scale(DIVE, self.char_size)
        self.angel = pygame.transform.scale(ANGEL, (50, 50))
        self.duck = pygame.transform.scale(PLAYER['duck'], self.char_size)
        for n in range(8):
            walk = pygame.transform.scale(PLAYER['walk'][n], self.char_size)
            self.walk_right.append(walk)
            self.walk_left.append(pygame.transform.flip(walk, True, False))
        for n in range(6):
            stand = pygame.transform.scale(PLAYER['stand'][n], self.char_size)
            self.stand.append(stand)
        self.image = self.stand[1]
        self.rect = self.image.get_rect()

    def get_width(self):
        return self.image.get_width()

    def get_height(self):
        return self.image.get_height()

    def draw(self, window):
        # Draw Character onto screen
        window.blit(self.image, self.rect)


class Player(Character):
    def __init__(self, x, y, health=50):
        super().__init__(health)
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.index = 0
        self.counter = 0
        self.direction = 0
        self.jumped = False
        self.idle = 0
        self.still = 0
        self.in_air = False
        self.max_health = 100

    def controls(self, world):
        delta_x = 0
        delta_y = 0
        walking_speed = 4
        collision_range = 20

        # Animation speed
        walking_delay = 4
        standing_delay = 100

        # Player controls
        key = pygame.key.get_pressed()

        if key[pygame.K_LEFT]:
            delta_x -= walking_speed
            self.counter += 1
            self.direction = -1

        if key[pygame.K_RIGHT]:
            delta_x += walking_speed
            self.counter += 1
            self.direction = 1

        if key[pygame.K_UP] and not self.jumped and not self.in_air:
            self.vel_y = -15
            self.jumped = True
            self.image = self.jump
            JUMP_FX.play()

        if not key[pygame.K_UP]:
            self.jumped = False

        if key[pygame.K_DOWN]:
            self.image = self.duck

        if not key[pygame.K_LEFT] and not key[pygame.K_RIGHT] and not key[pygame.K_UP] and not key[pygame.K_DOWN]:
            self.idle += 1
            self.image = self.stand[self.still]

        # Walking Animation
        if self.counter > walking_delay:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.walk_right):
                self.index = 0
            if self.direction == 1:
                self.image = self.walk_right[self.index]
            if self.direction == -1:
                self.image = self.walk_left[self.index]

        # Standing animation
        if self.idle > standing_delay:
            self.idle = 0
            self.still += 1
            if self.still >= len(self.stand):
                self.still = 0

        # Gravity
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
        delta_y += self.vel_y

        # Collision with walls
        self.in_air = True
        for tile in world.tiles:
            # Check for collision in x direction, collision between rectangles
            if tile[1].colliderect(self.rect.x + delta_x, self.rect.y, self.get_width(), self.get_height()):
                delta_x = 0
            # Check for collision in y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + delta_y, self.get_width(), self.get_height()):
                # Check if below the ground i.e. jumping
                if self.vel_y < 0:
                    delta_y = tile[1].bottom - self.rect.top
                    self.vel_y = 0
                # Check if above the ground i.e. falling
                elif self.vel_y >= 0:
                    delta_y = tile[1].top - self.rect.bottom
                    self.vel_y = 0
                    self.in_air = False

        # Collision with platforms
        for platform in world.platform_group:
            # Collision in x axis
            if platform.rect.colliderect(self.rect.x + delta_x, self.rect.y, self.get_width(), self.get_height()):
                delta_x = 0
            # Collision in y axis
            if platform.rect.colliderect(self.rect.x, self.rect.y + delta_y, self.get_width(), self.get_height()):
                # Check if below platform
                if abs((self.rect.top + delta_y) - platform.rect.bottom) < collision_range:
                    # If player hit her hed in platform, stop upside movement
                    self.vel_y = 0
                    # How much can move up
                    delta_y = platform.rect.bottom - self.rect.top
                # Check if above platform
                elif abs((self.rect.bottom + delta_y) - platform.rect.top) < collision_range:
                    # Don't let player drop through platform
                    self.rect.bottom = platform.rect.top - 1
                    delta_y = 0
                    self.in_air = False
                # Move sideways with the platform
                if platform.move_x:
                    self.rect.x += platform.move_direction

        # Update player coordinates
        self.rect.x += delta_x
        self.rect.y += delta_y

        # Don't let player off bottom of the screen, debunking
        # if self.rect.bottom > HEIGHT - 50:
        #     self.rect.bottom = HEIGHT - 50
        #     # delta_y = 0

    def swim(self, world):
        keys = pygame.key.get_pressed()
        delta_x = 0
        delta_y = 0
        self.image = self.dive
        can_move = True

        for tile in world.tiles:
            # Check for collision in x direction, collision between rectangles
            if tile[1].colliderect(self.rect.x + delta_x, self.rect.y, self.get_width(), self.get_height()):
                delta_x = 0
                can_move = False

            # Check for collision in y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + delta_y, self.get_width(), self.get_height()):
                # Swimming up
                if self.vel_y < 0:
                    delta_y += 1
                    can_move = False
                # Swimming down
                if self.vel_y >= 0:
                    delta_y -= 1
                    can_move = False

        if keys[pygame.K_UP] and can_move:
            delta_y -= 2
            self.image = pygame.transform.rotate(self.dive, 180)

        if keys[pygame.K_RIGHT]:
            delta_x += 1
            self.image = pygame.transform.rotate(self.dive, 90)

        if keys[pygame.K_LEFT]:
            delta_x -= 1
            self.image = pygame.transform.rotate(self.dive, 270)

        # Update player coordinates
        self.rect.x += delta_x
        self.rect.y += delta_y

    def collided(self, sprite_group):
        # Collision with enemies, collision with sprites, if True delete sprite after collision
        if pygame.sprite.spritecollide(self, sprite_group, False):
            return True

    def pick_up_flower(self, sprite_group):
        keys = pygame.key.get_pressed()
        if pygame.sprite.spritecollide(self, sprite_group, False):
            if keys[pygame.K_DOWN]:
                # Remove flower after its collected
                pygame.sprite.spritecollide(self, sprite_group, True)
                return True

    def draw(self, window):
        # Draw Character onto screen
        super().draw(window)

        # Draw player box
        # Screen, color, target, line_width
        # pygame.draw.rect(window, (255, 255, 255), self.rect, 2)

    def health_bar(self, window, x, y):
        pygame.draw.rect(window, (255, 0, 0), (x, y, 200, 15))
        pygame.draw.rect(window, (0, 255, 0), (x, y, 200 * (self.health/self.max_health), 15))


class Water(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(WATER[0], (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class DeepWater(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(WATER[1], (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Worm(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        # Images
        self.worm_right = []
        self.worm_left = []
        worm_list = random.choice(WORM)
        for n in range(2):
            image = pygame.transform.scale(worm_list[n], (TILE_SIZE - 20, TILE_SIZE - 20))
            self.worm_left.append(image)
            image = pygame.transform.flip(image, True, False)
            self.worm_right.append(image)
        self.image = self.worm_right[0]
        self.rect = self.image.get_rect()

        # Settings
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0
        self.index = 0
        self.counter = 0
        self.turning_point = 50
        self.animation_delay = 10

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        self.counter += 1

        # Change direction
        if abs(self.move_counter > self.turning_point):
            self.move_direction *= -1
            self.move_counter *= -1

        # Animation
        if self.counter > self.animation_delay:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.worm_left):
                self.index = 0
            if self.move_direction == 1:
                self.image = self.worm_right[self.index]
            if self.move_direction == -1:
                self.image = self.worm_left[self.index]


class Fly(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        # Images
        self.fly_right = []
        self.fly_left = []
        fly_list = random.choice(FLY)
        for n in range(2):
            image = pygame.transform.scale(fly_list[n], (TILE_SIZE - 20, TILE_SIZE - 20))
            self.fly_left.append(image)
            image = pygame.transform.flip(image, True, False)
            self.fly_right.append(image)
        self.image = self.fly_right[0]
        self.rect = self.image.get_rect()

        # Settings
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0
        self.index = 0
        self.counter = 0
        self.turning_point = 50
        self.animation_delay = 10
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        self.move_counter += 1
        self.counter += 1

        if self.move_x:
            self.rect.x += self.move_direction
        if self.move_y:
            self.rect.y += self.move_direction

        # Change direction
        if abs(self.move_counter > self.turning_point):
            # Change direction
            self.move_direction *= -1
            self.move_counter *= -1

        # Animation
        if self.counter > self.animation_delay:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.fly_left):
                self.index = 0
            if self.move_direction == 1:
                self.image = self.fly_right[self.index]
            if self.move_direction == -1:
                self.image = self.fly_left[self.index]


class Flower(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(random.choice(FLOWER), (TILE_SIZE // 3, TILE_SIZE // 3))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(PLATFORM, (TILE_SIZE, TILE_SIZE // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0
        self.move_direction = 1
        self.turning_point = 50
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        self.move_counter += 1
        if self.move_x:
            self.rect.x += self.move_direction
        if self.move_y:
            self.rect.y += self.move_direction

        # Change direction
        if abs(self.move_counter > self.turning_point):
            self.move_direction *= -1
            self.move_counter *= -1


class Door(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(DOOR, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self, window):
        # Draw button
        window.blit(self.image, self.rect)

        action = False

        # Get mouse position
        position = pygame.mouse.get_pos()

        # Check mouseover
        if self.rect.collidepoint(position):
            if pygame.mouse.get_pressed(3)[0] == 1 and not self.clicked:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed(3)[0] == 0:
            self.clicked = False
        return action


# Game is on
def platform_game():
    level = 10
    max_levels = 10
    health = 50

    def load_level():
        # Load level data
        pickle_in = open(f'levels/level{level}', 'rb')
        world_data = pickle.load(pickle_in)
        return world_data

    player_controls = True
    player_dead = False
    score = 0
    restart = False
    finish = False
    finish_btn = False
    starting_pos = [100, HEIGHT - 50]

    clock = pygame.time.Clock()

    world = World(load_level())

    player = Player(starting_pos[0], starting_pos[1], health=health)

    restart_btn = Button(WIDTH // 2 - RESTART.get_width() // 2, HEIGHT // 2 + 100, RESTART)

    score_flower = Flower(WIDTH - 126, TILE_SIZE + 15)
    world.flower_group.add(score_flower)

    def refresh_window():
        # Draw images to the screen
        WIN.blit(BG, (0, 0))
        WIN.blit(SUN, (480, 110))

        # Draw world
        world.draw(WIN)

        # Draw sprites
        world.water_group.draw(WIN)
        world.under_water_group.draw(WIN)
        world.worm_group.draw(WIN)
        world.worm_group.update()
        world.fly_group.draw(WIN)
        world.fly_group.update()
        world.flower_group.draw(WIN)
        world.platform_group.draw(WIN)
        world.platform_group.update()
        world.door_group.draw(WIN)

        # Draw player
        player.draw(WIN)

        # Draw gridlines
        # grid_lines()

        # Level text
        level_label = SCORE_FONT.render(f'LEVEL {level}', True, BLACK)
        WIN.blit(level_label, (WIDTH//2 + 83, 52))

        # Score text
        score_label = SCORE_FONT.render(f'X {score}', True, BLACK)
        WIN.blit(score_label, (WIDTH - 110, 52))

        # Health bar
        health_label = SCORE_FONT.render('HEALTH', True, BLACK)
        WIN.blit(health_label, (63, 52))
        player.health_bar(WIN, 154, 58)

        # Finish game
        if finish_btn:
            finish_label = FINISH_FONT.render('Congratulations! You finished the game.', True, ORANGE)
            WIN.blit(finish_label, (WIDTH // 2 - finish_label.get_width() // 2, HEIGHT // 2))
            if restart_btn.draw(WIN):
                platform_game()

        # Restart game
        if restart:
            game_over_label = RESTART_FONT.render('Game Over', True, ORANGE)
            WIN.blit(game_over_label, (WIDTH // 2 - game_over_label.get_width() // 2, HEIGHT // 2))
            if restart_btn.draw(WIN):
                platform_game()

        # Update window
        pygame.display.update()

    while True:
        clock.tick(FPS)
        refresh_window()

        # Give control to the player
        if player_controls:
            player.controls(world)

        # Check if player goes swimming
        if player.collided(world.water_group):
            player.rect.y += 1
            player_controls = False
            # Change controls to swimming settings
            player.swim(world)
            # If player goes off water, change controls back to normal
            if not player.collided(world.water_group):
                player_controls = True
            # If player goes too deep in water
            if player.collided(world.under_water_group):
                player.health -= 1
                if player.health == 0:
                    player_dead = True
                    GAME_OVER_FX.play()
                elif player.health > player.max_health:
                    player.health = player.max_health

        # Player collided with enemies
        if player.collided(world.worm_group) or player.collided(world.fly_group):
            player.health -= 1
            if player.health == 0:
                player_dead = True
                GAME_OVER_FX.play()
            elif player.health > player.max_health:
                player.health = player.max_health

        # Pick up those flowers
        if player.pick_up_flower(world.flower_group):
            score += 1
            player.health += 10
            SCORE_FX.play()
            if player.health > 100:
                player.health = 100

        # Go to next level
        if player.collided(world.door_group):
            if level == max_levels:
                finish = True
            else:
                level += 1
                world = World(load_level())
                player.rect.x = starting_pos[0]
                player.rect.y = starting_pos[1]
                score_flower = Flower(WIDTH - 126, TILE_SIZE + 15)
                world.flower_group.add(score_flower)

        # It's over
        if player_dead:
            player_controls = False
            restart = True
            player.image = player.angel
            if player.rect.y > 80:
                player.rect.y -= 2

        # Congratulations
        if finish:
            world.door_group.empty()
            player_controls = False
            finish_btn = True

        # Close window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


def main_menu():
    menu_img = pygame.transform.scale(BG, (800, 800))
    WIN.blit(menu_img, (0, 0))

    player = pygame.transform.scale(PLAYER['stand'][5], (90, 110))
    WIN.blit(player, (60, 20))
    player_label = SCORE_FONT.render("Left and right to move. Up to jump. Down to collect flowers.", True, BLACK)
    WIN.blit(player_label, (180, 75))

    flower = pygame.transform.scale(FLOWER[0], (FLOWER[0].get_width() // 2, FLOWER[0].get_height() // 2))
    WIN.blit(flower, (90, 170))
    flower_label = SCORE_FONT.render("Collect flowers.", True, BLACK)
    WIN.blit(flower_label, (180, 170))

    worm = pygame.transform.scale(WORM[0][0], (WORM[0][0].get_width() // 2, WORM[0][0].get_height() // 2))
    WIN.blit(worm, (75, 205))
    worm_label = SCORE_FONT.render("Worms and bugs are scary. They try to harm you.", True, BLACK)
    WIN.blit(worm_label, (180, 245))

    fly = pygame.transform.scale(FLY[0][0], (FLY[0][0].get_width() // 2, FLY[0][0].get_height() // 2))
    WIN.blit(fly, (75, 295))
    fly_label = SCORE_FONT.render("Bees and flies are scary. They try to harm you.", True, BLACK)
    WIN.blit(fly_label, (180, 320))

    water = pygame.transform.scale(WATER[0], (WATER[0].get_width() // 2, WATER[0].get_height() // 2))
    WIN.blit(water, (75, 365))
    water_label = SCORE_FONT.render("Player can swim. Don't go too deep though.", True, BLACK)
    WIN.blit(water_label, (180, 395))

    health = pygame.transform.scale(HEALTH, (HEALTH.get_width() // 2, HEALTH.get_height() // 2))
    WIN.blit(health, (55, 482))
    health_label = SCORE_FONT.render("This is your health bar. If all red, game over.", True, BLACK)
    WIN.blit(health_label, (180, 470))

    door = pygame.transform.scale(DOOR, (DOOR.get_width(), DOOR.get_height()))
    WIN.blit(door, (75, 530))
    door_label = SCORE_FONT.render("Enter next level through this door.", True, BLACK)
    WIN.blit(door_label, (180, 545))

    begin_label = SCORE_FONT.render("Click mouse button to begin...", True, BLACK)
    WIN.blit(begin_label, (260, 645))

    while True:
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                platform_game()


if __name__ == '__main__':
    main_menu()
