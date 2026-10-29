import pygame
import sys
from player import *
from pathlib import Path

# initalization
pygame.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode() # display surface
width,height = pygame.Surface.get_width(screen),pygame.Surface.get_height(screen)
pygame.display.set_caption("Adventure")
show_debug = 1
 # level info
TILE_SIZE = 32

# loading texture
def load_tile_image(path, color):
    try:
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image,(TILE_SIZE,TILE_SIZE))
    except (pygame.error, FileNotFoundError):
        image = pygame.Surface((TILE_SIZE,TILE_SIZE))
        image.fill(color)
        return image

tile_images = {
    "G": load_tile_image("tiles/grass.png",(70,180,70)),
    "#": load_tile_image("tiles/stone.png", (120,120,130)),
    #"C": load_tile_image("tiles/crate.png", (150,95,45)),
}

# . = empty space
# G = grass
# # = stone
# C = crate
# P = player spawn
# E = exit

level_1 = [
  "........................................",
  ".............................######.....",
  "........................................",
  ".................#..#...................",
  "........................................",
  ".....####....................#.#.#......",
  "........................................",
  "................####..................#.",
  "....#.##.............................#..",
  "..........#.............................",
  "...............................#.#.#....",
  "..............#.#.......................",
  "........................................",
  ".....##..................#..#...........",
  "...............#........................",
  "........................................",
  "......................#...#.............",
  "................#.......................",
  "........................................",
  "...####......#..................#######.",
  ".................###....................",
  "......................#####.............",
  "...........#####........................",
  "p.......................................",
  "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",

]
def load_level(level_data):
    walls = []
    spawn = (100,100)

    for row_index, row in enumerate(level_data):
        for col_index,symbol in enumerate(row):
            x = col_index * TILE_SIZE
            y = row_index * TILE_SIZE

            if symbol in ("G","#","C"):
                walls.append(
                    pygame.Rect(x,y, TILE_SIZE,TILE_SIZE)
                )

            elif symbol == "P":
                spawn = (
                    x + TILE_SIZE // 2,
                    y + TILE_SIZE ,
                )

    return walls, spawn

