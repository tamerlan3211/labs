
import pygame
import sys
import random
import time

from pygame.locals import *

# Project modules
from racer import (
    Road, Player, Enemy, Coin,
    OilSpill, SpeedBump, Barrier, NitroStrip,
    PowerUp, POWERUP_TYPES, DIFFICULTY,
    SCREEN_WIDTH, SCREEN_HEIGHT, ROAD_LEFT, ROAD_RIGHT, NUM_LANES
)
from ui import main_menu, name_entry, settings_screen, game_over_screen, leaderboard_screen
from persistence import load_settings, add_leaderboard_entry

# ─────────────────── Pygame setup ────────────────────
pygame.init()
SURFACE = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer — TSIS3")

FPS_CLOCK = pygame.time.Clock()

# ─────────────────── HUD fonts ───────────────────────
FONT_SM  = pygame.font.SysFont("Verdana", 16)
FONT_MED = pygame.font.SysFont("Verdana", 20, bold=True)
FONT_LG  = pygame.font.SysFont("Verdana", 36, bold=True)

# ─────────────────── Colours ─────────────────────────
BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
YELLOW = (255, 215, 0)
ACCENT = (0,   220, 120)
RED    = (220, 50,  50)
BG_DARK = (15, 20, 40)

# ─────────────────── HUD helpers ─────────────────────

