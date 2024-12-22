import pygame
import random
import os

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60
SPACESHIP_SPEED = 5
ASTEROID_SPEED = 2

SPACE_BLUE = (10, 10, 50)

ASSETS_DIR = "Labs/assets"
SPACESHIP_IMG = os.path.join(ASSETS_DIR, "spaceship.png")
ASTEROID_IMG = os.path.join(ASSETS_DIR, "asteroid.png")
CRYSTAL_IMG = os.path.join(ASSETS_DIR, "energy_crystal.png")
BACKGROUND_MUSIC = os.path.join(ASSETS_DIR, "background_music.wav")
CLASH_SOUND = os.path.join(ASSETS_DIR, "clash_sound.wav")

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

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def move(self, keys):
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.left > 0:
            self.rect.x -= SPACESHIP_SPEED
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.right < WIDTH:
            self.rect.x += SPACESHIP_SPEED
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.rect.top > 0:
            self.rect.y -= SPACESHIP_SPEED
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.rect.bottom < HEIGHT:
            self.rect.y += SPACESHIP_SPEED


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

        self.image = pygame.transform.rotate(asteroid_image, random.randint(0, 360))
        target_x = random.randint(0, WIDTH)
        target_y = random.randint(0, HEIGHT)
        self.direction = pygame.math.Vector2(
            target_x - self.rect.centerx, target_y - self.rect.centery
        ).normalize()

    def update(self):
        self.rect.x += self.direction.x * ASTEROID_SPEED
        self.rect.y += self.direction.y * ASTEROID_SPEED

    def draw(self, surface):
        angle = -self.direction.angle_to(pygame.math.Vector2(1, 0)) - 135
        rotated_image = pygame.transform.rotate(self.image, angle)
        new_rect = rotated_image.get_rect(center=self.rect.center)
        surface.blit(rotated_image, new_rect)


class Crystal:
    def __init__(self):
        self.image = crystal_image
        self.rect = self.image.get_rect(
            center=(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
        )

    def draw(self, surface):
        surface.blit(self.image, self.rect)


spaceship = Spaceship()
asteroids = []
crystals = [Crystal() for _ in range(5)]
score = 0
clock = pygame.time.Clock()

background_music.play(loops=-1)

# Generate starfield, for the background
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(100)]

running = True
while running:
    screen.fill(SPACE_BLUE)

    # Draw stars
    for star in stars:
        pygame.draw.circle(screen, (255, 255, 255), star, 1)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    spaceship.move(keys)

    # Spawn asteroids
    if random.randint(1, 50) == 1:
        asteroids.append(Asteroid())

    # Update asteroids and check collisions
    for asteroid in asteroids[:]:
        asteroid.update()
        if asteroid.rect.colliderect(spaceship.rect):
            clash_sound.play()
            asteroids.remove(asteroid)
            spaceship.lives -= 1
            if spaceship.lives == 0:
                running = False  # Game over

    # Draw and collect crystals
    for crystal in crystals[:]:
        if crystal.rect.colliderect(spaceship.rect):
            score += 1
            crystals.remove(crystal)
            crystals.append(Crystal())

    spaceship.draw(screen)

    for asteroid in asteroids:
        asteroid.draw(screen)

    for crystal in crystals:
        crystal.draw(screen)

    # Display score and lives
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    lives_text = font.render(f"Lives: {spaceship.lives}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 50))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
