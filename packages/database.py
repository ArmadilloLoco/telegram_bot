import os
import sys
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
import psycopg2
import handlers as hand


DB_CONFIG = {
    'host': hand.read_ini('database', 'host'),
    'port': int(hand.read_ini('database', 'port')),
    'database': hand.read_ini('database', 'database'),
    'user': hand.read_ini('database', 'user'),
    'password': hand.read_ini('database', 'password')
}

def get_connection(): 
    return psycopg2.connect(**DB_CONFIG)

def add_user(user_id, username, first_name, last_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO users (user_id, username, first_name, last_name)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id) DO NOTHING
    ''', (user_id, username, first_name, last_name))
    conn.commit()
    cur.close()
    conn.close()

def get_all_words(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT word_rus, word_eng FROM common_words
        UNION
        SELECT word_rus, word_eng FROM user_words WHERE user_id = %s
    ''', (user_id,))
    rows = cur.fetchall()
    words = [{'word_rus': r, 'word_eng': e} for r, e in rows]
    cur.close()
    conn.close()
    return words

def add_user_word(user_id, russian, english):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO user_words (user_id, word_rus, word_eng)
        VALUES (%s, %s, %s)
    ''', (user_id, russian, english))
    conn.commit()
    cur.close()
    conn.close()

def delete_user_word(user_id, russian, english):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        DELETE FROM user_words
        WHERE user_id = %s AND word_rus = %s AND word_eng = %s
        RETURNING id
    ''', (user_id, russian, english))
    deleted = cur.fetchone() is not None
    conn.commit()
    cur.close()
    conn.close()
    return deleted

def get_user_words_count(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM user_words WHERE user_id = %s', (user_id,))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count

def get_word(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT word_rus, word_eng FROM user_words WHERE user_id = %s', (user_id,))
    rows = cur.fetchall()
    words = [{'word_rus': r, 'word_eng': e} for r, e in rows]
    cur.close()
    conn.close()
    return words