def draw_hud(surface, score, coins, distance, player, active_pu, pu_end):
    """Draw all HUD elements."""
    # Top bar background
    pygame.draw.rect(surface, (0, 0, 0, 180), (0, 0, SCREEN_WIDTH, 38))

    score_s = FONT_SM.render(f"Score: {score}", True, WHITE)
    coins_s = FONT_SM.render(f"Coins: {coins}", True, YELLOW)
    dist_s  = FONT_SM.render(f"Dist: {distance}m", True, ACCENT)

    surface.blit(score_s, (8, 10))
    surface.blit(coins_s, (SCREEN_WIDTH//2 - 40, 10))
    surface.blit(dist_s,  (SCREEN_WIDTH - 108, 10))

    # Active power-up bar
    if active_pu:
        remaining = max(0, pu_end - pygame.time.get_ticks())
        pu_colors = {"NITRO": (0, 220, 120), "SHIELD": (50, 130, 255), "REPAIR": (255, 160, 0)}
        color = pu_colors.get(active_pu, WHITE)
        bar_w = int(160 * (remaining / 4000))
        bar_w = max(0, min(160, bar_w))
        pygame.draw.rect(surface, (40, 40, 60), (ROAD_LEFT, 42, 160, 12), border_radius=4)
        pygame.draw.rect(surface, color,         (ROAD_LEFT, 42, bar_w, 12), border_radius=4)
        pu_lbl = FONT_SM.render(f"{active_pu} active", True, color)
        surface.blit(pu_lbl, (ROAD_LEFT, 56))

    # Shield / Nitro indicators
    if player.shield_active:
        sh = FONT_SM.render("🛡 SHIELD", True, (100, 180, 255))
        surface.blit(sh, (SCREEN_WIDTH - 90, 42))
    if player.nitro_active:
        ni = FONT_SM.render("⚡ NITRO", True, (0, 220, 120))
        surface.blit(ni, (SCREEN_WIDTH - 90, 60))


def flash_message(surface, text, color, duration_ms=600):
    surf = FONT_LG.render(text, True, color)
    rect = surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    surface.blit(surf, rect)
    pygame.display.flip()
    pygame.time.delay(duration_ms)


# ─────────────────── Main game session ───────────────

def run_game(player_name: str, settings: dict):
    """Run one game session. Returns (score, distance, coins)."""
    diff   = DIFFICULTY[settings.get("difficulty", "MEDIUM")]
    road   = Road()

    # Sprite groups
    player = Player(settings.get("car_color", "BLUE"))
    enemies_grp  = pygame.sprite.Group()
    coins_grp    = pygame.sprite.Group()
    obstacles_grp = pygame.sprite.Group()  # OilSpill, SpeedBump
    barriers_grp  = pygame.sprite.Group()  # Barrier (lethal)
    nitro_strips  = pygame.sprite.Group()  # NitroStrip (collect = nitro)
    powerups_grp  = pygame.sprite.Group()

    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    # Game state
    score    = 0
    coins    = 0
    distance = 0            # metres driven (approx)
    speed    = diff["speed"]
    base_spd = diff["speed"]

    # Timers (ms ticks)
    last_enemy_spawn   = pygame.time.get_ticks()
    last_coin_spawn    = pygame.time.get_ticks()
    last_obs_spawn     = pygame.time.get_ticks()
    last_pu_spawn      = pygame.time.get_ticks()
    last_nitro_spawn   = pygame.time.get_ticks()
    game_start         = pygame.time.get_ticks()

    enemy_interval = diff["interval"]
    obs_interval   = 3000
    pu_interval    = 7000
    nitro_interval = 5000

    active_pu     = None   # "NITRO" | "SHIELD" | "REPAIR"
    active_pu_end = 0

    oil_slow_end  = 0      # When oil slow wears off
    slow_active   = False

    def spawn_enemy():
        if len(enemies_grp) < diff["max_enemies"]:
            e = Enemy(base_speed=speed, player_rect=player.rect)
            enemies_grp.add(e)
            all_sprites.add(e)

    def spawn_coin():
        c = Coin(speed=speed)
        coins_grp.add(c)
        all_sprites.add(c)

    def spawn_obstacle():
        kind = random.choice(["oil", "bump", "barrier"])
        if kind == "oil":
            obj = OilSpill(speed=speed)
            obstacles_grp.add(obj)
        elif kind == "bump":
            obj = SpeedBump(speed=speed)
            obstacles_grp.add(obj)
        else:
            obj = Barrier(speed=speed)
            barriers_grp.add(obj)
        all_sprites.add(obj)

    def spawn_powerup():
        if len(powerups_grp) == 0:
            kind = random.choice(POWERUP_TYPES)
            pu = PowerUp(kind, speed=speed)
            powerups_grp.add(pu)
            all_sprites.add(pu)

    def spawn_nitro_strip():
        ns = NitroStrip(speed=speed)
        nitro_strips.add(ns)
        all_sprites.add(ns)

    # Initial spawns
    spawn_enemy()
    spawn_coin()

    running = True
    while running:
        now = pygame.time.get_ticks()
        dt  = FPS_CLOCK.tick(60)

        # ── Events ──────────────────────────────────────
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False

        # ── Difficulty scaling (every 10 score pts) ─────
        speed    = base_spd + score // 10 * 0.5
        enemy_interval = max(500, diff["interval"] - score * 5)

        # ── Timed spawning ──────────────────────────────
        if now - last_enemy_spawn > enemy_interval:
            spawn_enemy()
            last_enemy_spawn = now

        if now - last_coin_spawn > 1200:
            spawn_coin()
            last_coin_spawn = now

        if now - last_obs_spawn > obs_interval:
            spawn_obstacle()
            last_obs_spawn = now
            obs_interval = max(1500, 3000 - score * 10)

        if now - last_pu_spawn > pu_interval:
            spawn_powerup()
            last_pu_spawn = now

        if now - last_nitro_spawn > nitro_interval:
            spawn_nitro_strip()
            last_nitro_spawn = now

        # ── Slow / oil effects ──────────────────────────
        if slow_active and now > oil_slow_end:
            slow_active = False

        effective_speed = speed * (0.5 if slow_active else 1.0)

        # ── Move everything ─────────────────────────────
        road.update(effective_speed)
        player.move()

        for e in list(enemies_grp):
            e.speed = effective_speed
            e.move()

        for c in list(coins_grp):
            c.speed = effective_speed
            c.move()

        for o in list(obstacles_grp):
            o.speed = effective_speed
            o.move()

        for b in list(barriers_grp):
            b.speed = effective_speed
            b.move()

        for ns in list(nitro_strips):
            ns.speed = effective_speed
            ns.move()

        for pu in list(powerups_grp):
            pu.speed = effective_speed
            pu.move()

        # ── Distance tracking ───────────────────────────
        distance = int((now - game_start) * effective_speed / 1000 * 0.8)

        # ── Collision: coins ────────────────────────────
        hit_coins = pygame.sprite.spritecollide(player, coins_grp, True)
        for coin in hit_coins:
            val = int(coin.value * diff["coin_val_mult"])
            coins += val
            score += val * 2

        # ── Collision: oil / bumps (slow) ───────────────
        if pygame.sprite.spritecollideany(player, obstacles_grp):
            slow_active  = True
            oil_slow_end = now + 2000

        # ── Collision: barriers (lethal) ────────────────
        if pygame.sprite.spritecollideany(player, barriers_grp):
            saved = player.absorb_hit()
            if not saved:
                running = False

        # ── Collision: nitro strips ─────────────────────
        hit_ns = pygame.sprite.spritecollide(player, nitro_strips, True)
        if hit_ns:
            player.activate_nitro(3000)

        # ── Collision: enemies ──────────────────────────
        if pygame.sprite.spritecollideany(player, enemies_grp):
            saved = player.absorb_hit()
            if not saved:
                running = False

        # ── Collision: power-ups ────────────────────────
        hit_pu = pygame.sprite.spritecollide(player, powerups_grp, True)
        for pu in hit_pu:
            active_pu = pu.kind
            if pu.kind == "NITRO":
                player.activate_nitro(4000)
                active_pu_end = now + 4000
            elif pu.kind == "SHIELD":
                player.activate_shield()
                active_pu_end = now + 99999  # until hit
            elif pu.kind == "REPAIR":
                # Repair clears oil slow and removes one barrier
                slow_active = False
                for b in list(barriers_grp)[:1]:
                    b.kill()
                active_pu = None   # instant

        # ── Score ticks per distance ────────────────────
        score = int(coins * 2 + distance // 10)

        # ── Draw ─────────────────────────────────────────
        SURFACE.fill((15, 20, 40))
        road.draw(SURFACE)

        # Draw all sprites manually (ordered)
        for grp in [nitro_strips, obstacles_grp, barriers_grp, coins_grp, powerups_grp, enemies_grp]:
            grp.draw(SURFACE)
        SURFACE.blit(player.image, player.rect)

        draw_hud(SURFACE, score, coins, distance, player, active_pu, active_pu_end)
        pygame.display.flip()

    # ── Final score calc ────────────────────────────────
    final_score = coins * 3 + distance // 5 + score // 2
    return final_score, distance, coins


# ─────────────────── App loop ─────────────────────────

def main():
    settings    = load_settings()
    player_name = "Player1"
    state       = "menu"

    while True:
        if state == "menu":
            state = main_menu(SURFACE)

        elif state == "play":
            player_name = name_entry(SURFACE)
            score, dist, coins = run_game(player_name, settings)
            add_leaderboard_entry(player_name, score, dist, coins)
            state = game_over_screen(SURFACE, score, dist, coins)
            if state == "retry":
                # Keep same player name, restart immediately
                score, dist, coins = run_game(player_name, settings)
                add_leaderboard_entry(player_name, score, dist, coins)
                state = game_over_screen(SURFACE, score, dist, coins)
            else:
                state = "menu"

        elif state == "leaderboard":
            leaderboard_screen(SURFACE)
            state = "menu"

        elif state == "settings":
            settings_screen(SURFACE)
            settings = load_settings()   # reload after save
            state = "menu"

        elif state == "quit":
            pygame.quit()
            sys.exit()

        else:
            state = "menu"


if __name__ == "__main__":
    main()
