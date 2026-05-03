import json
import os

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "sound": True,
    "car_color": "BLUE",
    "difficulty": "MEDIUM"
}

# ---------- Settings ----------

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                # Fill in any missing keys with defaults
                for key, val in DEFAULT_SETTINGS.items():
                    if key not in data:
                        data[key] = val
                return data
        except (json.JSONDecodeError, IOError):
            pass
    return DEFAULT_SETTINGS.copy()

def save_settings(settings: dict):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)
    except IOError as e:
        print(f"[persistence] Could not save settings: {e}")

# ---------- Leaderboard ----------

def load_leaderboard() -> list:
    """Return a list of dicts sorted by score descending."""
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except (json.JSONDecodeError, IOError):
            pass
    return []

def save_leaderboard(entries: list):
    try:
        with open(LEADERBOARD_FILE, "w") as f:
            json.dump(entries, f, indent=2)
    except IOError as e:
        print(f"[persistence] Could not save leaderboard: {e}")

def add_leaderboard_entry(name: str, score: int, distance: int, coins: int):
    """Add an entry, keep top 10, save to disk. Returns updated list."""
    entries = load_leaderboard()
    entries.append({
        "name": name,
        "score": score,
        "distance": distance,
        "coins": coins
    })
    entries.sort(key=lambda e: e["score"], reverse=True)
    entries = entries[:10]
    save_leaderboard(entries)
    return entries
