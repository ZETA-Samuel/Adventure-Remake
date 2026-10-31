import os
import pygame, asyncio

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def asset_path(*parts):
    return os.path.join(BASE_DIR, *parts)


# initalization
pygame.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode((1280,832)) # display surface
width, height = screen.get_size()
pygame.display.set_caption("Adventure")

# level info
TILE_SIZE = 32

# loading texture
def load_tile_image(path, color):
    try:
        image = pygame.image.load(asset_path(path)).convert_alpha()
        return pygame.transform.scale(image,(TILE_SIZE,TILE_SIZE))
    except (pygame.error, FileNotFoundError, OSError):
        image = pygame.Surface((TILE_SIZE,TILE_SIZE))
        image.fill(color)
        return image

tile_images = {
    "G": load_tile_image("tiles/grass.png",(70,180,70)),
    "#": load_tile_image("tiles/stone.png", (120,120,130)),
    #"C": load_tile_image("tiles/crate.png", (150,95,45)),
}

key_image = pygame.image.load(asset_path("items", "key.png")).convert_alpha()
door_image = pygame.image.load(asset_path("items", "door.png")).convert_alpha()
door_image_open = pygame.image.load(asset_path("items", "door_open.png")).convert_alpha()
turret_image = pygame.image.load(asset_path("items", "turret.png")).convert_alpha()
spikes_image = pygame.image.load(asset_path("items", "spikes.png")).convert_alpha()
blast_image = pygame.image.load(asset_path("items", "explosion.png")).convert_alpha()

key_image = pygame.transform.scale(key_image, (36, 18))
door_image = pygame.transform.scale(door_image, (32, 48))
door_image_open = pygame.transform.scale(door_image_open, (32, 48))
turret_image = pygame.transform.scale(turret_image, (32, 48))
spikes_image = pygame.transform.scale(spikes_image,(32,24))
blast_image = pygame.transform.scale(blast_image, (80, 80))



# . = empty space
# G = grass
# # = stone
# P = player spawn
# D = door
# K = key
# S = spikes
# T = turret
# B = bullet
levels = [
         
    [
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "..............................D.........",
    "............................#####.......",
    "...................####.................",
    "........#######.........................",
    "........................................",
    "..P................................K....",
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    ],
    [
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    ".....................K..................",
    "........................................",
    "..P....SS.......S............SS........D",
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    ],
    [
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "T......................................T",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "................#.......................",
    ".......GG.......#.......................",
    "................#.......................",
    "..............GG#.......................",
    "..P.............#...K..............D....",
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    ],
    [
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "................................K.......",
    "T............................. ###......",
    "........................................",
    ".........................###............",
    "........................................",
    "...................###..................",
    "........................................",
    ".............###........................",
    "....P..........SSSSSSSSSSSSSSSSSSS...D..",
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    ],


]
def load_level(level_data):
    walls = []
    spikes = []
    turrets = []
    spawn = (100, 100)

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
                    y + TILE_SIZE,
                )

            elif symbol == "K":
                key = pygame.Rect(x+6, y+6, 20, 20)
                
            elif symbol == "D":
                door = pygame.Rect(x+4, y, 24, TILE_SIZE)

            elif symbol == "S":
                spikes.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))

            elif symbol == "T":
                turrets.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))

    walls.append(pygame.Rect(-TILE_SIZE, 0, TILE_SIZE, height))
    walls.append(pygame.Rect(width, 0, TILE_SIZE, height))
    walls.append(pygame.Rect(0, -TILE_SIZE, width, TILE_SIZE))
    walls.append(pygame.Rect(0, height, width, TILE_SIZE))

    return walls, spawn, key, door, spikes, turrets

