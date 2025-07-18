import sqlite3

def get_connection():
    conn = sqlite3.connect("vocab.db", check_same_thread=False)
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS vocab_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            book_name TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            word TEXT,
            meaning TEXT,
            pos TEXT,
            memorized INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def get_user(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def add_book(user_id, book_name):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO vocab_books (user_id, book_name) VALUES (?, ?)", (user_id, book_name))
    conn.commit()
    conn.close()

def get_books(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM vocab_books WHERE user_id=?", (user_id,))
    books = c.fetchall()
    conn.close()
    return books

def delete_book(book_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM words WHERE book_id=?", (book_id,))
    c.execute("DELETE FROM vocab_books WHERE id=?", (book_id,))
    conn.commit()
    conn.close()

def add_word(book_id, word, meaning, pos):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO words (book_id, word, meaning, pos) VALUES (?, ?, ?, ?)",
              (book_id, word, meaning, pos))
    conn.commit()
    conn.close()

def get_words(book_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM words WHERE book_id=?", (book_id,))
    words = c.fetchall()
    conn.close()
    return words

def update_memorized(word_id, val):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE words SET memorized=? WHERE id=?", (val, word_id))
    conn.commit()
    conn.close()

def delete_word(word_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM words WHERE id=?", (word_id,))
    conn.commit()
    conn.close()
