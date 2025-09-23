import pygame
import sys
import random
import os

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400

# Colors
SKY_BLUE = (107, 140, 255)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
GREEN = (0, 128, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Mario PC Port")

# Disable maximize button (this is OS-dependent and may not work on all systems)
pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)

# Clock for controlling FPS
clock = pygame.time.Clock()
FPS = 60

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
LEVEL_COMPLETE = 3
BOSS_FIGHT = 4

# Current game state
game_state = MENU

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = SCREEN_HEIGHT - 100
        self.velocity_y = 0
        self.velocity_x = 0
        self.jumping = False
        self.on_ground = False
        self.direction = 1  # 1 for right, -1 for left
        self.lives = 3
        self.score = 0
        
    def update(self, platforms):
        # Apply gravity
        self.velocity_y += 0.5
        if self.velocity_y > 10:
            self.velocity_y = 10
            
        # Update position
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
        # Check for collisions with platforms
        self.on_ground = False
        for platform in platforms:
            if pygame.sprite.collide_rect(self, platform):
                # Collision from top
                if self.velocity_y > 0 and self.rect.bottom > platform.rect.top and self.rect.top < platform.rect.top:
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                    self.jumping = False
                # Collision from bottom
                elif self.velocity_y < 0 and self.rect.top < platform.rect.bottom and self.rect.bottom > platform.rect.bottom:
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0
                # Collision from sides
                elif self.velocity_x > 0 and self.rect.right > platform.rect.left and self.rect.left < platform.rect.left:
                    self.rect.right = platform.rect.left
                elif self.velocity_x < 0 and self.rect.left < platform.rect.right and self.rect.right > platform.rect.right:
                    self.rect.left = platform.rect.right
        
        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity_y = 0
            self.on_ground = True
            self.jumping = False
            
    def jump(self):
        if self.on_ground and not self.jumping:
            self.velocity_y = -12
            self.jumping = True
            self.on_ground = False
            
    def move_left(self):
        self.velocity_x = -5
        self.direction = -1
        
    def move_right(self):
        self.velocity_x = 5
        self.direction = 1
        
    def stop(self):
        self.velocity_x = 0

# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=BROWN):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type="goomba"):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        if enemy_type == "goomba":
            self.image.fill(BROWN)
        elif enemy_type == "koopa":
            self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity_x = -2
        self.enemy_type = enemy_type
        self.direction = -1  # Start moving left
        
    def update(self, platforms):
        self.rect.x += self.velocity_x
        
        # Change direction if hitting a wall or at edge
        on_platform = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_x > 0 and self.rect.right > platform.rect.left and self.rect.left < platform.rect.left:
                    self.velocity_x = -2
                elif self.velocity_x < 0 and self.rect.left < platform.rect.right and self.rect.right > platform.rect.right:
                    self.velocity_x = 2
                    
                # Check if on platform
                if self.rect.bottom == platform.rect.top:
                    on_platform = True
                    
        # If not on a platform, turn around
        if not on_platform and self.rect.bottom < SCREEN_HEIGHT:
            self.velocity_x *= -1

# Boss class
class Boss(pygame.sprite.Sprite):
    def __init__(self, boss_type):
        super().__init__()
        self.image = pygame.Surface((60, 60))
        
        # Different colors for different bosses
        if boss_type == "bowser":
            self.image.fill(RED)
        elif boss_type == "king_boo":
            self.image.fill(WHITE)
        elif boss_type == "petey_piranha":
            self.image.fill(GREEN)
            
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH - 100
        self.rect.y = SCREEN_HEIGHT - 150
        self.velocity_x = 3
        self.velocity_y = 0
        self.health = 3
        self.boss_type = boss_type
        self.attack_timer = 0
        self.projectiles = pygame.sprite.Group()
        
    def update(self, platforms):
        # Simple boss movement pattern
        self.rect.x += self.velocity_x
        
        if self.rect.left < SCREEN_WIDTH // 2:
            self.velocity_x = 3
        elif self.rect.right > SCREEN_WIDTH - 50:
            self.velocity_x = -3
            
        # Attack pattern
        self.attack_timer += 1
        if self.attack_timer > 120:  # Attack every 2 seconds
            self.attack()
            self.attack_timer = 0
            
        # Update projectiles
        self.projectiles.update()
        
    def attack(self):
        # Different attacks based on boss type
        if self.boss_type == "bowser":
            # Bowser shoots fireballs
            fireball = Projectile(self.rect.centerx, self.rect.centery, -5, 0, RED)
            self.projectiles.add(fireball)
        elif self.boss_type == "king_boo":
            # King Boo shoots ghostly projectiles
            ghost = Projectile(self.rect.centerx, self.rect.centery, -3, random.randint(-2, 2), WHITE)
            self.projectiles.add(ghost)
        elif self.boss_type == "petey_piranha":
            # Petey Piranha shoots seeds
            seed = Projectile(self.rect.centerx, self.rect.centery, -4, 0, GREEN)
            self.projectiles.add(seed)

