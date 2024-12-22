import pygame
import random
import os

pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
SPACESHIP_SPEED = 5
ASTEROID_SPEED = 2
SPACE_BLUE = (10, 10, 50)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Asset paths
ASSETS_DIR = "Labs/assets"
SPACESHIP_IMG = os.path.join(ASSETS_DIR, "spaceship.png")
ASTEROID_IMG = os.path.join(ASSETS_DIR, "asteroid.png")
CRYSTAL_IMG = os.path.join(ASSETS_DIR, "energy_crystal.png")
BACKGROUND_MUSIC = os.path.join(ASSETS_DIR, "background_music.wav")
CLASH_SOUND = os.path.join(ASSETS_DIR, "clash_sound.wav")

# Initialize screen and assets
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Scavenger")

spaceship_image = pygame.image.load(SPACESHIP_IMG)
asteroid_image = pygame.image.load(ASTEROID_IMG)
crystal_image = pygame.image.load(CRYSTAL_IMG)
background_music = pygame.mixer.Sound(BACKGROUND_MUSIC)
clash_sound = pygame.mixer.Sound(CLASH_SOUND)

spaceship_image = pygame.transform.scale(spaceship_image, (50, 50))
asteroid_image = pygame.transform.scale(asteroid_image, (50, 50))
crystal_image = pygame.transform.scale(crystal_image, (30, 30))


class Spaceship:
    def __init__(self):
        self.image = spaceship_image
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.lives = 3
        self.speed = SPACESHIP_SPEED
        self.shield = False
        self.shield_timer = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        if self.shield:
            pygame.draw.circle(surface, BLUE, self.rect.center, 35, 2)

    def move(self, keys):
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.left > 0:
            self.rect.x -= self.speed
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.rect.top > 0:
            self.rect.y -= self.speed
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

    def update_shield(self):
        if self.shield and pygame.time.get_ticks() > self.shield_timer:
            self.break_shield()

    def break_shield(self):
        self.shield = False


class Asteroid:
    def __init__(self):
        edge = random.choice(["top", "bottom", "left", "right"])
        if edge == "top":
            self.rect = asteroid_image.get_rect(center=(random.randint(0, WIDTH), 0))
        elif edge == "bottom":
            self.rect = asteroid_image.get_rect(
                center=(random.randint(0, WIDTH), HEIGHT)
            )
        elif edge == "left":
            self.rect = asteroid_image.get_rect(center=(0, random.randint(0, HEIGHT)))
        else:  # right
            self.rect = asteroid_image.get_rect(
                center=(WIDTH, random.randint(0, HEIGHT))
            )

        self.scale_factor = 1.0
        self.rotation_angle = random.randint(0, 360)
        self.original_image = asteroid_image

        self.image = pygame.transform.rotate(self.original_image, self.rotation_angle)
        target_x = random.randint(0, WIDTH)
        target_y = random.randint(0, HEIGHT)
        self.direction = pygame.math.Vector2(
            target_x - self.rect.centerx, target_y - self.rect.centery
        )
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()

    def update(self):
        self.rect.x += self.direction.x * ASTEROID_SPEED
        self.rect.y += self.direction.y * ASTEROID_SPEED

        self.scale_factor += 0.002
        scaled_size = int(50 * self.scale_factor)
        self.image = pygame.transform.scale(
            self.original_image, (scaled_size, scaled_size)
        )
        self.rect = self.image.get_rect(center=self.rect.center)

    def draw(self, surface):
        angle = -self.direction.angle_to(pygame.math.Vector2(1, 0)) + 180
        rotated_image = pygame.transform.rotate(self.image, angle)
        new_rect = rotated_image.get_rect(center=self.rect.center)
        surface.blit(rotated_image, new_rect)

    def is_off_screen(self):
        return (
            self.rect.right < 0
            or self.rect.left > WIDTH
            or self.rect.bottom < 0
            or self.rect.top > HEIGHT
        )


class Crystal:
    def __init__(self):
        self.image = crystal_image
        self.rect = self.image.get_rect(
            center=(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
        )

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class PowerUp:
    def __init__(self, power_type):
        self.type = power_type
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        self.color = GREEN if self.type == "speed" else BLUE
        pygame.draw.circle(self.image, self.color, (15, 15), 15)
        self.rect = self.image.get_rect(
            center=(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
        )

    def draw(self, surface):
        surface.blit(self.image, self.rect)


def draw_game_elements(screen, asteroids, crystals, power_ups):
    for asteroid in asteroids:
        asteroid.draw(screen)
    for power_up in power_ups:
        power_up.draw(screen)
    for crystal in crystals:
        crystal.draw(screen)


def draw_game_info(screen, spaceship, score, level):
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {spaceship.lives}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 50))
    screen.blit(level_text, (10, 90))

    pygame.draw.rect(screen, RED, (10, 120, 100, 10))
    pygame.draw.rect(screen, GREEN, (10, 120, 100 * (spaceship.lives / 3), 10))


def draw_starfield(screen, stars):
    for i in range(len(stars)):
        stars[i] = (stars[i][0], stars[i][1] + 1)
        if stars[i][1] > HEIGHT:
            stars[i] = (random.randint(0, WIDTH), 0)
        pygame.draw.circle(screen, WHITE, stars[i], 1)


def handle_events(spaceship):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.USEREVENT + 1:
            spaceship.speed = SPACESHIP_SPEED
    return True


def initialize_game():
    global spaceship, asteroids, crystals, power_ups, score, level, clock, stars
    spaceship = Spaceship()
    asteroids = []
    crystals = [Crystal() for _ in range(5)]
    power_ups = []
    score = 0
    level = 1
    clock = pygame.time.Clock()
    stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(100)]
    background_music.play(loops=-1)


def update_game():
    global level, ASTEROID_SPEED, score
    keys = pygame.key.get_pressed()
    spaceship.move(keys)

    if random.randint(1, max(50 - level * 2, 10)) == 1:
        asteroids.append(Asteroid())

    if random.randint(1, 500) == 1:
        power_ups.append(PowerUp(random.choice(["speed", "shield"])))

    for asteroid in asteroids[:]:
        asteroid.update()
        if asteroid.rect.colliderect(spaceship.rect):
            if spaceship.shield:
                asteroids.remove(asteroid)
                spaceship.break_shield()
            else:
                clash_sound.play()
                asteroids.remove(asteroid)
                spaceship.lives -= 1
                if spaceship.lives == 0:
                    return False
        elif asteroid.is_off_screen():
            asteroids.remove(asteroid)

    for power_up in power_ups[:]:
        if power_up.rect.colliderect(spaceship.rect):
            if power_up.type == "speed":
                spaceship.speed = 10
                pygame.time.set_timer(pygame.USEREVENT + 1, 5000)
            elif power_up.type == "shield":
                spaceship.shield = True
                spaceship.shield_timer = pygame.time.get_ticks() + 5000
            power_ups.remove(power_up)

    spaceship.update_shield()

    for crystal in crystals[:]:
        if crystal.rect.colliderect(spaceship.rect):
            score += 1
            crystals.remove(crystal)
            crystals.append(Crystal())

    if score > level * 10:
        level += 1
        ASTEROID_SPEED += 0.5

    return True


initialize_game()

running = True
while running:
    screen.fill(SPACE_BLUE)
    draw_starfield(screen, stars)
    running = handle_events(spaceship)
    if not running:
        break
    running = update_game()
    if not running:
        break
    spaceship.draw(screen)
    draw_game_elements(screen, asteroids, crystals, power_ups)
    draw_game_info(screen, spaceship, score, level)
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
