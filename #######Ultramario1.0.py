#!/usr/bin/env python3.13
"""
Ultra Mario 3D Bros PC Port - A Non-Copyrighted 3D Platformer
Inspired by classic 3D platformers but with original content
Built with Ursina Engine
"""

from ursina import *
import math, random

# Initialize Ursina
app = Ursina()

# Game Configuration
window.title = 'Ultra Mario 3D Bros PC Port'
window.borderless = False
window.fullscreen = False
window.exit_button.visible = False
window.fps_counter.enabled = True

# Sky and lighting
Sky(color=color.rgb(135, 206, 235))
scene.fog_color = color.rgb(135, 206, 235)
scene.fog_density = 0.02
light = DirectionalLight()
light.look_at(Vec3(1, -1, -1))


# -------------------------------------------------
# Main Menu
# -------------------------------------------------
class MainMenu(Entity):
    def __init__(self):
        super().__init__(parent=camera.ui)

        self.bg = Entity(parent=self, model='quad', color=color.dark_gray, scale=(2, 1.5), z=1)

        self.title = Text("Ultra Mario 3D Bros PC Port",
                          parent=self, y=0.3, x=0,
                          origin=(0, 0), scale=3, color=color.azure)

        self.start_button = Button("Start Game",
                                   parent=self, y=0, scale=(0.3, 0.1),
                                   color=color.orange, text_color=color.black,
                                   highlight_color=color.yellow)
        self.quit_button = Button("Quit",
                                  parent=self, y=-0.2, scale=(0.3, 0.1),
                                  color=color.red, text_color=color.white,
                                  highlight_color=color.gray)

        self.start_button.on_click = self.start_game
        self.quit_button.on_click = application.quit

    def start_game(self):
        destroy(self)   # remove menu
        start_game()    # launch main game loop


# -------------------------------------------------
# Player Class
# -------------------------------------------------
class Mario(Entity):
    def __init__(self):
        super().__init__()
        self.model = 'cube'
        self.color = color.red
        self.scale = (1, 2, 1)
        self.position = (0, 5, 0)

        # Movement variables
        self.speed = 8
        self.jump_height = 12
        self.gravity = 30
        self.velocity = Vec3(0, 0, 0)
        self.grounded = False
        self.double_jump_available = True

        # Camera setup
        self.camera_pivot = Entity(parent=self, y=2)
        camera.parent = self.camera_pivot
        camera.position = (0, 1, -10)
        camera.rotation = (0, 0, 0)
        camera.fov = 90
        mouse.locked = True

        # Collision
        self.collider = BoxCollider(self, size=(1, 2, 1))

        # Stats
        self.coins = 0
        self.health = 3
        self.invulnerable_timer = 0

    def update(self):
        # Camera rotation with mouse
        self.rotation_y += mouse.velocity[0] * 40
        self.camera_pivot.rotation_x -= mouse.velocity[1] * 40
        self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -45, 45)

        # Movement input
        movement = Vec3(
            self.forward * (held_keys['w'] - held_keys['s']) +
            self.right * (held_keys['d'] - held_keys['a'])
        ).normalized()

        if movement.length() > 0:
            self.velocity.x = movement.x * self.speed
            self.velocity.z = movement.z * self.speed
        else:
            self.velocity.x = lerp(self.velocity.x, 0, time.dt * 10)
            self.velocity.z = lerp(self.velocity.z, 0, time.dt * 10)

        # Gravity
        if not self.grounded:
            self.velocity.y -= self.gravity * time.dt

        # Jump
        if self.grounded:
            self.double_jump_available = True
            if held_keys['space']:
                self.velocity.y = self.jump_height
                self.grounded = False
        elif self.double_jump_available and held_keys['space']:
            self.velocity.y = self.jump_height * 0.8
            self.double_jump_available = False

        # Apply velocity
        self.position += self.velocity * time.dt

        # Ground check
        hit_info = raycast(self.world_position + Vec3(0, 0.1, 0), Vec3(0, -1, 0), distance=0.2)
        self.grounded = hit_info.hit

        if self.grounded and self.velocity.y < 0:
            self.velocity.y = 0

        # Boundary check
        if self.y < -20:
            self.respawn()

        # Invulnerability flicker
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= time.dt
            self.color = color.rgb(255, 200, 200) if int(self.invulnerable_timer * 10) % 2 else color.red
        else:
            self.color = color.red

    def respawn(self):
        self.position = (0, 5, 0)
        self.velocity = Vec3(0, 0, 0)
        self.health -= 1
        if self.health <= 0:
            self.game_over()

    def game_over(self):
        print("Game Over! Final Score:", self.coins)
        application.quit()

    def collect_coin(self):
        self.coins += 1
        print(f"Coins: {self.coins}")