# Projectile class for boss attacks
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, velocity_x, velocity_y, color):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        
    def update(self):
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
        # Remove if off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.top > SCREEN_HEIGHT or self.rect.bottom < 0:
            self.kill()

# Coin class
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((15, 15))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Flag pole for level completion
class FlagPole(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 100))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Create game objects
player = Player()
platforms = pygame.sprite.Group()
enemies = pygame.sprite.Group()
coins = pygame.sprite.Group()
flag_pole = None
boss = None

# Level variables
current_world = 1
current_level = 1
level_complete = False

# Font for text
font = pygame.font.SysFont(None, 36)

# Function to generate a level
def generate_level(world, level):
    global platforms, enemies, coins, flag_pole, boss
    
    # Clear existing objects
    platforms.empty()
    enemies.empty()
    coins.empty()
    flag_pole = None
    boss = None
    
    # Ground platform
    platforms.add(Platform(0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20))
    
    # Different level layouts based on world and level
    if level == 5:  # Castle level with boss
        # Castle platforms
        platforms.add(Platform(100, SCREEN_HEIGHT - 100, 200, 20))
        platforms.add(Platform(400, SCREEN_HEIGHT - 150, 150, 20))
        
        # Create boss based on world
        boss_types = ["bowser", "king_boo", "petey_piranha", "bowser", "king_boo", "petey_piranha"]
        boss = Boss(boss_types[world-1])
        
    else:  # Regular level
        # Generate random platforms
        for i in range(10):
            x = random.randint(50, SCREEN_WIDTH - 100)
            y = random.randint(100, SCREEN_HEIGHT - 100)
            width = random.randint(50, 150)
            platforms.add(Platform(x, y, width, 20))
            
        # Generate enemies
        for i in range(5):
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = SCREEN_HEIGHT - 50
            enemy_type = random.choice(["goomba", "koopa"])
            enemies.add(Enemy(x, y, enemy_type))
            
        # Generate coins
        for i in range(10):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 100)
            coins.add(Coin(x, y))
            
        # Add flag pole at the end
        flag_pole = FlagPole(SCREEN_WIDTH - 50, SCREEN_HEIGHT - 120)
        
    # Reset player position
    player.rect.x = 50
    player.rect.y = SCREEN_HEIGHT - 100
    player.velocity_x = 0
    player.velocity_y = 0

