# 🏛️ RIMS — Resident Information Management System
### Barangay Edition v1.0

A desktop application built with Python and Tkinter for managing barangay residents, puroks, and user accounts. Designed for local government units to efficiently record, update, and organize resident data.

---

## ✨ Features

- 🔐 **Secure Login & Registration** — role-based access for Barangay Officials and Workers
- 🏘️ **Purok Management** — add and organize puroks with ease
- 👥 **Resident Registry** — add, update, delete, and search residents per purok
- 📤 **CSV Export / Import** — backup and restore resident data
- 🔍 **Live Search** — filter residents instantly by name or contact
- 📊 **System Overview** — see total residents and puroks at a glance
- 🖥️ **Standalone .exe** — runs without Python installed

---

## 📁 Project Structure

```
RIMS/
│
├── main.py                  # Entry point — launches the login window
├── login.py                 # Login window with authentication
├── register.py              # Create account window
├── purok.py                 # Purok management window
├── ui.py                    # Resident registry window
├── logo.py                  # Shared RIMS logo canvas widget
│
├── database.py              # SQLite handler — puroks & residents
├── users_database.py        # SQLite handler — user accounts
│
├── images/                  # App image assets
│
├── rims_icon.ico            # App icon (used for .exe build)
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

> **Note:** The following are auto-generated and excluded from the repository:
> - `*.db` — SQLite database files (created automatically on first run)
> - `dist/` — PyInstaller build output containing `RIMS.exe`
> - `build/` — PyInstaller temporary files
> - `__pycache__/` — Python bytecode cache
> - `.venv/` — Virtual environment

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/RIMS.git
   cd RIMS
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**
   ```bash
   python main.py
   ```

The database files (`residents.db` and `users.db`) will be created automatically on first run.

---

## 📦 Building the .exe

To compile into a standalone Windows executable:

```bash
pyinstaller --clean --onefile --windowed --name "RIMS" --icon=rims_icon.ico main.py
```

The output will be in the `dist/` folder as `RIMS.exe`.

> ⚠️ Do not delete the `.db` files inside `dist/` — they contain your live data.

---

## 🗂️ Database Schema

### `residents.db`
| Column       | Type    | Description              |
|--------------|---------|--------------------------|
| id           | INTEGER | Primary key              |
| first_name   | TEXT    | Resident's first name    |
| last_name    | TEXT    | Resident's last name     |
| age          | TEXT    | Resident's age           |
| contact      | TEXT    | Contact number           |
| purok_id     | INTEGER | Foreign key → puroks     |

### `users.db`
| Column       | Type    | Description              |
|--------------|---------|--------------------------|
| id           | INTEGER | Primary key              |
| username     | TEXT    | Unique username          |
| password     | TEXT    | Hashed password          |
| first_name   | TEXT    | User's first name        |
| last_name    | TEXT    | User's last name         |
| email        | TEXT    | Email address            |
| phone        | TEXT    | Phone number             |

---

## 🖥️ Screenshots

> _Add your screenshots here_

---

## 🛠️ Built With

- [Python 3](https://www.python.org/) — core language
- [Tkinter](https://docs.python.org/3/library/tkinter.html) — GUI framework
- [SQLite3](https://www.sqlite.org/) — local database
- [PyInstaller](https://pyinstaller.org/) — packaging to .exe

---

## 👥 Authors

- **Reynald** — developer
- **Arl** — developer

---

## 📄 License

This project is for academic and local government use.  
© Barangay Management System · v1.0

![Project Structure](images/rims_project_structure.png)
