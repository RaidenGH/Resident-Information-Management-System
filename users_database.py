import sqlite3

def connect_users_db():
    return sqlite3.connect("users.db")

def create_users_table():
    conn = connect_users_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = connect_users_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

def validate_login(username, password):
    conn = connect_users_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def create_users_table():
    conn = connect_users_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            phone TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_user(username, password, first_name, last_name, email, phone):
    conn = connect_users_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (username, password, first_name, last_name, email, phone)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (username, password, first_name, last_name, email, phone))
    conn.commit()
    conn.close()