# -------------------------------------------------
# Collectibles, Enemies, Platforms, Level
# -------------------------------------------------
class MarioCoin(Entity):
    def __init__(self, position=(0, 0, 0)):
        super().__init__(model='sphere', color=color.yellow, scale=0.5,
                         position=position, collider='sphere')
        self.rotation_speed = 100
        self.bob_speed = 2
        self.bob_height = 0.2
        self.start_y = position[1]
        self.time = random.random() * math.pi * 2

    def update(self):
        self.rotation_y += self.rotation_speed * time.dt
        self.time += time.dt
        self.y = self.start_y + math.sin(self.time * self.bob_speed) * self.bob_height

        if distance(self.position, mario.position) < 1.5:
            mario.collect_coin()
            destroy(self)


class Goomba(Entity):
    def __init__(self, position=(0, 0, 0), patrol_points=None):
        super().__init__(model='cube', color=color.green, scale=(1, 1, 1),
                         position=position, collider='box')
        self.patrol_points = patrol_points or [position]
        self.current_patrol_index = 0
        self.speed = 2

    def update(self):
        if len(self.patrol_points) > 1:
            target = self.patrol_points[self.current_patrol_index]
            direction = (Vec3(*target) - self.position).normalized()
            self.position += direction * self.speed * time.dt

            if distance(self.position, target) < 0.5:
                self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)

        if distance(self.position, mario.position) < 1.5:
            if mario.invulnerable_timer <= 0:
                if mario.velocity.y < -2:
                    destroy(self)
                    mario.velocity.y = 10
                else:
                    mario.health -= 1
                    mario.invulnerable_timer = 2
                    print(f"Health: {mario.health}")


class MarioPlatform(Entity):
    def __init__(self, position=(0, 0, 0), end_position=(0, 5, 0), speed=2):
        super().__init__(model='cube', color=color.brown, scale=(3, 0.5, 3),
                         position=position, collider='box')
        self.start_position = position
        self.end_position = end_position
        self.speed = speed
        self.direction = 1
        self.progress = 0

    def update(self):
        self.progress += self.direction * self.speed * time.dt
        if self.progress >= 1:
            self.progress, self.direction = 1, -1
        elif self.progress <= 0:
            self.progress, self.direction = 0, 1
        self.position = lerp(Vec3(*self.start_position), Vec3(*self.end_position), self.progress)


class MarioLevel:
    def __init__(self):
        ground = Entity(model='cube', color=color.gray, scale=(50, 1, 50),
                        position=(0, 0, 0), collider='box')

        # Coins
        self.coins = [MarioCoin(position=(x, 3, 0)) for x in range(10, 50, 10)]

        # Enemies
        self.enemies = [Goomba(position=(15, 1, 0), patrol_points=[(15, 1, 0), (25, 1, 0)])]

        # Goal
        self.goal = Entity(model='cube', color=color.magenta, scale=(1, 5, 1),
                           position=(45, 5, 0), collider='box')


class MarioUI:
    def __init__(self):
        self.coin_text = Text(f'Coins: 0', position=(-0.85, 0.45), scale=2)
        self.health_text = Text(f'Health: 3', position=(-0.85, 0.40), scale=2)


# -------------------------------------------------
# Game Start Wrapper
# -------------------------------------------------
def start_game():
    global mario, level, ui
    mario = Mario()
    level = MarioLevel()
    ui = MarioUI()

    def update_ui():
        ui.coin_text.text = f'Coins: {mario.coins}'
        ui.health_text.text = f'Health: {mario.health}'
        if distance(mario.position, level.goal.position) < 2:
            print(f"Level Complete! Score: {mario.coins}")
            application.quit()

    def input(key):
        if key == 'escape':
            mouse.locked = not mouse.locked
        if key == 'r':
            mario.respawn()

    globals()['update'] = update_ui
    globals()['input'] = input


# -------------------------------------------------
# Run with Menu First
# -------------------------------------------------
menu = MainMenu()
app.run()
