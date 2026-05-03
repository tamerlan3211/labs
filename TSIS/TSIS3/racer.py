
import pygame
import random
from pygame.locals import *

# ─────────────────── Colour palette ───────────────────
BLUE   = (0,   0,   255)
RED    = (220, 30,  30)
GREEN  = (0,   200, 80)
BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
YELLOW = (255, 215, 0)
ORANGE = (255, 140, 0)
PURPLE = (160, 32,  240)
CYAN   = (0,   220, 220)
GREY   = (120, 120, 120)
DARK_GREY = (60, 60, 60)
LIME   = (180, 255, 0)
BROWN  = (139, 90,  43)

CAR_COLORS = {
    "BLUE":   (30,  120, 255),
    "RED":    (220, 40,  40),
    "GREEN":  (30,  200, 80),
    "YELLOW": (240, 200, 0),
}

# ─────────────────── Constants ────────────────────────
SCREEN_WIDTH  = 500
SCREEN_HEIGHT = 600
ROAD_LEFT     = 40          # Road starts X
ROAD_RIGHT    = 360         # Road ends   X
ROAD_WIDTH    = ROAD_RIGHT - ROAD_LEFT

NUM_LANES     = 3
LANE_WIDTH    = ROAD_WIDTH // NUM_LANES

# Difficulty tables  { name: (base_enemy_speed, spawn_interval_ms, max_enemies) }
DIFFICULTY = {
    "EASY":   {"speed": 4,  "interval": 2000, "max_enemies": 2, "coin_val_mult": 1.0},
    "MEDIUM": {"speed": 6,  "interval": 1500, "max_enemies": 3, "coin_val_mult": 1.2},
    "HARD":   {"speed": 9,  "interval": 900,  "max_enemies": 4, "coin_val_mult": 1.5},
}

POWERUP_TIMEOUT = 8000   # ms — power-up disappears if uncollected

# ─────────────────── Helpers ─────────────────────────

def lane_center_x(lane: int) -> int:
    """lane: 0,1,2  → x centre of that lane on the road."""
    return ROAD_LEFT + lane * LANE_WIDTH + LANE_WIDTH // 2

def random_lane_x() -> int:
    return lane_center_x(random.randint(0, NUM_LANES - 1))

def safe_spawn_y(player_rect, margin=120) -> int:
    """Return a Y position guaranteed to NOT overlap the player."""
    return -random.randint(60, 200)

# ─────────────────── Road / background ───────────────

class Road:
    """Scrolling road with lane markings."""

    STRIPE_H = 40
    STRIPE_GAP = 40

    def __init__(self):
        self.scroll_y = 0

    def update(self, speed):
        self.scroll_y = (self.scroll_y + speed) % (self.STRIPE_H + self.STRIPE_GAP)

    def draw(self, surface):
        # Asphalt
        pygame.draw.rect(surface, DARK_GREY, (ROAD_LEFT, 0, ROAD_WIDTH, SCREEN_HEIGHT))

        # Lane dividers (dashed yellow)
        for lane in range(1, NUM_LANES):
            x = ROAD_LEFT + lane * LANE_WIDTH - 2
            y = -self.STRIPE_GAP + self.scroll_y
            while y < SCREEN_HEIGHT:
                pygame.draw.rect(surface, YELLOW, (x, y, 4, self.STRIPE_H))
                y += self.STRIPE_H + self.STRIPE_GAP

        # Road edges (white solid)
        pygame.draw.rect(surface, WHITE, (ROAD_LEFT - 4, 0, 4, SCREEN_HEIGHT))
        pygame.draw.rect(surface, WHITE, (ROAD_RIGHT, 0, 4, SCREEN_HEIGHT))

        # Kerb (grass / dirt)
        pygame.draw.rect(surface, (34, 139, 34), (0, 0, ROAD_LEFT - 4, SCREEN_HEIGHT))
        pygame.draw.rect(surface, (34, 139, 34), (ROAD_RIGHT + 4, 0, SCREEN_WIDTH - ROAD_RIGHT - 4, SCREEN_HEIGHT))

# ─────────────────── Player ──────────────────────────