def show_instructions(screen):
    screen.fill((25,30,45))

    title_font = pygame.font.Font(None,75)
    font = pygame.font.Font(None,36)
    small_font = pygame.font.Font(None, 28)

    title = title_font.render("HOW TO PLAY", True, (255,255,255))
    screen.blit(title, title.get_rect(center=(640,120)))


    instructions = [
        "A / D or LEFT / RIGHT  -  Move [P - Hitbox / Y - Respawn]",
        "SPACE  -  Jump",
        "SHIFT  -  Dash",
        "Collect the KEY to unlock the DOOR.",
        "Avoid spikes, turret & bullets!",
        "Reach the door to complete the level.",

    ]

    y = 230

    for instruction in instructions:
        text = font.render(instruction, True, (230,230,230))
        screen.blit(text, text.get_rect(center=(640,y)))
        y += 55

    start_text = small_font.render(
        "Press ENTER to start", True, (100,255,150)
    )

    screen.blit(start_text, start_text.get_rect(center=(640,650)))


# player class
class Player(pygame.sprite.Sprite):
    def __init__(self,pos):
        super().__init__()

        self.sprite_sheet = pygame.image.load(asset_path("animation", "hero.png")).convert_alpha()
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
        self.spawn_pos = pygame.Vector2(pos)
        self.blast_timer = 0
        self.blast_duration = 0.35
        self.show_blast = False
        self.blast_position = pygame.Vector2()



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
        self.normal_width = self.rect.width
        self.normal_height = self.rect.height

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


    def restore_hitbox(self,walls):
        above = self.rect.copy()
        above.height = self.normal_height
        above.bottom = self.rect.bottom

        if not any(above.colliderect(wall) for wall in walls):
            self.rect = above
            return True

        below = self.rect.copy()
        below.height = self.normal_height
        below.top = self.rect.top

        if not any(below.colliderect(wall) for wall in walls):
            self.rect = below
            return True

        self.dying = True
        self.current_animation = None
        return False

    def respawn(self):
        self.rect.width = self.normal_width
        self.rect.height = self.normal_height

        self.rect.midbottom=self.spawn_pos

        self.velocity_y = 0
        self.velocity_x = 0

        # self.direction.update(0,0)
        self.moving = False
        self.on_ground = False

        self.dying = False
        self.dead = False

        self.dash_timer = 0
        # self.dash_cooldown_timer = 0

        # self.rect.height = self.normal_height

        # self.current_animation = None
        # self.frame_index = 0
        # self.animation_timer = 0
        # self.image = self.idle_image

        self.draw_rect = self.image.get_rect(midbottom=self.rect.midbottom)


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
        if self.show_blast:
            self.blast_timer -= dt

            if self.blast_timer <= 0:
                self.show_blast = False
                self.dying = True
                self.current_animation = None

            else:
                return

        if self.dead:
            self.respawn()
            return

        if self.dying:
            self.animate(dt, self.death_animation, loop=False,speed=8)
            self.draw_rect = self.image.get_rect(midbottom = self.rect.midbottom)

            if self.frame_index >= len(self.death_animation) -1:
                self.dead = True

            return

        was_dashing = self.dash_timer > 0

        self.dash_timer = max(0, self.dash_timer - dt)

        if was_dashing and self.dash_timer == 0:
            if not self.restore_hitbox(walls):
                self.dying = True
                self.current_animation = None
                return

        self.dash_cooldown_timer = max(0, self.dash_cooldown_timer - dt)


        self.input()
        self.move(dt, walls)

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


    def bullet_hit(self):
        if self.dying or self.dead or self.show_blast:
            return

        self.show_blast = True
        self.blast_timer = self.blast_duration
        self.blast_position = pygame.Vector2(self.rect.center)

