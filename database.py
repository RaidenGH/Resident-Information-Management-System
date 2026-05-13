import sqlite3

def connect_db():
    return sqlite3.connect("residents.db")

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    # Residents table linked to Purok
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS residents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            contact TEXT,
            purok_id INTEGER,
            FOREIGN KEY (purok_id) REFERENCES puroks(id)
        )
    """)
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def create_purok_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS puroks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# User functions
def add_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

def validate_login(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# Purok functions
def get_puroks():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM puroks")
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_purok(name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO puroks (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

# Resident functions
def add_resident(name, age, contact, purok_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO residents (name, age, contact, purok_id) VALUES (?, ?, ?, ?)",
                   (name, age, contact, purok_id))
    conn.commit()
    conn.close()

def get_residents_by_purok(purok_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, age, contact FROM residents WHERE purok_id=?", (purok_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_resident(resident_id, name, age, contact):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE residents SET name=?, age=?, contact=? WHERE id=?",
                   (name, age, contact, resident_id))
    conn.commit()
    conn.close()

def delete_resident(resident_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM residents WHERE id=?", (resident_id,))
    conn.commit()
    conn.close()
