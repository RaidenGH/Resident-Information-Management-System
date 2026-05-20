import sqlite3
import hashlib

# ── Salt for password hashing ──────────────────────────────────────────────────
_PEPPER = "RIMS-BARANGAY-2024"

# ── Role hierarchy (higher index = more permissions) ──────────────────────────
ROLES = ["Barangay Worker", "Staff", "Barangay Official", "Admin"]

# ── Permission levels ─────────────────────────────────────────────────────────
def get_role_level(role: str) -> int:
    """Return the permission level index for a role. -1 for unknown roles."""
    try:
        return ROLES.index(role)
    except ValueError:
        return -1


def has_permission(username: str, min_role: str) -> bool:
    """
    Check if an approved user has at least the given role level.
    Example: has_permission('john', 'Staff') returns True for Staff, Official, Admin.
    """
    conn = connect_users_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role FROM users WHERE username=? AND approved=1",
        (username,),
    )
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return False
    return get_role_level(row[0]) >= get_role_level(min_role)


def _hash_password(password: str) -> str:
    """Return a SHA-256 hex digest of the password combined with the pepper."""
    return hashlib.sha256((password + _PEPPER).encode()).hexdigest()


def connect_users_db():
    return sqlite3.connect("users.db")


def create_users_table():
    conn = connect_users_db()
    cursor = conn.cursor()

    # Main users table
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
    # Migrate: add new columns if missing
    for col, dtype in [("role", "TEXT DEFAULT 'Barangay Worker'"),
                       ("approved", "INTEGER DEFAULT 0")]:
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {dtype}")
        except sqlite3.OperationalError:
            pass  # Column already exists

    # App config table (registration code etc.)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_config (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    cursor.execute(
        "INSERT OR IGNORE INTO app_config (key, value) VALUES ('registration_code', 'RIMS-2024')"
    )

    # Audit log table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            action TEXT NOT NULL,
            acted_on TEXT NOT NULL,
            acted_by TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# ── Registration code ─────────────────────────────────────────────────────────

def get_theme_preference() -> str:
    """Return the saved theme preference. Defaults to 'dark'."""
    conn = connect_users_db()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM app_config WHERE key='theme'")
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "dark"


def set_theme_preference(theme: str):
    """Persist the user's theme preference."""
    conn = connect_users_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO app_config (key, value) VALUES ('theme', ?)",
        (theme,),
    )
    conn.commit()
    conn.close()


def get_font_scale_preference() -> str:
    """Return the saved font scale preference. Defaults to 'medium'."""
    conn = connect_users_db()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM app_config WHERE key='font_scale'")
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "medium"


def set_font_scale_preference(level: str):
    """Persist the user's font scale preference."""
    conn = connect_users_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO app_config (key, value) VALUES ('font_scale', ?)",
        (level,),
    )
    conn.commit()
    conn.close()


def get_registration_code() -> str:
    conn = connect_users_db()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM app_config WHERE key='registration_code'")
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "RIMS-2024"


def set_registration_code(code: str):
    conn = connect_users_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO app_config (key, value) VALUES ('registration_code', ?)",
        (code,),
    )
    conn.commit()
    conn.close()


# ── User management ───────────────────────────────────────────────────────────

