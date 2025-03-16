import sqlite3
import datetime
from typing import Optional, List, Dict

class Database:
    def __init__(self, db_file: str = 'bot_database.db'):
        self.db_file = db_file
        self.create_tables()

    def create_tables(self) -> None:
        """Создание необходимых таблиц в базе данных"""
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()

        # Таблица пользователей
        cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            rating INTEGER DEFAULT 0,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP
        )
        ''')

        # Таблица настроек пользователей
        cur.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id INTEGER PRIMARY KEY,
            notifications_enabled BOOLEAN DEFAULT TRUE,
            language TEXT DEFAULT 'ru',
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        ''')

        # Таблица статистики использования команд
        cur.execute('''
        CREATE TABLE IF NOT EXISTS command_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            command TEXT,
            used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        ''')

        conn.commit()
        conn.close()

    def add_user(self, user_id: int, username: str, first_name: str, last_name: str) -> None:
        """Добавление нового пользователя"""
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        
        cur.execute('''
        INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, last_activity)
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name, datetime.datetime.now()))
        
        # Создаем запись в таблице настроек для нового пользователя
        cur.execute('''
        INSERT OR IGNORE INTO user_settings (user_id) VALUES (?)
        ''', (user_id,))
        
        conn.commit()
        conn.close()

    def update_user_activity(self, user_id: int) -> None:
        """Обновление времени последней активности пользователя"""
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        
        cur.execute('''
        UPDATE users SET last_activity = ? WHERE user_id = ?
        ''', (datetime.datetime.now(), user_id))
        
        conn.commit()
        conn.close()

    def log_command(self, user_id: int, command: str) -> None:
        """Логирование использования команды"""
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        
        cur.execute('''
        INSERT INTO command_stats (user_id, command)
        VALUES (?, ?)
        ''', (user_id, command))
        
        conn.commit()
        conn.close()

    def get_user(self, user_id: int) -> Optional[Dict]:
        """Получение информации о пользователе"""
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        
        cur.execute('''
        SELECT users.*, user_settings.notifications_enabled, user_settings.language
        FROM users 
        LEFT JOIN user_settings ON users.user_id = user_settings.user_id
        WHERE users.user_id = ?
        ''', (user_id,))
        
        result = cur.fetchone()
        conn.close()
        
        if result:
            return {
                'user_id': result[0],
                'username': result[1],
                'first_name': result[2],
                'last_name': result[3],
                'rating': result[4],
                'registration_date': result[5],
                'last_activity': result[6],
                'notifications_enabled': result[7],
                'language': result[8]
            }
        return None

    def update_user_settings(self, user_id: int, notifications_enabled: Optional[bool] = None, 
                           language: Optional[str] = None) -> None:
        """Обновление настроек пользователя"""
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        
        updates = []
        values = []
        if notifications_enabled is not None:
            updates.append("notifications_enabled = ?")
            values.append(notifications_enabled)
        if language is not None:
            updates.append("language = ?")
            values.append(language)
            
        if updates:
            query = f"UPDATE user_settings SET {', '.join(updates)} WHERE user_id = ?"
            values.append(user_id)
            cur.execute(query, values)
            
        conn.commit()
        conn.close()