# Generate the first level
generate_level(current_world, current_level)

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if game_state == MENU:
                if event.key == pygame.K_RETURN:
                    game_state = PLAYING
                    generate_level(current_world, current_level)
                    
            elif game_state == PLAYING or game_state == BOSS_FIGHT:
                if event.key == pygame.K_SPACE:
                    player.jump()
                if event.key == pygame.K_ESCAPE:
                    game_state = MENU
                    
            elif game_state == GAME_OVER or game_state == LEVEL_COMPLETE:
                if event.key == pygame.K_RETURN:
                    if game_state == GAME_OVER:
                        player.lives = 3
                        player.score = 0
                        current_world = 1
                        current_level = 1
                    game_state = PLAYING
                    generate_level(current_world, current_level)
    
    # Get pressed keys for continuous movement
    keys = pygame.key.get_pressed()
    if game_state == PLAYING or game_state == BOSS_FIGHT:
        if keys[pygame.K_LEFT]:
            player.move_left()
        elif keys[pygame.K_RIGHT]:
            player.move_right()
        else:
            player.stop()
    
    # Update game objects based on game state
    if game_state == PLAYING:
        player.update(platforms)
        enemies.update(platforms)
        
        # Check for coin collisions
        coin_collisions = pygame.sprite.spritecollide(player, coins, True)
        for coin in coin_collisions:
            player.score += 100
            
        # Check for enemy collisions
        enemy_collisions = pygame.sprite.spritecollide(player, enemies, False)
        for enemy in enemy_collisions:
            # If player is falling on enemy
            if player.velocity_y > 0 and player.rect.bottom < enemy.rect.centery:
                enemy.kill()
                player.score += 200
                player.velocity_y = -5  # Bounce
            else:
                player.lives -= 1
                if player.lives <= 0:
                    game_state = GAME_OVER
                else:
                    # Reset player position
                    player.rect.x = 50
                    player.rect.y = SCREEN_HEIGHT - 100
                    player.velocity_x = 0
                    player.velocity_y = 0
        
        # Check for flag pole collision (level complete)
        if flag_pole and pygame.sprite.collide_rect(player, flag_pole):
            game_state = LEVEL_COMPLETE
            current_level += 1
            if current_level > 5:
                current_level = 1
                current_world += 1
                if current_world > 6:
                    current_world = 1  # Loop back to world 1 after completing all worlds
            
        # Check if player reached the boss area
        if current_level == 5 and player.rect.x > SCREEN_WIDTH - 200:
            game_state = BOSS_FIGHT
            
    elif game_state == BOSS_FIGHT:
        player.update(platforms)
        if boss:
            boss.update(platforms)
            
            # Check for boss projectile collisions with player
            projectile_collisions = pygame.sprite.spritecollide(player, boss.projectiles, True)
            for projectile in projectile_collisions:
                player.lives -= 1
                if player.lives <= 0:
                    game_state = GAME_OVER
                else:
                    # Reset player position
                    player.rect.x = 50
                    player.rect.y = SCREEN_HEIGHT - 100
                    player.velocity_x = 0
                    player.velocity_y = 0
            
            # Check if player jumps on boss
            if pygame.sprite.collide_rect(player, boss):
                if player.velocity_y > 0 and player.rect.bottom < boss.rect.centery:
                    boss.health -= 1
                    player.velocity_y = -10  # Bounce higher
                    if boss.health <= 0:
                        boss.kill()
                        player.score += 1000
                        game_state = LEVEL_COMPLETE
                        current_level += 1
                        if current_level > 5:
                            current_level = 1
                            current_world += 1
                            if current_world > 6:
                                current_world = 1  # Loop back to world 1 after completing all worlds
                else:
                    player.lives -= 1
                    if player.lives <= 0:
                        game_state = GAME_OVER
                    else:
                        # Reset player position
                        player.rect.x = 50
                        player.rect.y = SCREEN_HEIGHT - 100
                        player.velocity_x = 0
                        player.velocity_y = 0
    
    # Draw everything
    screen.fill(SKY_BLUE)
    
    if game_state == MENU:
        # Draw menu
        title_text = font.render("SUPER MARIO PC PORT", True, RED)
        instruction_text = font.render("Press ENTER to Start", True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))
        screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, 200))
        
    elif game_state == PLAYING or game_state == BOSS_FIGHT:
        # Draw platforms
        platforms.draw(screen)
        
        # Draw coins
        coins.draw(screen)
        
        # Draw flag pole if it exists
        if flag_pole:
            screen.blit(flag_pole.image, flag_pole.rect)
        
        # Draw enemies
        enemies.draw(screen)
        
        # Draw player
        screen.blit(player.image, player.rect)
        
        # Draw boss if in boss fight
        if game_state == BOSS_FIGHT and boss:
            screen.blit(boss.image, boss.rect)
            boss.projectiles.draw(screen)
            
            # Draw boss health
            health_text = font.render(f"BOSS HP: {boss.health}", True, RED)
            screen.blit(health_text, (SCREEN_WIDTH - 150, 20))
        
        # Draw HUD
        lives_text = font.render(f"Lives: {player.lives}", True, WHITE)
        score_text = font.render(f"Score: {player.score}", True, WHITE)
        world_text = font.render(f"World {current_world}-{current_level}", True, WHITE)
        screen.blit(lives_text, (10, 10))
        screen.blit(score_text, (10, 50))
        screen.blit(world_text, (SCREEN_WIDTH - 100, 10))
        
    elif game_state == LEVEL_COMPLETE:
        # Draw level complete screen
        complete_text = font.render("LEVEL COMPLETE!", True, GREEN)
        next_text = font.render(f"Next: World {current_world}-{current_level}", True, WHITE)
        instruction_text = font.render("Press ENTER to Continue", True, WHITE)
        screen.blit(complete_text, (SCREEN_WIDTH // 2 - complete_text.get_width() // 2, 100))
        screen.blit(next_text, (SCREEN_WIDTH // 2 - next_text.get_width() // 2, 150))
        screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, 200))
        
    elif game_state == GAME_OVER:
        # Draw game over screen
        game_over_text = font.render("GAME OVER", True, RED)
        score_text = font.render(f"Final Score: {player.score}", True, WHITE)
        instruction_text = font.render("Press ENTER to Restart", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 100))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 150))
        screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, 200))
    
    # Update the display
    pygame.display.flip()
    
    # Control the frame rate
    clock.tick(FPS)

# Quit pygame
pygame.quit()
sys.exit()
