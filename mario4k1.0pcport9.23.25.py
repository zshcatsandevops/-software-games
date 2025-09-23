import pygame, sys

# ========================
# Initialization
# ========================
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ultra Mario 2D Bros v0.x 1.0 - SMB1 Engine")
clock = pygame.time.Clock()
FPS = 60

# ========================
# Constants
# ========================
MENU, PLAYING, LEVEL_COMPLETE, HOWTO = 0, 1, 2, 3
SKY_BLUE = (107, 140, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
YELLOW = (255, 200, 0)
SKIN = (255, 220, 177)

# Fonts
title_font = pygame.font.SysFont("Arial", 48, bold=True)
menu_font = pygame.font.SysFont("Arial", 28, bold=True)

# ========================
# NES Mario sprite
# ========================
def create_mario():
    surf = pygame.Surface((16, 16), pygame.SRCALPHA)
    pygame.draw.rect(surf, RED, (4, 0, 8, 3))
    pygame.draw.rect(surf, RED, (3, 1, 10, 2))
    pygame.draw.rect(surf, SKIN, (5, 3, 6, 5))
    pygame.draw.rect(surf, BLACK, (6, 4, 1, 1))
    pygame.draw.rect(surf, BLACK, (9, 4, 1, 1))
    pygame.draw.rect(surf, BLUE, (4, 8, 8, 5))
    pygame.draw.rect(surf, RED, (3, 8, 2, 3))
    pygame.draw.rect(surf, RED, (11, 8, 2, 3))
    pygame.draw.rect(surf, BLUE, (4, 13, 3, 3))
    pygame.draw.rect(surf, BLUE, (9, 13, 3, 3))
    pygame.draw.rect(surf, BROWN, (4, 15, 3, 1))
    pygame.draw.rect(surf, BROWN, (9, 15, 3, 1))
    return surf

# ========================
# Entities
# ========================
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = create_mario()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_y = 0
        self.on_ground = False

    def update(self, keys, platforms):
        dx, dy = 0, 0
        speed = 3
        if keys[pygame.K_LEFT]:
            dx = -speed
        if keys[pygame.K_RIGHT]:
            dx = speed

        # gravity
        self.vel_y += 0.5
        if self.vel_y > 6:
            self.vel_y = 6
        dy += self.vel_y

        # collisions
        self.on_ground = False
        self.rect.x += dx
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if dx > 0: self.rect.right = p.rect.left
                if dx < 0: self.rect.left = p.rect.right
        self.rect.y += dy
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if dy > 0:
                    self.rect.bottom = p.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                if dy < 0:
                    self.rect.top = p.rect.bottom
                    self.vel_y = 0

    def jump(self):
        if self.on_ground:
            self.vel_y = -10
            self.on_ground = False

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect(topleft=(x, y))

# ========================
# Game Functions
# ========================
def run_game():
    player = Player(50, SCREEN_HEIGHT-100)
    platforms = [Platform(0, SCREEN_HEIGHT-40, SCREEN_WIDTH, 40)]

    running = True
    while running:
        dt = clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return MENU
                elif e.key == pygame.K_z:   # Z jump trigger
                    player.jump()

        # update
        player.update(keys, platforms)

        # draw
        screen.fill(SKY_BLUE)
        for p in platforms: screen.blit(p.image, p.rect)
        screen.blit(player.image, player.rect)
        pygame.display.flip()

def main():
    run_game()

if __name__ == "__main__":
    main()
