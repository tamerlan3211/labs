# TSIS3 — Racer Game (Advanced Edition)

## Requirements

```
pip install pygame
```

## How to Run

```bash
cd TSIS3
python main.py
```

## Project Structure

```
TSIS3/
├── main.py          ← Entry point & game loop
├── racer.py         ← All sprite / game-object classes
├── ui.py            ← All screens (menu, settings, leaderboard, game-over)
├── persistence.py   ← Save/load settings.json & leaderboard.json
├── settings.json    ← Auto-created/updated by Settings screen
├── leaderboard.json ← Auto-created/updated after each run
└── assets/          ← (optional) images & sounds
```

## Controls

| Key | Action |
|-----|--------|
| ← / A | Move left |
| → / D | Move right |
| ESC | Pause / return to menu |

## Features (TSIS3)

### 3.1 — Gameplay & Race Track
- **Lane hazards**: Oil spills (slow you down), speed bumps (slow), barriers (lethal)
- **Road events**: Nitro strips on the road give instant speed boosts; dynamic event frequency increases with score

### 3.2 — Dynamic Traffic & Obstacles
- **Traffic cars**: Enemy cars scroll down; collision = game over (or shield absorbs)
- **Road obstacles**: Oil spills, speed bumps, barriers — all randomly placed in lanes
- **Safe spawn logic**: Enemies never spawn directly on the player
- **Difficulty scaling**: Enemy count and spawn interval scale with score

### 3.3 — Power-Ups
| Power-Up | Effect | Duration |
|----------|--------|----------|
| ⚡ Nitro  | 1.8× speed boost | 4 seconds |
| 🛡 Shield | Absorbs one fatal collision | Until hit |
| 🔧 Repair | Clears oil slow + removes nearest barrier | Instant |

- Only one power-up active at a time
- Power-ups disappear after 8 seconds if uncollected
- Active power-up + remaining time shown in HUD

### 3.4 — Score, Distance & Leaderboard
- Score = coins × 3 + distance ÷ 5 + in-game score ÷ 2
- Distance meter shown in HUD
- Top 10 leaderboard saved to `leaderboard.json`
- Name entry before each game session
- Leaderboard screen shows rank, name, score, distance

### 3.5 — Screens & Settings
- **Main Menu**: Play, Leaderboard, Settings, Quit
- **Settings**: Toggle sound, choose car color (4 options), choose difficulty (Easy/Medium/Hard)
- **Game Over**: Shows score, distance, coins; Retry or Main Menu buttons
- **Leaderboard**: Top 10 with rank highlighting (gold/silver/bronze)
- Settings auto-saved to `settings.json` and applied immediately
