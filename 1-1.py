import pygame, sys

# ========================
# Initialization
# ========================
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ultra Mario 2D Bros v0.x 1.0 - SMB1 1-1 (Pygame)")
clock = pygame.time.Clock()
FPS = 60

# ========================
# Constants
# ========================
TILE = 16
MENU, PLAYING, LEVEL_COMPLETE, HOWTO, DEAD = 0, 1, 2, 3, 4
SKY_BLUE = (107, 140, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
YELLOW = (255, 200, 0)
SKIN = (255, 220, 177)
GREEN = (40, 170, 40)
GRAY = (160, 160, 160)
GROUND_TOP = SCREEN_HEIGHT - TILE*2

# Fonts
title_font = pygame.font.SysFont("Arial", 36, bold=True)
menu_font = pygame.font.SysFont("Arial", 20, bold=True)

def make_surface(w, h, color, border=True):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.fill(color)
    if border:
        pygame.draw.rect(surf, BLACK, (0,0,w-1,h-1), 1)
    return surf

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

def create_goomba_surface():
    surf = pygame.Surface((16, 16), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, BROWN, (1, 5, 14, 10))
    pygame.draw.rect(surf, BROWN, (2, 10, 12, 6))
    pygame.draw.circle(surf, BLACK, (6, 9), 1)
    pygame.draw.circle(surf, BLACK, (10, 9), 1)
    pygame.draw.rect(surf, BLACK, (5, 13, 2, 2))
    pygame.draw.rect(surf, BLACK, (9, 13, 2, 2))
    return surf

# ========================
# Entities
# ========================
class Entity(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = None
        self.rect = pygame.Rect(0,0,0,0)

class Solid(Entity):
    def __init__(self, x, y, w, h, color=BROWN):
        super().__init__()
        self.image = make_surface(w, h, color)
        self.rect = self.image.get_rect(topleft=(x, y))

class Block(Solid):
    def __init__(self, x, y, kind='brick'):
        color = (185, 70, 20) if kind == 'brick' else YELLOW
        super().__init__(x, y, TILE, TILE, color)
        self.kind = kind
        self.used = False if kind == 'question' else None
        self.bump_timer = 0

    def on_head_hit(self, player):
        self.bump_timer = 6
        if self.kind == 'question' and not self.used:
            self.used = True

    def update(self):
        if self.bump_timer > 0:
            self.bump_timer -= 1

    def draw(self, surface, camera_x=0):
        offset_y = -2 if self.bump_timer > 0 else 0
        img = self.image.copy()
        if self.kind == 'question':
            pygame.draw.rect(img, YELLOW if not self.used else GRAY, (0,0,TILE-1,TILE-1))
            pygame.draw.rect(img, BLACK, (0,0,TILE-1,TILE-1), 1)
            if not self.used:
                pygame.draw.circle(img, BLACK, (8, 6), 2)
                pygame.draw.rect(img, BLACK, (7, 9, 2, 4))
        elif self.kind == 'brick':
            pygame.draw.rect(img, (180,80,40), (0,0,TILE-1,TILE-1))
            pygame.draw.rect(img, BLACK, (0,0,TILE-1,TILE-1), 1)
        surface.blit(img, (self.rect.x - camera_x, self.rect.y + offset_y))

class Pipe(Solid):
    def __init__(self, tile_x, height_tiles):
        x = tile_x * TILE
        top_y = GROUND_TOP - height_tiles * TILE
        super().__init__(x, top_y, TILE*2, height_tiles*TILE, GREEN)

class Flagpole(Entity):
    def __init__(self, x):
        super().__init__()
        self.image = pygame.Surface((3, TILE*10), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (235,235,235), (0,0,3,TILE*10))
        pygame.draw.circle(self.image, (235,235,235), (1, 3), 3)
        self.rect = self.image.get_rect(bottomleft=(x, GROUND_TOP))

class Goomba(Entity):
    def __init__(self, x, y):
        super().__init__()
        self.image = create_goomba_surface()
        self.rect = self.image.get_rect(topleft=(x,y))
        self.vx = -1
        self.alive = True
        self.squash_timer = 0

    def update(self, solids):
        if not self.alive:
            self.squash_timer -= 1
            return
        self.rect.y += 4
        for s in solids:
            if self.rect.colliderect(s.rect):
                self.rect.bottom = s.rect.top
                break
        self.rect.x += self.vx
        for s in solids:
            if self.rect.colliderect(s.rect):
                if self.vx > 0: self.rect.right = s.rect.left
                else: self.rect.left = s.rect.right
                self.vx *= -1
                break

    def stomp(self):
        self.alive = False
        self.squash_timer = FPS // 2
        self.image = pygame.transform.scale(self.image, (16, 8))
        self.rect = self.image.get_rect(midbottom=self.rect.midbottom)

    def draw(self, surface, camera_x=0):
        if self.alive or self.squash_timer > 0:
            surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))