# player class
class Player(pygame.sprite.Sprite):
    def __init__(self,pos):
        super().__init__()

        self.sprite_sheet = pygame.image.load('animation/hero.png').convert_alpha()
        self.speed = 200
        self.velocity_y = 0
        self.gravity = 1200
        self.jump_strength = 500
        self.on_ground = False
        self.direction = pygame.Vector2()
        self.moving = False
        self.frame_width = 80
        self.frame_height = 80
        self.facing_left = False
        self.jump_animation = [self.get_frame(1,col) for col in range(8,12)]
        self.current_animation = None
        self.dash_animation = [self.get_frame(2,col) for col in range(12,15)]
        self.death_animation = [self.get_frame(2,15)] + [self.get_frame(3,col) for col in range(12)]
        self.dying = False
        self.dead = False
        self.dash_speed = 700
        self.dash_direction = 0.15
        self.dash_timer = 0
        self.dash_duration = 0.5
        self.dash_cooldown = 0.8
        self.dash_cooldown_timer = 0
        self.dash_direction = 1


        self.idle_image = self.get_frame(0,0)

        self.animations = []
        for col in range(12,16):
            self.animations.append(self.get_frame(0,col))
        for col in range(0,4):
            self.animations.append(self.get_frame(1,col))

        self.frame_index = 0
        self.animation_speed = 4
        self.run_animation_speed = 10
        self.animation_timer = 0

        self.image = self.idle_image
        self.rect = pygame.Rect(0,0,32,54)
        self.rect.midbottom = pos

        self.draw_rect = self.image.get_rect()
        self.draw_rect.midbottom = self.rect.midbottom

        self.normal_height = self.rect.height
        self.dash_height = self.normal_height // 2

    def get_frame(self,row,col):
        frame = pygame.Surface((self.frame_width,self.frame_height),pygame.SRCALPHA)

        frame.blit(self.sprite_sheet,(0,0),(
            col * self.frame_width,
            row * self.frame_height,
            self.frame_width,
            self.frame_height)
        )
        return frame

    def animate(self,dt,animation,loop=True,speed = None):
        if self.current_animation != animation:
            self.current_animation = animation
            self.frame_index = 0
            self.animation_timer = 0

        if speed is None:
            speed = self.animation_speed

        self.animation_timer += dt
        frame_duration = 1/ speed

        if self.animation_timer >= frame_duration:
            self.animation_timer -= frame_duration

            if loop:
                self.frame_index = (self.frame_index + 1) % len(animation)
            else:
                self.frame_index = min(self.frame_index + 1, len(animation) - 1)

        frame = animation[self.frame_index]
        self.image = pygame.transform.flip(frame,self.facing_left,False)


    def input(self):
        keys = pygame.key.get_pressed()

        self.direction.x = (keys[pygame.K_d] - keys[pygame.K_a])

        #self.direction.y = (keys[pygame.K_s] - keys[pygame.K_w])
        if self.direction.x > 0:
            self.facing_left = False
        elif self.direction.x < 0:
            self.facing_left = True

        self.moving = self.direction.length_squared() > 0

        if self.moving:
            self.direction = self.direction.normalize()

    def move(self,dt,walls):
        if self.dash_timer > 0:
            self.rect.x += self.dash_direction * self.dash_speed * dt
        else:
            self.rect.x += self.direction.x * self.speed * dt

        move_direction = (self.dash_direction if self.dash_timer > 0 else self.direction.x)


        for wall in walls:
            if self.rect.colliderect(wall):
                if move_direction > 0:
                    self.rect.right = wall.left
                elif move_direction < 0:
                    self.rect.left = wall.right

        self.velocity_y += self.gravity * dt
        self.rect.y += self.velocity_y * dt

        self.on_ground = False

        for wall in walls:
            if self.rect.colliderect(wall):
                if self.velocity_y > 0:
                    self.rect.bottom = wall.top
                    self.on_ground = True
                elif self.velocity_y < 0:
                    self.rect.top = wall.bottom

                self.velocity_y = 0

        if not self.on_ground:
            ground_check = self.rect.copy()
            ground_check.y += 2

            for wall in walls:
                if ground_check.colliderect(wall):
                    self.on_ground = True

                    if self.velocity_y > 0:
                        self.velocity_y = 0

                    break

    def jump(self):
        if self.on_ground:
            self.velocity_y = -self.jump_strength
            self.on_ground = False

    def update(self,dt,walls):
        if self.dead:
            return

        if self.dying:
           self.animate(dt, self.death_animation, loop=False,speed=8)
        
        if self.frame_index >= len(self.death_animation) -1:
            self.dead = True

            self.draw_rect.midbottom = self.image.get_rect(midbottom=self.rect.midbottom)
            return

        self.dash_timer = max(0, self.dash_timer - dt)
        self.dash_cooldown_timer = max(0,self.dash_cooldown_timer - dt)

        if self.dash_timer == 0 and self.rect.height != self.normal_height:
            bottom = self.rect.bottom
            self.rect.height = self.normal_height
            self.rect.bottom = bottom

        
        self.input()
        self.move(dt, walls)

        if self.dash_timer > 0:
            self.dash_timer = max(0, self.dash_timer - dt)

            if self.dash_timer == 0:
                bottom = self.rect.bottom
                self.rect.height = self.normal_height
                self.rect.bottom = bottom

        if self.dash_timer > 0:
            self.animate(dt, self.dash_animation,loop=True,speed=20)

        elif not self.on_ground:
            self.animate(dt,self.jump_animation,loop = False)

        elif self.moving:
            self.animate(dt, self.animations,speed=self.run_animation_speed)

        else:
            self.current_animation = None
            self.frame_index = 0
            self.animation_timer = 0
            self.image = pygame.transform.flip(self.idle_image,self.facing_left,False)

        self.draw_rect = self.image.get_rect(midbottom=self.rect.midbottom)


        # if self.moving:
        #     self.animate(dt,self.animations)

        # else:
        #     self.frame_index = 0
        #     self.image = pygame.transform.flip(self.idle_image,self.facing_left,False)


walls, spawn = load_level(level_1)

player = Player(spawn)
player.rect.midbottom = spawn
all_sprites = pygame.sprite.Group(player)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if not player.dying and not player.dead:

                if event.key in (pygame.K_w, pygame.K_SPACE):
                    player.jump()

                if event.key == pygame.K_LSHIFT:
                    if player.dash_cooldown_timer <= 0:
                        player.dash_direction = (-1 if player.facing_left else 1)
                        player.dash_timer = player.dash_duration
                        player.dash_cooldown_timer = player.dash_cooldown

                        bottom = player.rect.bottom
                        player.rect.height = player.dash_height
                        player.rect.bottom = bottom

                if event.key == pygame.K_p:
                    show_debug *= -1

                if event.key == pygame.K_y:
                    player.dying = True
                    player.current_animation = None

    dt = clock.tick(60) / 1000
    screen.fill("black")

    all_sprites.update(dt, walls)

    for row_index,row in enumerate(level_1):
        for col_index, symbol in enumerate(row):
            x = col_index * TILE_SIZE
            y = row_index * TILE_SIZE

            if symbol in tile_images:
                screen.blit(tile_images[symbol], (x,y))

    for sprite in all_sprites:
        screen.blit(sprite.image, sprite.draw_rect)
    

    if show_debug == 1:
        pygame.draw.rect(screen, "red", player.rect,2)

    pygame.display.update()



pygame.quit()
sys.exit()