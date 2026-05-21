# 🏛️ RIMS — Resident Information Management System

### Barangay Edition v1.0

A full-featured desktop application built with **Python** and **Tkinter** for managing barangay residents, puroks, and user accounts. Designed for local government units (LGUs) to efficiently record, update, organize, and analyze resident data at the purok level.

---

## 📋 Table of Contents

- [Key Features](#-key-features)
- [Benefits](#-benefits)
- [System Requirements](#%EF%B8%8F-system-requirements)
- [Installation](#-installation)
- [How to Use](#-how-to-use)
- [Project Structure](#-project-structure)
- [Database Schema](#-database-schema)
- [Building the .exe](#-building-the-exe)
- [Troubleshooting](#-troubleshooting)
- [Built With](#%EF%B8%8F-built-with)
- [Authors & License](#-authors--license)

---

## ✨ Key Features

### 🔐 Authentication & User Management

| Feature | Description |
|---------|-------------|
| **Secure Login** | Password-based authentication with SHA-256 hashing (peppered) |
| **Account Registration** | New users register with a secret registration code |
| **Role-Based Access** | 4 roles: Barangay Worker, Staff, Barangay Official, Admin |
| **Account Approval** | Admins approve or reject new user accounts |
| **Password Reset** | Admins/Staff can reset any user's password |
| **Remember Me** | Save login credentials locally for quick access |
| **Audit Log** | All approvals, rejections, and password resets are logged with timestamps |

### 🏘️ Purok Management

| Feature | Description |
|---------|-------------|
| **Purok CRUD** | Add, delete, archive, and restore puroks |
| **Location Data** | Built-in Philippine locations (Regions, Provinces, Cities, Barangays) — preloaded with **Davao Region**, **Metro Manila**, **Central Visayas**, and **Northern Mindanao** data |
| **Smart Filtering** | Cascade dropdowns — selecting a Region filters Provinces, which filters Cities, etc. |
| **Archive/Restore** | Soft-delete puroks instead of permanent removal; restore them anytime |
| **Live Search** | Filter puroks by name, province, city, or barangay in real-time |
| **Right-Click Menu** | Quick access to delete or archive from the list |

### 👥 Resident Registry

| Feature | Description |
|---------|-------------|
| **Full CRUD** | Add, update, delete, and view residents |
| **Calendar Picker** | Visual date picker for birthdate selection with year/month navigation |
| **Photo Capture** | Take a photo using your webcam or browse for an image file |
| **Photo Preview** | Circular photo thumbnails with auto-generated initials fallback |
| **Gender & Status** | Dropdown selectors for Gender (Male/Female/Other) and Status (Registered/Pending/Inactive) |
| **Live Search** | Search residents instantly by any field (name, contact, etc.) |
| **Clickable Table Headers** | Sort residents by ID, Name, Age, Gender, etc. — ascending/descending |
| **Status Tabs** | Filter the table by All, Registered, Pending, or Inactive |
| **Age Calculation** | Automatic age computation from birthdate |
| **Resident Profile** | Detailed popup view with photo, personal info, age indicator bar, and status badge |

### 📊 Dashboard & Analytics

| Feature | Description |
|---------|-------------|
| **Login Dashboard** | See total residents and puroks at a glance |
| **Horizontal Bar Charts** | Visual distribution of status, gender, and age groups |
| **Dashboard Refresh** | One-click refresh to update all charts and stats |
| **Stats Bar** | Real-time counts for total, registered, pending, inactive, seniors 60+, male, and female residents |
| **Last Updated** | Timestamp showing when stats were last refreshed |

### 📤 Data Management

| Feature | Description |
|---------|-------------|
| **CSV Export** | Export all residents or selected residents to CSV |
| **CSV Import** | Batch-import residents from a CSV file |
| **Print List** | Generate a print-friendly HTML report that opens in your browser |
| **Batch Operations** | Select multiple residents and delete or export them all at once |

### 🎨 UI Customization

| Feature | Description |
|---------|-------------|
| **3 Themes** | Dark, Light, and Forest themes — toggle with one click from any screen |
| **Font Scaling** | Choose Small (A⁻), Medium (A), or Large (A⁺) font sizes |
| **Persistent Settings** | Theme and font scale preferences are saved between sessions |
| **Fullscreen Mode** | Toggle fullscreen on/off in the Purok Management window |

### 🛡️ Admin Panel

| Feature | Description |
|---------|-------------|
| **Pending Approvals** | Review, approve, or reject new user registrations |
| **Audit Log Viewer** | Browse all account actions (approvals, rejections, password resets) |
| **Password Reset** | Select any user and set a new password with strength indicator |
| **Registration Code** | Change the secret code required for new account registration |
| **Select/Deselect All** | Bulk-approve or reject with select-all / deselect-all helpers |
| **Double-Click Approve** | Double-click a pending user row to quickly approve |

---

## 🎯 Benefits

### For Barangay LGUs
- **Centralized Records** — All resident data stored in one place, accessible instantly
- **Offline-First** — Runs entirely locally with no internet required; data stays on your computer
- **Paperless** — Reduce physical file cabinets and manual record-keeping
- **Standalone .exe** — No Python or technical setup needed for end users

### For Admins & Staff
- **Role-Based Control** — Assign permissions so the right people have the right access
- **Audit Trail** — Every admin action is logged for accountability
- **Easy Data Migration** — CSV import/export makes it simple to move data between systems
- **Visual Analytics** — Charts and stats give instant insight into community demographics

### For Daily Operations
- **Quick Search** — Find any resident or purok in seconds
- **Photo Identification** — Attach photos to resident records for easy identification
- **Batch Processing** — Handle multiple residents at once with batch operations
- **Printable Reports** — Generate formatted resident lists for meetings and documentation

---

## 🖥️ System Requirements

### Minimum Requirements
| Component | Requirement |
|-----------|-------------|
| **OS** | Windows 10 / 11 (64-bit) |
| **RAM** | 512 MB |
| **Storage** | 100 MB free space |
| **Display** | 1280 × 720 resolution |
| **Python** | Not required (use the .exe build) |

### For Running from Source
| Component | Requirement |
|-----------|-------------|
| **OS** | Windows 10 / 11, macOS 12+, or Linux (X11) |
| **Python** | 3.8 or higher |
| **RAM** | 512 MB |
| **Storage** | 200 MB (including virtual environment) |
| **Webcam** | Optional — for photo capture feature |

### Python Dependencies
```
altgraph==0.17.5
babel==2.18.0
cefpython3==66.1
numpy==2.4.6
opencv-python==4.13.0.92
packaging==26.2
pefile==2024.8.26
pillow==12.2.0
pyinstaller==6.20.0
pyinstaller-hooks-contrib==2026.5
pywin32==311
pywin32-ctypes==0.2.3
setuptools==82.0.1
tkcalendar==1.6.1
tkinterweb==4.25.2
tkinterweb-tkhtml==2.1.1
voxe==0.0.4
webview2==0.0.4
wheel==0.47.0
```

---

## 🚀 Installation

### Option 1: Download the .exe (Easiest — No Python Needed)

1. Go to the **Releases** page or get the `RIMS.exe` file from the `dist/` folder
2. **Do not delete** the `residents.db` and `users.db` files inside `dist/` — they contain your data
3. Run `RIMS.exe` to start the application
4. On first run, the database files are created automatically

> ⚠️ **Important:** Keep the `.exe` and `.db` files in the same folder. The databases store all your resident and user data.

### Option 2: Run from Source (For Developers)

#### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

#### Step 1: Get the Code
```bash
git clone https://github.com/yourusername/RIMS.git
cd RIMS
```

#### Step 2: Set Up Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Run the Application
```bash
python main.py
```

The application will launch showing the **Login** screen. Databases are created automatically on first run.

---

## 📖 How to Use

### First-Time Setup

1. **Launch the app** — The login screen appears with a dashboard on the right
2. **Create an account** — Click "Create Account →" below the login form
3. **Enter registration code** — Default code is `RIMS-2026` (can be changed in Admin Panel)
4. **Select a role** — Choose your role (e.g., Admin, Barangay Official)
5. **First admin auto-approved** — The first Admin/Barangay Official to register is automatically approved
6. **Log in** — Use your new credentials to sign in

### Managing Puroks

1. **Login** — Enter your credentials and click **SIGN IN**
2. **Purok Management** — The Purok Management window opens in fullscreen
3. **Add a Purok**:
   - Select **Region**, **Province**, **City/Municipality**, and **Barangay** from the cascading dropdowns
   - Enter the **Purok Name**
   - Click **+ Add**
4. **Navigate** — Select a purok and click **OPEN RESIDENTS →**
5. **Right-Click** — Right-click any purok to **Archive** or **Delete**
6. **Archived Puroks** — Click "Show Archived Puroks" to view, restore, or permanently delete
7. **Search** — Type in the search bar to filter puroks in real-time

### Managing Residents

1. **Add a Resident**:
   - Fill in **First Name**, **Last Name**
   - Select **Birthdate** using the calendar picker (age is auto-calculated)
   - Select **Gender** and **Status**
   - Enter **Contact** number
   - Optionally **Browse** for a photo or use the **Camera** to capture one
   - Click **+ Add Resident**
2. **Update** — Click a resident row, the form fills automatically. Edit and click **Update Selected**
3. **Delete** — Select a resident and click **Delete Selected**
4. **View Profile** — Double-click any resident row to open the **Resident Profile** popup with photo, info, and age indicator
5. **Search** — Use the top search bar to filter residents by any field
6. **Sort** — Click any column header to sort ascending/descending
7. **Filter by Status** — Click the tab buttons (All / Registered / Pending / Inactive)
8. **Export** — Click **Export** to save all or selected residents as CSV
9. **Import** — Click **Import** to bulk-add residents from a CSV file
10. **Print** — Click **Print** to generate a formatted HTML report

### Using the Dashboard

- **Login Screen Dashboard** — View totals for residents and puroks, plus bar charts for gender, status, and age distribution
- **Resident Registry Stats** — The stats bar shows real-time counts for total, registered, pending, inactive, seniors, male, and female
- **Refresh** — Click the **Refresh** button to update all charts and stats

### Admin Panel Access

1. On the **Login** screen, enter your admin credentials and click **⚙ ADMIN PANEL**
2. Or, from the **Purok** or **Resident** screens, click **⚙ ADMIN** and enter your password
3. **Pending Approvals** — Approve or reject new account requests
4. **Audit Log** — View a timestamped log of all admin actions
5. **Password Reset** — Select a user and set a new password (with strength indicator)
6. **Settings** — Change the registration code required for new accounts

### Changing Themes & Font Size

- **Theme Toggle** — On any window (Login, Purok Management), look for the theme button (☀ / 🌲 / ☾) in the title bar and click to cycle through **Dark**, **Light**, and **Forest** themes
- **Font Scale** — Click **A⁻** (small), **A** (medium), or **A⁺** (large) buttons to adjust text size
- All preferences are saved and persist between sessions

---

## 📁 Project Structure

```
RIMS/
│
├── main.py                  # Entry point — creates DB tables and launches login
├── login.py                 # Login window with authentication, dashboard, charts
├── register.py              # New account registration window
├── purok.py                 # Purok management — add, search, archive, delete
├── ui.py                    # Resident registry — CRUD, search, batch ops, export/import
├── resident_info.py         # Resident profile popup with photo, details, age bar
├── camera_capture.py        # Webcam capture and photo browsing popup
├── admin_panel.py           # Admin Panel — approvals, audit log, password reset, settings
├── database.py              # SQLite handler — puroks & residents tables
├── users_database.py        # SQLite handler — users, roles, audit log, config
├── theme.py                 # Dynamic theme system (dark/light/forest) + font scaling
├── logo.py                  # Reusable RIMS logo canvas widget
├── check_errors.py          # Diagnostics tool — validates all modules
│
├── requirements.txt         # Python dependencies
├── RIMS.spec                # PyInstaller build spec
│
├── resident_photos/         # Captured/browsed resident photos (auto-created)
├── dist/                    # PyInstaller build output — contains RIMS.exe
├── build/                   # PyInstaller temporary build files
│
├── residents.db             # SQLite database — puroks & residents (auto-created)
├── users.db                 # SQLite database — user accounts & config (auto-created)
│
└── README.md                # This documentation
```

> **Note:** The `*.db`, `dist/`, `build/`, `resident_photos/`, and `__pycache__/` are excluded from the repository but are listed here so you understand the full project layout.

---

## 🗂️ Database Schema

### `residents.db` — Residents Table

| Column       | Type    | Description                         |
|--------------|---------|-------------------------------------|
| `id`         | INTEGER | Primary key, auto-increment          |
| `first_name` | TEXT    | Resident's first name (required)     |
| `last_name`  | TEXT    | Resident's last name (required)      |
| `age`        | TEXT    | Auto-calculated from birthdate        |
| `contact`    | TEXT    | Contact number                       |
| `purok_id`   | INTEGER | Foreign key → `puroks(id)`           |
| `gender`     | TEXT    | Male / Female / Other                |
| `birthdate`  | TEXT    | Date in YYYY-MM-DD format            |
| `status`     | TEXT    | Registered / Pending / Inactive      |
| `photo_path` | TEXT    | Path to resident photo file          |

### `residents.db` — Puroks Table

| Column     | Type    | Description                        |
|------------|---------|------------------------------------|
| `id`       | INTEGER | Primary key, auto-increment         |
| `name`     | TEXT    | Purok name (required, unique)       |
| `region`   | TEXT    | Region (preloaded from PH data)     |
| `province` | TEXT    | Province                           |
| `city`     | TEXT    | City / Municipality                |
| `barangay` | TEXT    | Barangay                           |
| `archived` | INTEGER | 0 = active, 1 = archived (soft-delete) |

### `users.db` — Users Table

| Column       | Type    | Description                        |
|--------------|---------|------------------------------------|
| `id`         | INTEGER | Primary key, auto-increment         |
| `username`   | TEXT    | Unique username (required)          |
| `password`   | TEXT    | SHA-256 hashed + peppered password  |
| `first_name` | TEXT    | User's first name                   |
| `last_name`  | TEXT    | User's last name                    |
| `email`      | TEXT    | Email address                       |
| `phone`      | TEXT    | Phone number                        |
| `role`       | TEXT    | Barangay Worker / Staff / Barangay Official / Admin |
| `approved`   | INTEGER | 0 = pending, 1 = approved           |

### `users.db` — App Config Table

| Key                 | Value        | Description                         |
|---------------------|--------------|-------------------------------------|
| `registration_code` | `RIMS-2024`  | Code required for new registrations |
| `theme`             | `dark`       | Saved theme preference              |
| `font_scale`        | `medium`     | Saved font scale preference         |

### `users.db` — Audit Log Table

| Column      | Type    | Description                        |
|-------------|---------|------------------------------------|
| `id`        | INTEGER | Primary key, auto-increment         |
| `timestamp` | TEXT    | Timestamp of the action             |
| `action`    | TEXT    | approved / rejected / password_reset |
| `acted_on`  | TEXT    | Username of affected user           |
| `acted_by`  | TEXT    | Username of admin who performed action |

---

## 📦 Building the .exe

To compile the application into a standalone Windows executable:

### Using PyInstaller Directly
```bash
pyinstaller --clean --onefile --windowed --name "RIMS" --icon=rims_icon.ico main.py
```

### Using the Spec File (Recommended)
```bash
pyinstaller --clean RIMS.spec
```

The output will be in the `dist/` folder as `RIMS.exe`.

> ⚠️ **Important:** When distributing the `.exe`, you must include:
> - `RIMS.exe` (the compiled application)
> - `residents.db` (your resident data)
> - `users.db` (your user accounts)
> - `resident_photos/` folder (resident photos)

---

## 🔧 Troubleshooting

### "No camera found"
- Ensure your webcam is connected and not in use by another application
- The app supports both built-in and USB webcams
- You can also use the **Browse** button to select a photo file instead

### "Registration code is incorrect"
- Default code is `RIMS-2024`
- Ask your Barangay Admin for the current code
- Admins can change the code in Admin Panel → Settings

### "Account Pending" on login
- Your account has not been approved yet
- Contact a Barangay Official or Admin to approve your account
- The first Admin to register is auto-approved

### Database errors
- If you encounter database issues, check that `.db` files are not set to read-only
- Backup your `.db` files and delete them (they will be recreated on next launch)
- ⚠️ **This will delete all data** — only do this if you have a backup

### "Module not found" errors (running from source)
- Make sure your virtual environment is activated
- Run `pip install -r requirements.txt` to install all dependencies
- Verify you're using Python 3.8 or higher with `python --version`

---

## 🛠️ Built With

| Technology | Purpose |
|------------|---------|
| [Python 3](https://www.python.org/) | Core programming language |
| [Tkinter](https://docs.python.org/3/library/tkinter.html) | GUI framework — native desktop UI |
| [SQLite3](https://www.sqlite.org/) | Local database — zero configuration, files are portable |
| [Pillow](https://python-pillow.org/) | Image processing — photo thumbnails, circular masks, avatars |
| [OpenCV](https://opencv.org/) | Camera capture — webcam photo capture |
| [NumPy](https://numpy.org/) | Numerical processing (OpenCV dependency) |
| [PyInstaller](https://pyinstaller.org/) | Application packaging into standalone .exe |

### Architecture Highlights

- **Dynamic Theme System** — Module-level attribute resolution via `__getattr__` allows theme switching without re-importing
- **Font Scaling** — All font sizes are computed with a multiplier; changing the scale factor instantly affects the entire UI
- **Database Migrations** — Automatic column additions via `PRAGMA table_info` ensure backward compatibility as the schema evolves
- **Role Hierarchy** — Permission levels with numeric indices enable simple `>=` comparison for access control
- **Audit Trail** — All admin actions are logged with timestamps and actor information

---

## 👥 Authors & License

### Authors
- **Reynald** — Lead Developer
- **Arl** — Developer

### License
This project is developed for **academic** and **local government** administrative use.

© Barangay Management System · v1.0

---

> 📬 For questions, bug reports, or feature requests, please open an issue on the project repository.
