import sqlite3

DB_NAME = "residents.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_tables():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS puroks (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS residents (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name  TEXT NOT NULL,
                age        TEXT,
                contact    TEXT,
                purok_id   INTEGER,
                gender     TEXT DEFAULT '',
                birthdate  TEXT DEFAULT '',
                status     TEXT DEFAULT 'Registered',
                FOREIGN KEY (purok_id) REFERENCES puroks(id)
            )
        """)
        # Migrate existing tables that may be missing the new columns
        _migrate(conn)
        conn.commit()


def _migrate(conn):
    """Add missing columns to residents table if upgrading from old schema."""
    cursor = conn.execute("PRAGMA table_info(residents)")
    existing = {row[1] for row in cursor.fetchall()}
    if "gender" not in existing:
        conn.execute("ALTER TABLE residents ADD COLUMN gender TEXT DEFAULT ''")
    if "birthdate" not in existing:
        conn.execute("ALTER TABLE residents ADD COLUMN birthdate TEXT DEFAULT ''")
    if "status" not in existing:
        conn.execute("ALTER TABLE residents ADD COLUMN status TEXT DEFAULT 'Registered'")


# ── Puroks ────────────────────────────────────────────────────────────────────
def create_purok_table():
    create_tables()


def add_purok(name):
    with get_connection() as conn:
        conn.execute("INSERT INTO puroks (name) VALUES (?)", (name,))
        conn.commit()


def get_puroks():
    with get_connection() as conn:
        return conn.execute(
            "SELECT id, name FROM puroks ORDER BY name"
        ).fetchall()


def count_puroks():
    with get_connection() as conn:
        return conn.execute("SELECT COUNT(*) FROM puroks").fetchone()[0]


# ── Residents ─────────────────────────────────────────────────────────────────
def add_resident(first_name, last_name, age, contact, purok_id,
                 birthdate="", gender="", status="Registered"):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO residents
                (first_name, last_name, age, contact, purok_id,
                 gender, birthdate, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (first_name, last_name, age, contact, purok_id,
              gender, birthdate, status))
        conn.commit()


def update_resident(resident_id, first_name, last_name, age, contact,
                    birthdate="", gender="", status="Registered"):
    with get_connection() as conn:
        conn.execute("""
            UPDATE residents
            SET first_name=?, last_name=?, age=?, contact=?,
                gender=?, birthdate=?, status=?
            WHERE id=?
        """, (first_name, last_name, age, contact,
              gender, birthdate, status, resident_id))
        conn.commit()


def delete_resident(resident_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM residents WHERE id=?", (resident_id,))
        conn.commit()


def get_residents_by_purok(purok_id):
    """
    Returns rows as:
    (id, first_name, last_name, age, contact, purok_id, gender, birthdate, status)
    """
    with get_connection() as conn:
        return conn.execute("""
            SELECT id, first_name, last_name, age, contact, purok_id,
                   gender, birthdate, status
            FROM residents
            WHERE purok_id=?
            ORDER BY last_name, first_name
        """, (purok_id,)).fetchall()


def count_residents():
    with get_connection() as conn:
        return conn.execute("SELECT COUNT(*) FROM residents").fetchone()[0]