def add_user(username, password, first_name, last_name, email, phone,
             role="Barangay Worker"):
    conn = connect_users_db()
    cursor = conn.cursor()

    # Auto-approve only if this is the first Admin or Barangay Official registering
    # This ensures at least one person can use the Admin Panel to approve others
    cursor.execute(
        "SELECT COUNT(*) FROM users WHERE approved=1 AND (role='Admin' OR role='Barangay Official')"
    )
    admin_count = cursor.fetchone()[0]
    approved = 1 if (admin_count == 0 and get_role_level(role) >= get_role_level("Barangay Official")) else 0

    cursor.execute("""
        INSERT INTO users (username, password, first_name, last_name,
                           email, phone, role, approved)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, _hash_password(password), first_name,
          last_name, email, phone, role, approved))
    conn.commit()
    conn.close()


def check_login_status(username, password):
    """
    Returns one of:
        "approved"  — credentials correct & account approved
        "pending"   — credentials correct but not yet approved
        "invalid"   — wrong username or password
    """
    conn = connect_users_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT password, approved FROM users WHERE username=?",
        (username,),
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return "invalid"
    stored_hash, approved = row
    if stored_hash != _hash_password(password):
        return "invalid"
    return "approved" if approved else "pending"


def validate_login(username, password):
    return check_login_status(username, password) == "approved"


def can_access_admin_panel(username) -> bool:
    """
    Check if an approved user can access the Admin Panel.
    Returns True for Staff, Barangay Official, and Admin.
    Used by login.py, purok.py, and ui.py to show admin buttons.
    """
    return has_permission(username, "Staff")


def is_admin(username) -> bool:
    conn = connect_users_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role FROM users WHERE username=? AND approved=1",
        (username,),
    )
    row = cursor.fetchone()
    conn.close()
    return row is not None and get_role_level(row[0]) >= get_role_level("Barangay Official")


def get_user_role(username: str) -> str:
    """Return the role of an approved user, or empty string if not found."""
    conn = connect_users_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role FROM users WHERE username=? AND approved=1",
        (username,),
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else ""


def count_admins() -> int:
    conn = connect_users_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM users WHERE approved=1 AND (role='Admin' OR role='Barangay Official')"
    )
    count = cursor.fetchone()[0]
    conn.close()
    return count


# ── Pending user approval ─────────────────────────────────────────────────────

def get_pending_users():
    """Return list of (id, username, first_name, last_name, email, phone, role)."""
    conn = connect_users_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, first_name, last_name, email, phone, role "
        "FROM users WHERE approved=0 ORDER BY id"
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_users():
    """Return list of (id, username, first_name, last_name, email, phone, role, approved)."""
    conn = connect_users_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, first_name, last_name, email, phone, role, approved "
        "FROM users ORDER BY id"
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def approve_user(user_id: int, acted_by: str = "unknown"):
    conn = connect_users_db()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE id=?", (user_id,))
    row = cursor.fetchone()
    if row is None:
        conn.close()
        return
    username = row[0]
    cursor.execute("UPDATE users SET approved=1 WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    # Log after closing to avoid SQLite locking on Windows
    log_audit_entry("approved", username, acted_by)


def reject_user(user_id: int, acted_by: str = "unknown"):
    """Delete a pending user entirely."""
    conn = connect_users_db()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE id=? AND approved=0", (user_id,))
    row = cursor.fetchone()
    if row is None:
        conn.close()
        return
    username = row[0]
    cursor.execute("DELETE FROM users WHERE id=? AND approved=0", (user_id,))
    conn.commit()
    conn.close()
    # Log after closing to avoid SQLite locking on Windows
    log_audit_entry("rejected", username, acted_by)


# ── Audit log ────────────────────────────────────────────────────────────────

def log_audit_entry(action: str, acted_on: str, acted_by: str):
    """Record an action in the audit log."""
    from datetime import datetime
    conn = connect_users_db()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute(
        "INSERT INTO audit_log (timestamp, action, acted_on, acted_by) VALUES (?, ?, ?, ?)",
        (timestamp, action, acted_on, acted_by),
    )
    conn.commit()
    conn.close()


def get_audit_log(limit: int = 100):
    """Return list of (id, timestamp, action, acted_on, acted_by) ordered newest first."""
    conn = connect_users_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, timestamp, action, acted_on, acted_by "
        "FROM audit_log ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


# ── Password reset ────────────────────────────────────────────────────────────

def reset_password(username: str, new_password: str, acted_by: str = "unknown") -> bool:
    """
    Reset a user's password. Returns True on success, False if user not found.
    Logs the action to the audit log.
    """
    conn = connect_users_db()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    if row is None:
        conn.close()
        return False
    cursor.execute(
        "UPDATE users SET password=? WHERE username=?",
        (_hash_password(new_password), username),
    )
    conn.commit()
    conn.close()
    log_audit_entry("password_reset", username, acted_by)
    return True


def get_approved_users():
    """Return list of (id, username, first_name, last_name, role) for approved users."""
    conn = connect_users_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, first_name, last_name, role "
        "FROM users WHERE approved=1 ORDER BY username"
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


# ── Remember Me ────────────────────────────────────────────────────────────────

def save_remembered_credentials(username: str, password: str):
    """Save remembered username and password to app_config."""
    conn = connect_users_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO app_config (key, value) VALUES ('remember_username', ?)",
        (username,),
    )
    cursor.execute(
        "INSERT OR REPLACE INTO app_config (key, value) VALUES ('remember_password', ?)",
        (password,),
    )
    conn.commit()
    conn.close()


def get_remembered_credentials():
    """Return (username, password) if saved, or (None, None)."""
    conn = connect_users_db()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM app_config WHERE key='remember_username'")
    urow = cursor.fetchone()
    cursor.execute("SELECT value FROM app_config WHERE key='remember_password'")
    prow = cursor.fetchone()
    conn.close()
    if urow and prow:
        return urow[0], prow[0]
    return None, None


def clear_remembered_credentials():
    """Remove saved remembered credentials."""
    conn = connect_users_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM app_config WHERE key='remember_username'")
    cursor.execute("DELETE FROM app_config WHERE key='remember_password'")
    conn.commit()
    conn.close()