class Player(pygame.sprite.Sprite):
    WIDTH  = 36
    HEIGHT = 60

    def __init__(self, color_name="BLUE"):
        super().__init__()
        self.base_color = CAR_COLORS.get(color_name, BLUE)
        self.image = self._make_surface(self.base_color)
        self.rect  = self.image.get_rect(center=(SCREEN_WIDTH // 2, 510))

        self.speed = 5
        self.shield_active  = False
        self.nitro_active   = False
        self.nitro_end_time = 0
        self.shield_used    = False  # shield consumed by one hit

    def _make_surface(self, color):
        surf = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        # Body
        pygame.draw.rect(surf, color, (4, 10, self.WIDTH-8, self.HEIGHT-14), border_radius=6)
        # Windshield
        pygame.draw.rect(surf, (160, 220, 255, 200), (8, 14, self.WIDTH-16, 16), border_radius=3)
        # Wheels
        wc = (30, 30, 30)
        for wx, wy in [(0, 12), (self.WIDTH-8, 12), (0, self.HEIGHT-28), (self.WIDTH-8, self.HEIGHT-28)]:
            pygame.draw.rect(surf, wc, (wx, wy, 8, 14), border_radius=3)
        return surf

    def update_appearance(self):
        color = self.base_color
        if self.shield_active:
            # tint blue-ish
            color = tuple(min(255, c + 60) if i == 2 else max(0, c - 30) for i, c in enumerate(color))
        if self.nitro_active:
            color = tuple(min(255, c + 80) if i == 0 else c for i, c in enumerate(color))
        self.image = self._make_surface(color)

    def move(self):
        keys = pygame.key.get_pressed()
        spd = self.speed
        if self.nitro_active:
            if pygame.time.get_ticks() > self.nitro_end_time:
                self.nitro_active = False
                self.update_appearance()
            else:
                spd = int(spd * 1.8)

        if self.rect.left > ROAD_LEFT:
            if keys[K_LEFT] or keys[K_a]:
                self.rect.x -= spd
        if self.rect.right < ROAD_RIGHT:
            if keys[K_RIGHT] or keys[K_d]:
                self.rect.x += spd

    def activate_nitro(self, duration_ms=4000):
        self.nitro_active   = True
        self.nitro_end_time = pygame.time.get_ticks() + duration_ms
        self.update_appearance()

    def activate_shield(self):
        self.shield_active = True
        self.shield_used   = False
        self.update_appearance()

    def absorb_hit(self):
        """Returns True if shield saved the player, False if real collision."""
        if self.shield_active and not self.shield_used:
            self.shield_active = False
            self.shield_used   = True
            self.update_appearance()
            return True
        return False

# ─────────────────── Enemy cars ──────────────────────

class Enemy(pygame.sprite.Sprite):
    WIDTH  = 36
    HEIGHT = 60

    COLORS = [(220, 40, 40), (200, 80, 0), (140, 0, 200), (0, 160, 200)]

    def __init__(self, base_speed=6, player_rect=None):
        super().__init__()
        self.color = random.choice(self.COLORS)
        self.image = self._make_surface()
        self.rect  = self.image.get_rect()
        self.speed = base_speed + random.uniform(-1, 1)
        self._place(player_rect)

    def _make_surface(self):
        surf = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(surf, self.color, (4, 4, self.WIDTH-8, self.HEIGHT-8), border_radius=6)
        pygame.draw.rect(surf, (160, 220, 255, 180), (8, 8, self.WIDTH-16, 14), border_radius=3)
        wc = (30, 30, 30)
        for wx, wy in [(0, 8), (self.WIDTH-8, 8), (0, self.HEIGHT-22), (self.WIDTH-8, self.HEIGHT-22)]:
            pygame.draw.rect(surf, wc, (wx, wy, 8, 14), border_radius=3)
        return surf

    def _place(self, player_rect=None):
        lane = random.randint(0, NUM_LANES - 1)
        self.rect.centerx = lane_center_x(lane)
        self.rect.bottom  = random.randint(-80, -20)
        # Make sure not directly above player
        if player_rect:
            attempts = 0
            while abs(self.rect.centerx - player_rect.centerx) < 40 and attempts < 10:
                lane = random.randint(0, NUM_LANES - 1)
                self.rect.centerx = lane_center_x(lane)
                attempts += 1

    def move(self):
        self.rect.y += int(self.speed)
        if self.rect.top > SCREEN_HEIGHT + 10:
            self.kill()

# ─────────────────── Coin ────────────────────────────

class Coin(pygame.sprite.Sprite):
    VALUES = [1, 2, 5]
    COLORS_MAP = {1: YELLOW, 2: ORANGE, 5: CYAN}

    def __init__(self, speed=5):
        super().__init__()
        self.value  = random.choices(self.VALUES, weights=[60, 30, 10])[0]
        color       = self.COLORS_MAP[self.value]
        self.image  = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (10, 10), 10)
        pygame.draw.circle(self.image, WHITE,  (10, 10),  6, 2)
        self.rect   = self.image.get_rect()
        self.rect.centerx = random_lane_x()
        self.rect.bottom  = random.randint(-160, -20)
        self.speed  = speed

    def move(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# ─────────────────── Obstacles ───────────────────────

class OilSpill(pygame.sprite.Sprite):
    """Slows the player temporarily."""

    def __init__(self, speed=5):
        super().__init__()
        self.image = pygame.Surface((50, 30), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (30, 30, 30, 200), (0, 0, 50, 30))
        pygame.draw.ellipse(self.image, (80, 0, 120, 160), (5, 5, 40, 20))
        self.rect  = self.image.get_rect()
        self.rect.centerx = random_lane_x()
        self.rect.bottom  = random.randint(-200, -40)
        self.speed = speed

    def move(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class SpeedBump(pygame.sprite.Sprite):
    """Slows player temporarily."""

    def __init__(self, speed=5):
        super().__init__()
        self.image = pygame.Surface((LANE_WIDTH - 10, 14), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (180, 160, 0), (0, 0, LANE_WIDTH-10, 14), border_radius=4)
        for i in range(0, LANE_WIDTH-10, 12):
            pygame.draw.rect(self.image, (220, 200, 0), (i, 4, 6, 6))
        self.rect = self.image.get_rect()
        self.rect.centerx = random_lane_x()
        self.rect.bottom  = random.randint(-200, -40)
        self.speed = speed

    def move(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Barrier(pygame.sprite.Sprite):
    """Hard obstacle — touching it is like hitting an enemy."""

    def __init__(self, speed=5):
        super().__init__()
        self.image = pygame.Surface((LANE_WIDTH - 6, 22), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (200, 30, 30), (0, 0, LANE_WIDTH-6, 22), border_radius=4)
        pygame.draw.rect(self.image, WHITE, (0, 8, LANE_WIDTH-6, 6))
        self.rect  = self.image.get_rect()
        self.rect.centerx = random_lane_x()
        self.rect.bottom  = random.randint(-200, -40)
        self.speed = speed

    def move(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class NitroStrip(pygame.sprite.Sprite):
    """Road feature — gives a speed boost just like Nitro power-up."""

    def __init__(self, speed=5):
        super().__init__()
        w = LANE_WIDTH - 10
        self.image = pygame.Surface((w, 18), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (0, 220, 120, 220), (0, 0, w, 18), border_radius=5)
        # Arrow chevrons
        mx = w // 2
        pygame.draw.polygon(self.image, WHITE, [(mx-10, 14), (mx+10, 14), (mx, 4)])
        self.rect  = self.image.get_rect()
        self.rect.centerx = random_lane_x()
        self.rect.bottom  = random.randint(-200, -40)
        self.speed = speed

    def move(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# ─────────────────── Power-ups ───────────────────────

POWERUP_TYPES = ["NITRO", "SHIELD", "REPAIR"]

class PowerUp(pygame.sprite.Sprite):
    ICONS  = {"NITRO": "⚡", "SHIELD": "🛡", "REPAIR": "🔧"}
    COLORS = {"NITRO": (0, 220, 120), "SHIELD": (0, 100, 255), "REPAIR": (255, 160, 0)}

    def __init__(self, kind: str, speed=5):
        super().__init__()
        self.kind  = kind
        color      = self.COLORS[kind]
        size       = 32
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color,   (size//2, size//2), size//2)
        pygame.draw.circle(self.image, WHITE,   (size//2, size//2), size//2, 2)
        # Letter inside
        font = pygame.font.SysFont("Verdana", 14, bold=True)
        lbl  = font.render(kind[0], True, WHITE)
        self.image.blit(lbl, lbl.get_rect(center=(size//2, size//2)))
        self.rect  = self.image.get_rect()
        self.rect.centerx = random_lane_x()
        self.rect.bottom  = random.randint(-200, -40)
        self.speed = speed
        self.spawn_time = pygame.time.get_ticks()

    def move(self):
        self.rect.y += self.speed
        elapsed = pygame.time.get_ticks() - self.spawn_time
        if self.rect.top > SCREEN_HEIGHT or elapsed > POWERUP_TIMEOUT:
            self.kill()