# ========================
# Player
# ========================
class Player(Entity):
    def __init__(self, x, y):
        super().__init__()
        self.image = create_mario()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.spawn = pygame.Vector2(x, y)

    def update(self, keys, solids, blocks, enemies):
        prev_rect = self.rect.copy()
        accel, max_speed, friction = 0.5, 3.2, 0.85
        if keys[pygame.K_LEFT]: self.vel_x -= accel
        if keys[pygame.K_RIGHT]: self.vel_x += accel
        if not(keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
            self.vel_x *= friction
            if abs(self.vel_x) < 0.05: self.vel_x = 0
        self.vel_x = max(-max_speed, min(max_speed, self.vel_x))
        self.rect.x += int(self.vel_x)
        for s in solids:
            if self.rect.colliderect(s.rect):
                if self.vel_x > 0: self.rect.right = s.rect.left
                elif self.vel_x < 0: self.rect.left = s.rect.right
                self.vel_x = 0
        self.vel_y += 0.5
        if self.vel_y > 8: self.vel_y = 8
        dy = int(self.vel_y)
        self.on_ground = False
        self.rect.y += dy
        for s in solids:
            if self.rect.colliderect(s.rect):
                if dy > 0:
                    self.rect.bottom = s.rect.top; self.vel_y = 0; self.on_ground = True
                elif dy < 0:
                    self.rect.top = s.rect.bottom; self.vel_y = 0
                    if isinstance(s, Block): s.on_head_hit(self)
        for e in enemies:
            if not getattr(e, 'alive', True) and e.squash_timer <= 0: continue
            if self.rect.colliderect(e.rect):
                if dy > 0 and prev_rect.bottom <= e.rect.top:
                    e.stomp(); self.vel_y = -6
                else: return DEAD
        return PLAYING

    def jump(self):
        if self.on_ground:
            self.vel_y = -9.5; self.on_ground = False

    def reset(self):
        self.rect.topleft = (int(self.spawn.x), int(self.spawn.y))
        self.vel_x = self.vel_y = 0

# ========================
# Level
# ========================
class Level:
    def __init__(self):
        self.solids, self.blocks, self.enemies = [], [], []
        self.flag = None
        self.length_px = 0

    def add_block(self, block):
        self.blocks.append(block); self.solids.append(block)

    def add_solid(self, solid): self.solids.append(solid)
    def add_enemy(self, e): self.enemies.append(e)
    def all_solids(self): return self.solids

    def draw(self, surface, camera_x):
        for s in self.solids:
            if isinstance(s, Block): s.draw(surface, camera_x)
            else: surface.blit(s.image, (s.rect.x - camera_x, s.rect.y))
        for e in self.enemies: e.draw(surface, camera_x)
        if self.flag: surface.blit(self.flag.image, (self.flag.rect.x - camera_x, self.flag.rect.y))

def build_level_1_1():
    lvl = Level(); W = 240; lvl.length_px = W*TILE
    def add_ground(tx, length):
        x = tx*TILE; w = length*TILE
        lvl.add_solid(Solid(x, GROUND_TOP, w, TILE*2, (222,160,92)))
    for tx, length in [(0, 40), (43, 30), (76, 30), (110, 20),
                       (135, 20), (160, 30), (195, 45)]: add_ground(tx, length)
    def place_block(tx, ty, kind='brick'): lvl.add_block(Block(tx*TILE, ty*TILE, kind))
    base_ty = (GROUND_TOP//TILE) - 5
    place_block(22, base_ty, 'brick'); place_block(23, base_ty, 'question')
    place_block(24, base_ty, 'brick'); place_block(23, base_ty-1, 'question')
    for tx,h in [(50,2),(58,3),(66,4),(74,4),(102,2),(140,3),(172,2)]:
        lvl.add_solid(Pipe(tx,h))
    for t in range(104, 110): place_block(t, base_ty, 'brick')
    place_block(109, base_ty-1, 'question')
    def stairs(start_tx, height, ascending=True):
        for i in range(height):
            tx = start_tx+i if ascending else start_tx+(height-1-i)
            lvl.add_solid(Solid(tx*TILE, GROUND_TOP-(i+1)*TILE, TILE, (i+1)*TILE, (222,160,92)))
    stairs(180, 5, True); stairs(190, 5, False)
    lvl.flag = Flagpole(lvl.length_px - TILE*6)
    for x,y in [(35*TILE, GROUND_TOP-TILE),(60*TILE,GROUND_TOP-TILE),
                (108*TILE,GROUND_TOP-TILE),(170*TILE,GROUND_TOP-TILE)]:
        lvl.add_enemy(Goomba(x,y))
    return lvl

# ========================
# Helpers
# ========================
def clamp(n, minn, maxn): return max(minn, min(n, maxn))

# ========================
# Game loop
# ========================
def run_game():
    level = build_level_1_1()
    player = Player(32, GROUND_TOP - TILE)
    camera_x, state, time_left, HUD_timer = 0, MENU, 400, 0
    running = True
    while running:
        dt = clock.tick(FPS)/1000.0; keys = pygame.key.get_pressed()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            elif e.type==pygame.KEYDOWN:
                if e.key==pygame.K_ESCAPE: pygame.quit(); sys.exit()
                elif state==PLAYING:
                    if e.key==pygame.K_SPACE: player.jump()
                    elif e.key==pygame.K_r:
                        level=build_level_1_1(); player.reset()
                        camera_x,state,time_left=0,PLAYING,400
                elif state==MENU:
                    if e.key==pygame.K_RETURN: state=PLAYING
                    elif e.key==pygame.K_h: state=HOWTO
                elif state==HOWTO:
                    if e.key==pygame.K_RETURN: state=MENU
                elif state in (DEAD,LEVEL_COMPLETE):
                    if e.key==pygame.K_RETURN:
                        level=build_level_1_1(); player.reset()
                        camera_x,state,time_left=0,PLAYING,400
        screen.fill(SKY_BLUE)
        if state==MENU:
            title=title_font.render("Ultra Mario 2D Bros",True,WHITE)
            screen.blit(title,(SCREEN_WIDTH//2-title.get_width()//2,100))
            opt1=menu_font.render("Press ENTER to Start",True,WHITE)
            opt2=menu_font.render("Press H for How To Play",True,WHITE)
            screen.blit(opt1,(SCREEN_WIDTH//2-opt1.get_width()//2,300))
            screen.blit(opt2,(SCREEN_WIDTH//2-opt2.get_width()//2,340))
        elif state==HOWTO:
            lines=["HOW TO PLAY","---------------------------",
                   "Arrow Keys: Move left/right","SPACE: Jump","R: Reset level",
                   "ESC: Quit","ENTER: Back to Menu"]
            for i,text in enumerate(lines):
                surf=menu_font.render(text,True,WHITE)
                screen.blit(surf,(SCREEN_WIDTH//2-surf.get_width()//2,120+i*30))
        elif state==PLAYING:
            st=player.update(keys,level.all_solids(),level.blocks,level.enemies)
            if st==DEAD: state=DEAD
            for b in level.blocks: b.update()
            for enemy in level.enemies: enemy.update(level.all_solids())
            camera_x=clamp(player.rect.centerx-SCREEN_WIDTH//2,0,level.length_px-SCREEN_WIDTH)
            if player.rect.left<0: player.rect.left=0
            if level.flag and player.rect.colliderect(level.flag.rect): state=LEVEL_COMPLETE
            HUD_timer+=dt
            if HUD_timer>=1.0:
                HUD_timer=0; time_left=max(0,time_left-1)
                if time_left==0: state=DEAD
            pygame.draw.rect(screen,(222,160,92),(0,GROUND_TOP+TILE,SCREEN_WIDTH,SCREEN_HEIGHT-(GROUND_TOP+TILE)))
            level.draw(screen,camera_x)
            screen.blit(player.image,(player.rect.x-camera_x,player.rect.y))
            hud=title_font.render("MARIO   WORLD 1-1    TIME %03d"%time_left,True,WHITE)
            screen.blit(hud,(20,10))
        elif state==DEAD:
            txt=title_font.render("YOU DIED  -  Press ENTER",True,WHITE)
            screen.blit(txt,(SCREEN_WIDTH//2-txt.get_width()//2,SCREEN_HEIGHT//3))
        elif state==LEVEL_COMPLETE:
            txt=title_font.render("COURSE CLEAR!  -  Press ENTER",True,WHITE)
            screen.blit(txt,(SCREEN_WIDTH//2-txt.get_width()//2,SCREEN_HEIGHT//3))
        pygame.display.flip()

def main(): run_game()
if __name__=="__main__": main()