async def main():
    show_debug = 1
    font = pygame.font.Font(None, 64)
    has_key = False
    game_won = False
    running = True
    current_level = 0
    bullets = []
    bullet_speed = 350
    shoot_timer = 0
    shoot_delay = 1.5 #seconds
    game_state = "instructions"
    level_elapsed = 0.0
    level_times = []

    timer_font = pygame.font.Font(None, 42)

    walls,spawn,key,door,spikes,turrets = load_level(levels[current_level])

    player = Player(spawn)
    all_sprites = pygame.sprite.Group(player)

    def next_level():
        nonlocal current_level
        nonlocal walls,spawn,key,door,spikes,turrets
        nonlocal has_key,game_won
        nonlocal level_elapsed

        level_times.append(level_elapsed)
        level_elapsed = 0.0

        current_level += 1

        if current_level >= len(levels):
            game_won = True
            return

        walls,spawn,key,door,spikes,turrets = load_level(
            levels[current_level]
        )

        player.spawn_pos = spawn
        player.respawn()

        has_key = False
        bullets.clear()
    a = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if game_state == "instructions":
                    if event.key == pygame.K_RETURN:
                        game_state = "playing"

                if event.key == pygame.K_o:
                    running = False

                if not player.dying and not player.dead and not game_won:

                    
                    
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

        if game_state == "instructions":
            show_instructions(screen)

        elif game_state == "playing":  

            if not game_won:
                level_elapsed += dt

            collision_walls = walls.copy()

            if not has_key:
                collision_walls.append(door)

            if not game_won:
                all_sprites.update(dt, collision_walls)

            if not player.dying and not player.dead:
                for spike in spikes:
                    if player.rect.colliderect(spike):
                        player.dying = True
                        player.current_animation = None
                        break

            # Key
            if not has_key and player.rect.colliderect(key):
                has_key = True
                # print("Key Collected!")

            # Door
            if not game_won and has_key and player.rect.colliderect(door):
                next_level()

            # print(has_key)

            # Draw tile
            if not game_won:
                for row_index,row in enumerate(levels[current_level]):
                    for col_index, symbol in enumerate(row):
                        x = col_index * TILE_SIZE
                        y = row_index * TILE_SIZE

                        if symbol in tile_images:
                            screen.blit(tile_images[symbol], (x,y))

            if game_state=="instructions":
                show_instructions(screen)

            elif game_state == "playing":
                pass

            # Draw key
            if not has_key:
                screen.blit(
                    key_image,
                    key_image.get_rect(center=key.center)
                )

            # Draw door 
            if has_key:
                screen.blit(
                    door_image_open,
                    door_image_open.get_rect(midbottom=door.midbottom)
                )
            else:
                screen.blit(
                    door_image,
                    door_image.get_rect(midbottom=door.midbottom)
                )

            # Draw spikes
            for spike in spikes:
                screen.blit(
                    spikes_image, 
                    spikes_image.get_rect(midbottom=spike.midbottom)
                )

            # Draw turret
            for turret in turrets:
                screen.blit(
                    turret_image, 
                    turret_image.get_rect(midbottom=turret.midbottom)
                )

            # Draw player
            for sprite in all_sprites:
                screen.blit(sprite.image, sprite.draw_rect)

            # Draw collision blast
            if player.show_blast:
                screen.blit(blast_image, blast_image.get_rect(center=player.blast_position))
            
            #  Draw Hit_box
            if show_debug == -1:
                pygame.draw.rect(screen, "red", player.rect,2)

            # Draw bullet
            shoot_timer += dt

            if shoot_timer >= shoot_delay:
                shoot_timer = 0

                for turret in turrets:
                    direction = pygame.Vector2(player.rect.center) - pygame.Vector2(turret.center)

                    if direction.length() > 0:
                        direction = direction.normalize()

                        bullets.append({
                            "pos": pygame.Vector2(turret.center),
                            "direction": direction
                        })

            for bullet in bullets[:]:
                bullet["pos"] += bullet["direction"] * bullet_speed * dt

                bullet_rect = pygame.Rect(
                    bullet["pos"].x - 6, 
                    bullet["pos"].y - 6,
                    12,
                    12
                )

                if any(bullet_rect.colliderect(wall) for wall in walls):
                    bullets.remove(bullet)
                    continue

                if bullet_rect.colliderect(player.rect):
                    bullets.remove(bullet)

                    player.bullet_hit()

                    continue

                if not screen.get_rect().colliderect(bullet_rect):
                    bullets.remove(bullet)

            for bullet in bullets[:]:
                pygame.draw.circle(
                    screen,
                    "yellow",
                    (int(bullet["pos"].x), int(bullet["pos"].y)),
                    6
                )

            # Display text
            if game_won:
                bullets.clear()
                
                message = font.render("Congrats! You completed all levels.", True, "white")
                screen.blit(
                    message,
                    message.get_rect(center = (width // 2, height // 2))
                )

        pygame.display.update()

        await asyncio.sleep(0)
asyncio.run(main())
