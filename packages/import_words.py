import os
import sys
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
import psycopg2
import csv
import handlers as hand

DB_CONFIG = {
    'host': hand.read_ini('database', 'host'),
    'port': int(hand.read_ini('database', 'port')),
    'database': hand.read_ini('database', 'database'),
    'user': hand.read_ini('database', 'user'),
    'password': hand.read_ini('database', 'password')
}

def import_if_empty(csv_file_path):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM common_words")
    count = cur.fetchone()[0]
    if count == 0:
        print("Таблица common_words пуста. Загружаю данные из CSV...")
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cur.execute('''
                        INSERT INTO common_words (word_rus, word_eng)
                        VALUES (%s, %s)
                        ON CONFLICT DO NOTHING
                    ''', (row['word_rus'], row['word_eng']))
            conn.commit()
            print(f"✅ Успешно загружено {cur.rowcount} слов в таблицу common_words.")
            cur.close()

        except Exception as e:
            print(f"❌ Ошибка при загрузке данных: {e}")
        finally:
            if conn:
                conn.close()
    else:
        print(f"Уже есть {count} слов. Пропускаем загрузку.")
    cur.close()
    conn.close()