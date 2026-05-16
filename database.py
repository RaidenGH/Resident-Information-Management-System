import sqlite3

def connect_db():
    return sqlite3.connect("residents.db")

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS puroks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS residents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            age INTEGER,
            contact TEXT,
            purok_id INTEGER,
            FOREIGN KEY (purok_id) REFERENCES puroks(id)
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
            name TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# --- Purok functions ---
def add_purok(name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO puroks (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def get_puroks():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM puroks")
    rows = cursor.fetchall()
    conn.close()
    return rows

def count_puroks():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM puroks")
    total = cursor.fetchone()[0]
    conn.close()
    return total

# --- Resident functions ---
def add_resident(first_name, last_name, age, contact, purok_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO residents (first_name, last_name, age, contact, purok_id)
        VALUES (?, ?, ?, ?, ?)
    """, (first_name, last_name, age, contact, purok_id))
    conn.commit()
    conn.close()

def update_resident(resident_id, first_name, last_name, age, contact):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE residents
        SET first_name=?, last_name=?, age=?, contact=?
        WHERE id=?
    """, (first_name, last_name, age, contact, resident_id))
    conn.commit()
    conn.close()

def delete_resident(resident_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM residents WHERE id=?", (resident_id,))
    conn.commit()
    conn.close()

def get_residents_by_purok(purok_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, first_name, last_name, age, contact
        FROM residents
        WHERE purok_id=?
    """, (purok_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def count_residents():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM residents")
    total = cursor.fetchone()[0]
    conn.close()
    return total
