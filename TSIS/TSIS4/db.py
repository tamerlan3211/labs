"""
db.py — Работа с базой данных PostgreSQL через psycopg2.
Содержит функции для сохранения результатов и получения таблицы лидеров.
"""

try:
    import psycopg2
    import psycopg2.extras
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

from config import DB_CONFIG, SQL_CREATE_TABLES


def _connect():
    """
    Создаёт и возвращает соединение с базой данных.
    Возвращает None если psycopg2 не установлен или БД недоступна.
    """
    if not DB_AVAILABLE:
        return None
    try:
        conn = psycopg2.connect(**DB_CONFIG, client_encoding='utf-8')
        return conn
    except Exception as e:
        # Выводим ошибку только байтами чтобы избежать проблем с кодировкой консоли Windows
        print(f"[DB] Cannot connect: {e}".encode('ascii', errors='replace').decode('ascii'))
        return None


def init_db():
    """
    Создаёт таблицы players и game_sessions если они ещё не существуют.
    Вызывается один раз при старте игры.
    """
    conn = _connect()
    if not conn:
        return
    try:
        with conn.cursor() as cur:
            cur.execute(SQL_CREATE_TABLES)
        conn.commit()
        print("[DB] Таблицы инициализированы.")
    except Exception as e:
        print(f"[DB] Ошибка инициализации: {e}")
    finally:
        conn.close()


def get_or_create_player(username: str) -> int | None:
    """
    Возвращает id игрока по имени.
    Если игрок не существует — создаёт новую запись и возвращает её id.

    :param username: имя игрока
    :return: player_id или None при ошибке
    """
    conn = _connect()
    if not conn:
        return None
    try:
        with conn.cursor() as cur:
            # Пытаемся найти существующего игрока
            cur.execute("SELECT id FROM players WHERE username = %s", (username,))
            row = cur.fetchone()
            if row:
                return row[0]
            # Создаём нового
            cur.execute(
                "INSERT INTO players (username) VALUES (%s) RETURNING id",
                (username,)
            )
            player_id = cur.fetchone()[0]
        conn.commit()
        return player_id
    except Exception as e:
        print(f"[DB] Ошибка get_or_create_player: {e}")
        return None
    finally:
        conn.close()


def save_session(player_id: int, score: int, level_reached: int):
    """
    Сохраняет результат игровой сессии в таблицу game_sessions.

    :param player_id:     id игрока из таблицы players
    :param score:         итоговый счёт
    :param level_reached: достигнутый уровень
    """
    if player_id is None:
        return
    conn = _connect()
    if not conn:
        return
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO game_sessions (player_id, score, level_reached)
                   VALUES (%s, %s, %s)""",
                (player_id, score, level_reached)
            )
        conn.commit()
        print(f"[DB] Сессия сохранена: score={score}, level={level_reached}")
    except Exception as e:
        print(f"[DB] Ошибка save_session: {e}")
    finally:
        conn.close()


def get_leaderboard(limit: int = 10) -> list[dict]:
    """
    Возвращает топ-N результатов всех игроков, отсортированных по счёту.

    :param limit: количество строк (по умолчанию 10)
    :return: список словарей {rank, username, score, level, played_at}
    """
    conn = _connect()
    if not conn:
        return []
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(
                """SELECT p.username,
                          gs.score,
                          gs.level_reached,
                          gs.played_at
                   FROM game_sessions gs
                   JOIN players p ON p.id = gs.player_id
                   ORDER BY gs.score DESC
                   LIMIT %s""",
                (limit,)
            )
            rows = cur.fetchall()
        # Добавляем номер места
        result = []
        for i, row in enumerate(rows, start=1):
            result.append({
                'rank'      : i,
                'username'  : row['username'],
                'score'     : row['score'],
                'level'     : row['level_reached'],
                'played_at' : row['played_at'].strftime('%d.%m.%Y') if row['played_at'] else '—',
            })
        return result
    except Exception as e:
        print(f"[DB] Ошибка get_leaderboard: {e}")
        return []
    finally:
        conn.close()


def get_personal_best(player_id: int) -> int:
    """
    Возвращает лучший счёт конкретного игрока.

    :param player_id: id игрока
    :return: максимальный score или 0
    """
    if player_id is None:
        return 0
    conn = _connect()
    if not conn:
        return 0
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COALESCE(MAX(score), 0) FROM game_sessions WHERE player_id = %s",
                (player_id,)
            )
            return cur.fetchone()[0]
    except Exception as e:
        print(f"[DB] Ошибка get_personal_best: {e}")
        return 0
    finally:
        conn.close()