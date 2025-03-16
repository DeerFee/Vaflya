import sqlite3
from tabulate import tabulate  # Для красивого вывода таблиц
from typing import List, Tuple

class DatabaseViewer:
    def __init__(self, db_file: str = 'bot_database.db'):
        self.db_file = db_file

    def get_tables(self) -> List[str]:
        """Получить список всех таблиц в базе данных"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        conn.close()
        return [table[0] for table in tables]

    def view_table(self, table_name: str) -> Tuple[List[str], List[Tuple]]:
        """Просмотр содержимого таблицы"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Получаем информацию о столбцах
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Получаем данные
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        conn.close()
        return columns, rows

    def print_table(self, table_name: str) -> None:
        """Красивый вывод таблицы"""
        columns, rows = self.view_table(table_name)
        print(f"\nТаблица: {table_name}")
        print(tabulate(rows, headers=columns, tablefmt='grid'))

    def get_table_stats(self, table_name: str) -> dict:
        """Получить статистику по таблице"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        conn.close()
        return {
            "table_name": table_name,
            "total_rows": count
        }

if __name__ == "__main__":
    viewer = DatabaseViewer()
    
    print("🗄 Доступные таблицы в базе данных:")
    tables = viewer.get_tables()
    for i, table in enumerate(tables, 1):
        stats = viewer.get_table_stats(table)
        print(f"{i}. {table} (записей: {stats['total_rows']})")
    
    while True:
        print("\nВыберите действие:")
        print("1. Просмотреть таблицу")
        print("2. Показать статистику")
        print("3. Выйти")
        
        choice = input("Введите номер действия: ")
        
        if choice == "1":
            print("\nДоступные таблицы:")
            for i, table in enumerate(tables, 1):
                print(f"{i}. {table}")
            
            try:
                table_index = int(input("Введите номер таблицы: ")) - 1
                if 0 <= table_index < len(tables):
                    viewer.print_table(tables[table_index])
                else:
                    print("❌ Неверный номер таблицы")
            except ValueError:
                print("❌ Пожалуйста, введите число")
        
        elif choice == "2":
            print("\nСтатистика по таблицам:")
            for table in tables:
                stats = viewer.get_table_stats(table)
                print(f"📊 {stats['table_name']}: {stats['total_rows']} записей")
        
        elif choice == "3":
            print("👋 До свидания!")
            break
        
        else:
            print("❌ Неверный выбор")