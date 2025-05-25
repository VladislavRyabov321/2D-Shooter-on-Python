import sqlite3
import time

def save_result(player_name, level_reached, enemies_killed, start_time):
    duration = int(time.time() - start_time)

    conn = sqlite3.connect('game_results.db')
    c = conn.cursor()

    # Создаём таблицу, если не существует
    c.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT,
            level_reached INTEGER,
            enemies_killed INTEGER,
            play_time_seconds INTEGER,
            play_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Добавляем новую строку
    c.execute('''
        INSERT INTO results (player_name, level_reached, enemies_killed, play_time_seconds)
        VALUES (?, ?, ?, ?)
    ''', (player_name, level_reached, enemies_killed, duration))

    conn.commit()
    conn.close()


def get_all_games():
    conn = sqlite3.connect('game_results.db')
    c = conn.cursor()
    c.execute("SELECT * FROM results ORDER BY id DESC")
    table_data = c.fetchall()
    conn.close()
    return table_data

def get_avg_kills():
    conn = sqlite3.connect('game_results.db')
    c = conn.cursor()
    c.execute("SELECT AVG(enemies_killed) FROM results")
    result = c.fetchone()[0]
    conn.close()
    return round(result, 2) if result else 0

def get_avg_time():
    conn = sqlite3.connect('game_results.db')
    c = conn.cursor()
    c.execute("SELECT AVG(play_time_seconds) FROM results")
    result = c.fetchone()[0]
    conn.close()
    return round(result, 2) if result else 0

def get_fastest_run():
    conn = sqlite3.connect('game_results.db')
    c = conn.cursor()
    c.execute("SELECT MIN(play_time_seconds) FROM results WHERE play_time_seconds > 0")
    result = c.fetchone()[0]
    conn.close()
    if result is None:
        return 0
    return result

def get_longest_run():
    conn = sqlite3.connect('game_results.db')
    c = conn.cursor()
    c.execute("SELECT MAX(play_time_seconds) FROM results")
    result = c.fetchone()[0]
    conn.close()
    return result if result else 0

    conn.commit()
    conn.close()