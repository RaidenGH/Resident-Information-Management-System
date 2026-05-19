import sqlite3
import os

DB_NAME = "residents.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_tables():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS puroks (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                name     TEXT NOT NULL UNIQUE,
                region   TEXT DEFAULT '',
                city     TEXT DEFAULT '',
                barangay TEXT DEFAULT ''
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
                photo_path TEXT DEFAULT '',
                FOREIGN KEY (purok_id) REFERENCES puroks(id)
            )
        """)
        _migrate(conn)
        conn.commit()


def _migrate(conn):
    # ── residents columns ─────────────────────────────────────────────────────
    cursor = conn.execute("PRAGMA table_info(residents)")
    res_cols = {row[1] for row in cursor.fetchall()}
    if "gender" not in res_cols:
        conn.execute("ALTER TABLE residents ADD COLUMN gender TEXT DEFAULT ''")
    if "birthdate" not in res_cols:
        conn.execute("ALTER TABLE residents ADD COLUMN birthdate TEXT DEFAULT ''")
    if "status" not in res_cols:
        conn.execute("ALTER TABLE residents ADD COLUMN status TEXT DEFAULT 'Registered'")
    if "photo_path" not in res_cols:
        conn.execute("ALTER TABLE residents ADD COLUMN photo_path TEXT DEFAULT ''")

    # ── puroks location + archive columns ────────────────────────────────────
    cursor = conn.execute("PRAGMA table_info(puroks)")
    purok_cols = {row[1] for row in cursor.fetchall()}
    if "region" not in purok_cols:
        conn.execute("ALTER TABLE puroks ADD COLUMN region TEXT DEFAULT ''")
    if "city" not in purok_cols:
        conn.execute("ALTER TABLE puroks ADD COLUMN city TEXT DEFAULT ''")
    if "barangay" not in purok_cols:
        conn.execute("ALTER TABLE puroks ADD COLUMN barangay TEXT DEFAULT ''")
    if "archived" not in purok_cols:
        conn.execute("ALTER TABLE puroks ADD COLUMN archived INTEGER DEFAULT 0")


# ── Puroks ────────────────────────────────────────────────────────────────────
def create_purok_table():
    create_tables()


def add_purok(name, region="", city="", barangay=""):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO puroks (name, region, city, barangay) VALUES (?, ?, ?, ?)",
            (name, region, city, barangay)
        )
        conn.commit()


def get_puroks():
    with get_connection() as conn:
        return conn.execute(
            "SELECT id, name, region, city, barangay FROM puroks "
            "WHERE archived = 0 ORDER BY name"
        ).fetchall()


def delete_purok(purok_id):
    """Permanently remove a purok and unlink its residents."""
    with get_connection() as conn:
        conn.execute("UPDATE residents SET purok_id = NULL WHERE purok_id = ?",
                     (purok_id,))
        conn.execute("DELETE FROM puroks WHERE id = ?", (purok_id,))
        conn.commit()


def archive_purok(purok_id):
    """Soft-delete: hide from list but keep data intact."""
    with get_connection() as conn:
        conn.execute("UPDATE puroks SET archived = 1 WHERE id = ?", (purok_id,))
        conn.commit()


def restore_purok(purok_id):
    """Un-archive a previously archived purok."""
    with get_connection() as conn:
        conn.execute("UPDATE puroks SET archived = 0 WHERE id = ?", (purok_id,))
        conn.commit()


def get_archived_puroks():
    """Return all archived puroks."""
    with get_connection() as conn:
        return conn.execute(
            "SELECT id, name, region, city, barangay FROM puroks "
            "WHERE archived = 1 ORDER BY name"
        ).fetchall()


def count_puroks():
    with get_connection() as conn:
        return conn.execute("SELECT COUNT(*) FROM puroks").fetchone()[0]


# ── Residents ─────────────────────────────────────────────────────────────────
def add_resident(first_name, last_name, age, contact, purok_id,
                 birthdate="", gender="", status="Registered", photo_path=""):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO residents
                (first_name, last_name, age, contact, purok_id,
                 gender, birthdate, status, photo_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (first_name, last_name, age, contact, purok_id,
              gender, birthdate, status, photo_path))
        conn.commit()


def update_resident(resident_id, first_name, last_name, age, contact,
                    birthdate="", gender="", status="Registered", photo_path=None):
    with get_connection() as conn:
        if photo_path is not None:
            conn.execute("""
                UPDATE residents
                SET first_name=?, last_name=?, age=?, contact=?,
                    gender=?, birthdate=?, status=?, photo_path=?
                WHERE id=?
            """, (first_name, last_name, age, contact,
                  gender, birthdate, status, photo_path, resident_id))
        else:
            conn.execute("""
                UPDATE residents
                SET first_name=?, last_name=?, age=?, contact=?,
                    gender=?, birthdate=?, status=?
                WHERE id=?
            """, (first_name, last_name, age, contact,
                  gender, birthdate, status, resident_id))
        conn.commit()


def update_photo(resident_id, photo_path):
    with get_connection() as conn:
        conn.execute("UPDATE residents SET photo_path=? WHERE id=?",
                     (photo_path, resident_id))
        conn.commit()


def delete_resident(resident_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM residents WHERE id=?", (resident_id,))
        conn.commit()


def get_residents_by_purok(purok_id):
    """
    Returns rows as:
    (id, first_name, last_name, age, contact, purok_id,
     gender, birthdate, status, photo_path)
    """
    with get_connection() as conn:
        return conn.execute("""
            SELECT id, first_name, last_name, age, contact, purok_id,
                   gender, birthdate, status, photo_path
            FROM residents
            WHERE purok_id=?
            ORDER BY last_name, first_name
        """, (purok_id,)).fetchall()


def get_resident_by_id(resident_id):
    with get_connection() as conn:
        return conn.execute("""
            SELECT id, first_name, last_name, age, contact, purok_id,
                   gender, birthdate, status, photo_path
            FROM residents WHERE id=?
        """, (resident_id,)).fetchone()


def count_residents():
    with get_connection() as conn:
        return conn.execute("SELECT COUNT(*) FROM residents").fetchone()[0]