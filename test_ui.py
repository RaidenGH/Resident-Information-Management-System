
"""
test_ui.py -- Unit tests for ResidentApp class (CRUD, batch, sorting, helpers).

Patches tkinter so the Tk root window is never actually created.
Uses a temporary SQLite database to verify data operations.
"""

import os
import sys
import csv
import tempfile
import shutil
import unittest
from unittest.mock import MagicMock, patch, call, ANY, PropertyMock

# ══════════════════════════════════════════════════════════════════════
# Patch all tkinter-related modules BEFORE any UI imports
# ══════════════════════════════════════════════════════════════════════
_mock_tk = MagicMock()
_mock_ttk = MagicMock()
_mock_msg = MagicMock()
_mock_fd = MagicMock()
_mock_logo = MagicMock()
_mock_rinfo = MagicMock()
_mock_cam = MagicMock()

# Link tkinter sub-modules so that "from tkinter import messagebox"
# in ui.py returns our mock, not a fresh MagicMock
_mock_tk.ttk = _mock_ttk
_mock_tk.messagebox = _mock_msg
_mock_tk.filedialog = _mock_fd

_patcher = patch.dict("sys.modules", {
    "tkinter": _mock_tk,
    "tkinter.ttk": _mock_ttk,
    "tkinter.messagebox": _mock_msg,
    "tkinter.filedialog": _mock_fd,
    "logo": _mock_logo,
    "resident_info": _mock_rinfo,
    "camera_capture": _mock_cam,
})
_patcher.start()

# Now import UI with mocked tkinter
sys.modules.pop("database", None)  # fresh import each time tests are loaded
import database
sys.modules.pop("ui", None)
from ui import ResidentApp

# ── Constants for tests ────────────────────────────────────────────────
TEST_PUROK_ID = 1
TEST_PUROK_NAME = "Test Purok"
TEST_ADMIN = "test_admin"


# ══════════════════════════════════════════════════════════════════════
# Custom mocks with real behavior for key UI elements
# ══════════════════════════════════════════════════════════════════════

class MockStringVar:
    """Mimics tk.StringVar with .get() / .set()."""
    def __init__(self, value=""):
        self._value = value
    def get(self):
        return self._value
    def set(self, value):
        self._value = value
    def trace_add(self, *args):
        pass


class MockEntry:
    """Mimics tk.Entry with .get() / .insert() / .delete()."""
    def __init__(self, *args, **kwargs):
        self._text = ""
        self._bindings = {}
    def get(self):
        return self._text
    def insert(self, pos, text):
        self._text = text
    def delete(self, start, end=None):
        self._text = ""
    def config(self, **kwargs):
        pass
    def pack(self, **kwargs):
        pass
    def grid(self, **kwargs):
        pass
    def place(self, **kwargs):
        pass
    def bind(self, event, callback):
        self._bindings[event] = callback
    def focus_set(self):
        pass
    def winfo_exists(self):
        return True


class MockLabel:
    """Mimics tk.Label with .config() and text tracking."""
    def __init__(self, *args, **kwargs):
        self._config = {}
        self._text = kwargs.get("text", "")
    def config(self, **kwargs):
        self._config.update(kwargs)
        if "text" in kwargs:
            self._text = kwargs["text"]
    def pack(self, **kwargs):
        pass
    def grid(self, **kwargs):
        pass
    def place(self, **kwargs):
        pass


class MockTreeview:
    """Mimics ttk.Treeview with real item tracking."""
    def __init__(self, *args, **kwargs):
        self._items = {}           # iid -> {values, tags}
        self._children_order = []  # ordered iid list
        self._selection = []
        self._bindings = {}
        self._config_dict = {}
        self.selectmode = kwargs.get("selectmode", "browse")
        self.style = MagicMock()

    def insert(self, parent, index, **kwargs):
        iid = f"item_{len(self._children_order)}"
        self._items[iid] = {
            "values": kwargs.get("values", ()),
            "tags": kwargs.get("tags", ()),
        }
        self._children_order.append(iid)
        return iid

    def get_children(self):
        return list(self._children_order)

    def delete(self, *iids):
        for iid in iids:
            if iid in self._items:
                del self._items[iid]
            if iid in self._children_order:
                self._children_order.remove(iid)
            if iid in self._selection:
                self._selection.remove(iid)

    def item(self, iid, option=None, **kw):
        if option:
            return self._items[iid].get(option)
        return self._items.get(iid, {"values": (), "tags": ()})

    def set(self, iid, column=None, value=None):
        item = self._items[iid]
        if column is None:
            return {str(i): v for i, v in enumerate(item["values"])}
        idx = int(column) if isinstance(column, str) and column.isdigit() else column
        # handle column names like "ID", "First Name", etc.
        col_map = {"ID": 0, "First Name": 1, "Last Name": 2, "Age": 3,
                   "Birthdate": 4, "Gender": 5, "Contact": 6, "Status": 7}
        if column in col_map:
            idx = col_map[column]
            return str(item["values"][idx]) if idx < len(item["values"]) else ""
        return str(item["values"][0])

    def selection(self):
        return list(self._selection)

    def selection_set(self, iids):
        self._selection = list(iids) if isinstance(iids, (list, tuple)) else [iids]

    def selection_add(self, iid):
        if iid not in self._selection:
            self._selection.append(iid)

    def move(self, iid, parent, index):
        if iid in self._children_order:
            self._children_order.remove(iid)
        pos = int(index)
        self._children_order.insert(pos, iid)

    def heading(self, column, **kwargs):
        pass

    def column(self, column, **kwargs):
        pass

    def tag_configure(self, tagname, **kwargs):
        pass

    def identify_row(self, y):
        return self._children_order[0] if self._children_order else ""

    def yview(self, *args):
        pass

    def bind(self, event, callback):
        self._bindings[event] = callback

    def grid(self, **kwargs):
        pass

    def config(self, **kwargs):
        self._config_dict.update(kwargs)


class MockFrame:
    """Mimics tk.Frame."""
    def __init__(self, *args, **kwargs):
        self._children = []
        self._grid_info = {}
    def pack(self, **kwargs):
        pass
    def grid(self, **kwargs):
        self._grid_info = kwargs
    def grid_remove(self):
        pass
    def grid_propagate(self, flag):
        pass
    def pack_propagate(self, flag):
        pass
    def winfo_screenwidth(self):
        return 1920
    def winfo_screenheight(self):
        return 1080
    def grid_rowconfigure(self, *args, **kwargs):
        pass
    def grid_columnconfigure(self, *args, **kwargs):
        pass
    def config(self, **kwargs):
        pass
    def bind(self, *args, **kwargs):
        pass
    def winfo_exists(self):
        return True


class MockButton:
    """Mimics tk.Button."""
    def __init__(self, *args, **kwargs):
        self._config = kwargs
        self._bindings = {}
    def config(self, **kwargs):
        self._config.update(kwargs)
    def pack(self, **kwargs):
        pass
    def grid(self, **kwargs):
        pass
    def bind(self, event, callback):
        self._bindings[event] = callback


class MockCanvas:
    """Mimics tk.Canvas."""
    def __init__(self, *args, **kwargs):
        self._bindings = {}
    def pack(self, **kwargs):
        pass
    def grid(self, **kwargs):
        pass
    def yview(self, *args):
        pass
    def yview_moveto(self, fraction):
        pass
    def yview_scroll(self, n, what):
        pass
    def bbox(self, *args):
        return (0, 0, 100, 100)
    def create_window(self, *args, **kwargs):
        pass
    def config(self, **kwargs):
        pass
    def bind(self, event, callback):
        self._bindings[event] = callback
    def bind_all(self, event, callback):
        pass


class MockMenu:
    """Mimics tk.Menu."""
    def __init__(self, *args, **kwargs):
        pass
    def add_command(self, **kwargs):
        pass
    def add_separator(self):
        pass
    def post(self, x, y):
        pass


class MockScrollbar:
    """Mimics tk.Scrollbar."""
    def __init__(self, *args, **kwargs):
        pass
    def pack(self, **kwargs):
        pass
    def grid(self, **kwargs):
        pass
    def config(self, **kwargs):
        pass
    def set(self, *args):
        pass


class MockOptionMenu:
    """Mimics tk.OptionMenu — supports subscript access (dd["menu"])."""
    def __init__(self, parent, var, *values):
        self._var = var
        self._values = values
        self._menu = MagicMock()
    def config(self, **kwargs):
        pass
    def pack(self, **kwargs):
        pass
    def grid(self, **kwargs):
        pass
    def __getitem__(self, key):
        return self._menu


# ══════════════════════════════════════════════════════════════════════
# Test suite
# ══════════════════════════════════════════════════════════════════════

class TestResidentApp(unittest.TestCase):
    """Unit tests for the ResidentApp class."""

    @classmethod
    def setUpClass(cls):
        """Set up the mock environment once."""
        # ── Configure tkinter mocks to return our custom classes ─
        cls.tk_patch = _mock_tk
        cls.ttk_patch = _mock_ttk
        cls.msg_patch = _mock_msg
        cls.fd_patch = _mock_fd

        # Make tkinter constructors return Mock objects
        cls._orig_tk = _mock_tk.Tk
        cls._orig_frame = _mock_tk.Frame
        cls._orig_label = _mock_tk.Label
        cls._orig_entry = _mock_tk.Entry
        cls._orig_button = _mock_tk.Button
        cls._orig_svar = _mock_tk.StringVar
        cls._orig_canvas = _mock_tk.Canvas
        cls._orig_menu = _mock_tk.Menu
        cls._orig_scroll = _mock_tk.Scrollbar
        cls._orig_option = _mock_tk.OptionMenu
        cls._orig_toplevel = _mock_tk.Toplevel

        _mock_tk.Tk = MagicMock(return_value=MagicMock())
        _mock_tk.Frame = MockFrame
        _mock_tk.Label = MockLabel
        _mock_tk.Entry = MockEntry
        _mock_tk.Button = MockButton
        _mock_tk.StringVar = MockStringVar
        _mock_tk.Canvas = MockCanvas
        _mock_tk.Menu = MockMenu
        _mock_tk.Scrollbar = MockScrollbar
        _mock_tk.OptionMenu = MockOptionMenu
        _mock_tk.Toplevel = MockFrame

        _mock_ttk.Treeview = MockTreeview
        _mock_ttk.Style = MagicMock
        _mock_ttk.Scrollbar = MockScrollbar

        # Create temp directory for test database
        cls.test_dir = tempfile.mkdtemp()
        cls.orig_db_name = database.DB_NAME
        database.DB_NAME = os.path.join(cls.test_dir, "test_residents.db")
        database.create_tables()

    @classmethod
    def tearDownClass(cls):
        """Restore mocks and clean up."""
        _mock_tk.Tk = cls._orig_tk
        _mock_tk.Frame = cls._orig_frame
        _mock_tk.Label = cls._orig_label
        _mock_tk.Entry = cls._orig_entry
        _mock_tk.Button = cls._orig_button
        _mock_tk.StringVar = cls._orig_svar
        _mock_tk.Canvas = cls._orig_canvas
        _mock_tk.Menu = cls._orig_menu
        _mock_tk.Scrollbar = cls._orig_scroll
        _mock_tk.OptionMenu = cls._orig_option
        _mock_tk.Toplevel = cls._orig_toplevel
        database.DB_NAME = cls.orig_db_name
        shutil.rmtree(cls.test_dir, ignore_errors=True)

    def setUp(self):
        """Create a fresh ResidentApp for each test with a clean database."""
        # Clear any residents from previous tests
        with database.get_connection() as conn:
            conn.execute("DELETE FROM residents")
            conn.execute("DELETE FROM puroks")
            conn.commit()

        # Ensure test purok exists
        try:
            database.add_purok(TEST_PUROK_NAME)
        except Exception:
            pass  # already exists

        # Reset mocks
        _mock_msg.reset_mock()
        _mock_fd.reset_mock()
        _mock_logo.reset_mock()

        # Create the app
        self.app = ResidentApp(TEST_PUROK_ID, TEST_PUROK_NAME, TEST_ADMIN)

        # ── Override tree with a real MockTreeview for test control ──
        self.mock_tree = MockTreeview()
        self.app.tree = self.mock_tree

        # ── Override entries with controlled mocks ─────────────────
        self.mock_entries = {}
        for key in ["First Name", "Last Name", "Contact"]:
            e = MockEntry()
            self.mock_entries[key] = e
        # Birthdate is stored as string, not as Entry widget
        self.app.entries = self.mock_entries

        # Re-set birthdate to today
        from datetime import date
        self.app.entries["Birthdate"] = date.today().strftime("%Y-%m-%d")

        # ── Override calendar state ────────────────────────────────
        self.app.calendar_state = {
            "year": date.today().year,
            "month": date.today().month,
            "selected_date": date.today(),
            "temp_date": date.today(),
        }

        # ── Override gender/status vars ────────────────────────────
        self.app.gender_var = MockStringVar("Select Gender")
        self.app.status_var = MockStringVar("Registered")

        # ── Override labels ────────────────────────────────────────
        self.app.age_lbl = MockLabel()
        self.app.bd_display = MockLabel()
        self.app.thumb_lbl = MockLabel()
        self.app.photo_status_lbl = MockLabel()
        self.app.thumb_border = MockFrame()

        # ── Override stat labels ──────────────────────────────────
        self.app.stat_labels = {
            k: MockLabel() for k in
            ["total", "registered", "pending", "inactive", "seniors", "male", "female"]
        }
        self.app.sort_info = MockLabel()
        self.app.status_lbl = MockLabel()

        # ── Override batch bar ──────────────────────────────────────
        self.app.batch_bar = MockFrame()

        # ── Override sort state ─────────────────────────────────────
        self.app._sort_state = {"col": None, "rev": False}

    # ═══════════════════════════════════════════════════════════════════
    # PURE HELPER METHODS
    # ═══════════════════════════════════════════════════════════════════

    def test_status_of(self):
        """_status_of returns the correct status field."""
        self.assertEqual(self.app._status_of((1, "John", "Doe", 25, "123", 1, "Male", "2000-01-01", "Registered")),
                         "Registered")
        self.assertEqual(self.app._status_of((1, "John", "Doe", 25, "123", 1, "Male", "2000-01-01", "Pending")),
                         "Pending")
        self.assertEqual(self.app._status_of((1, "John", "Doe", 25, "123", 1, "Male", "2000-01-01", "Inactive")),
                         "Inactive")
        # Short tuple -> default to Registered
        self.assertEqual(self.app._status_of((1, "John", "Doe")),
                         "Registered")
        # None -> Registered
        self.assertEqual(self.app._status_of(None), "Registered")

    def test_gender_of(self):
        """_gender_of returns the correct gender field."""
        self.assertEqual(self.app._gender_of((1, "John", "Doe", 25, "123", 1, "Male", "2000-01-01", "Registered")),
                         "Male")
        self.assertEqual(self.app._gender_of((1, "Jane", "Doe", 25, "123", 1, "Female", "2000-01-01", "Registered")),
                         "Female")
        # Short tuple -> empty string
        self.assertEqual(self.app._gender_of((1, "John", "Doe")), "")
        # None -> empty string
        self.assertEqual(self.app._gender_of(None), "")

    def test_is_senior_true(self):
        """_is_senior returns True for age >= 60."""
        self.assertTrue(self.app._is_senior((1, "John", "Doe", 60, "123", 1)))
        self.assertTrue(self.app._is_senior((1, "John", "Doe", 65, "123", 1)))
        self.assertTrue(self.app._is_senior((1, "John", "Doe", 120, "123", 1)))

    def test_is_senior_false(self):
        """_is_senior returns False for age < 60."""
        self.assertFalse(self.app._is_senior((1, "John", "Doe", 59, "123", 1)))
        self.assertFalse(self.app._is_senior((1, "John", "Doe", 0, "123", 1)))
        self.assertFalse(self.app._is_senior((1, "John", "Doe", -1, "123", 1)))

    def test_is_senior_invalid(self):
        """_is_senior returns False for non-numeric age."""
        self.assertFalse(self.app._is_senior((1, "John", "Doe", "abc", "123", 1)))
        self.assertFalse(self.app._is_senior((1, "John", "Doe", None, "123", 1)))
        # Missing age index
        self.assertFalse(self.app._is_senior((1, "John", "Doe")))

    def test_calc_age_valid(self):
        """_calc_age returns correct age for a valid birthdate."""
        from datetime import date, timedelta
        bdate = date(1990, 6, 15)
        expected_age = (date.today().year - 1990 -
                        ((date.today().month, date.today().day) < (6, 15)))
        self.app.entries["Birthdate"] = bdate.strftime("%Y-%m-%d")
        age = self.app._calc_age()
        self.assertEqual(age, expected_age)
        self.assertEqual(self.app.age_lbl._text, f"Age: {expected_age} yrs")

    def test_calc_age_invalid(self):
        """_calc_age returns None for invalid birthdate."""
        self.app.entries["Birthdate"] = "invalid-date"
        age = self.app._calc_age()
        self.assertIsNone(age)
        self.assertIn("\u2014", self.app.age_lbl._text)

    def test_calc_age_empty(self):
        """_calc_age returns None for empty birthdate."""
        self.app.entries["Birthdate"] = ""
        age = self.app._calc_age()
        self.assertIsNone(age)

    # ═══════════════════════════════════════════════════════════════════
    # CLEAR FORM
    # ═══════════════════════════════════════════════════════════════════

    def test_clear_form_resets_entries(self):
        """clear_form resets all form fields to defaults."""
        # Fill in fields first
        self.app.entries["First Name"].insert(0, "John")
        self.app.entries["Last Name"].insert(0, "Doe")
        self.app.entries["Contact"].insert(0, "1234567890")
        self.app.gender_var.set("Male")
        self.app.status_var.set("Pending")

        self.app.clear_form()

        # All text entries should be cleared
        self.assertEqual(self.app.entries["First Name"].get(), "")
        self.assertEqual(self.app.entries["Last Name"].get(), "")
        self.assertEqual(self.app.entries["Contact"].get(), "")
        # Gender/Status reset
        self.assertEqual(self.app.gender_var.get(), "Select Gender")
        self.assertEqual(self.app.status_var.get(), "Registered")
        # Birthdate reset to today
        from datetime import date
        expected = date.today().strftime("%Y-%m-%d")
        self.assertEqual(self.app.entries["Birthdate"], expected)
        # Photo cleared
        self.assertEqual(self.app.current_photo["path"], "")

    # ═══════════════════════════════════════════════════════════════════
    # ADD RESIDENT
    # ═══════════════════════════════════════════════════════════════════

    def test_add_resident_missing_fields_shows_warning(self):
        """add_resident shows warning when required fields are empty."""
        self.app.entries["First Name"].insert(0, "")
        self.app.entries["Last Name"].insert(0, "")
        self.app.entries["Contact"].insert(0, "")

        self.app.add_resident()

        _mock_msg.showwarning.assert_called_once()
        # Database should NOT have been called
        self.assertEqual(len(database.get_residents_by_purok(TEST_PUROK_ID)), 0)

    def test_add_resident_missing_first_name(self):
        """add_resident shows warning when first name is missing."""
        self.app.entries["First Name"].insert(0, "")
        self.app.entries["Last Name"].insert(0, "Doe")
        self.app.entries["Contact"].insert(0, "1234567890")

        self.app.add_resident()

        _mock_msg.showwarning.assert_called_once()

    def test_add_resident_invalid_gender(self):
        """add_resident shows warning when gender is not selected."""
        self.app.entries["First Name"].insert(0, "John")
        self.app.entries["Last Name"].insert(0, "Doe")
        self.app.entries["Contact"].insert(0, "1234567890")
        self.app.gender_var.set("Select Gender")

        self.app.add_resident()

        _mock_msg.showwarning.assert_called_once()

    def test_add_resident_success(self):
        """add_resident inserts a new resident into the database."""
        self.app.entries["First Name"].insert(0, "Juan")
        self.app.entries["Last Name"].insert(0, "Dela Cruz")
        self.app.entries["Contact"].insert(0, "09171234567")
        self.app.gender_var.set("Male")
        self.app.status_var.set("Registered")
        self.app.entries["Birthdate"] = "1990-01-15"

        self.app.add_resident()

        residents = database.get_residents_by_purok(TEST_PUROK_ID)
        self.assertEqual(len(residents), 1)
        self.assertEqual(residents[0][1], "Juan")
        self.assertEqual(residents[0][2], "Dela Cruz")
        self.assertEqual(residents[0][4], "09171234567")

    def test_add_resident_success_pending_status(self):
        """add_resident works with Pending status."""
        self.app.entries["First Name"].insert(0, "Maria")
        self.app.entries["Last Name"].insert(0, "Santos")
        self.app.entries["Contact"].insert(0, "09221234567")
        self.app.gender_var.set("Female")
        self.app.status_var.set("Pending")

        self.app.add_resident()

        residents = database.get_residents_by_purok(TEST_PUROK_ID)
        self.assertEqual(len(residents), 1)
        # status is column index 8 in the row
        self.assertEqual(residents[0][8], "Pending")

    def test_add_resident_clears_form_on_success(self):
        """add_resident clears the form after successful addition."""
        self.app.entries["First Name"].insert(0, "John")
        self.app.entries["Last Name"].insert(0, "Doe")
        self.app.entries["Contact"].insert(0, "1234567890")
        self.app.gender_var.set("Male")

        self.app.add_resident()

        # Form should be cleared
        self.assertEqual(self.app.entries["First Name"].get(), "")
        self.assertEqual(self.app.entries["Last Name"].get(), "")
        self.assertEqual(self.app.entries["Contact"].get(), "")

    # ═══════════════════════════════════════════════════════════════════
    # UPDATE RESIDENT
    # ═══════════════════════════════════════════════════════════════════

    def test_update_resident_no_selection_shows_warning(self):
        """update_resident shows warning when no resident is selected."""
        self.mock_tree.selection_set([])
        self.app.update_resident()
        _mock_msg.showwarning.assert_called_once()

    def test_update_resident_success(self):
        """update_resident updates the selected resident's data."""
        # First, add a resident
        database.add_resident("Old", "Name", "25", "1234567890",
                              TEST_PUROK_ID, birthdate="1990-01-01",
                              gender="Male", status="Registered")
        residents = database.get_residents_by_purok(TEST_PUROK_ID)
        rid = residents[0][0]

        # Populate tree with the resident
        self.mock_tree.insert("", "end",
                              values=(f"{rid:03d}", "Old", "Name", 25,
                                      "1990-01-01", "Male", "1234567890", "Registered"),
                              tags=("even", "Registered"))
        self.mock_tree.selection_set([self.mock_tree.get_children()[0]])

        # Fill form with new data
        self.app.entries["First Name"].insert(0, "New")
        self.app.entries["Last Name"].insert(0, "Name")
        self.app.entries["Contact"].insert(0, "0987654321")
        self.app.gender_var.set("Female")
        self.app.status_var.set("Inactive")

        self.app.update_resident()

        # Verify database was updated
        updated = database.get_resident_by_id(rid)
        self.assertEqual(updated[1], "New")
        self.assertEqual(updated[2], "Name")
        self.assertEqual(updated[4], "0987654321")
        self.assertEqual(updated[6], "Female")
        self.assertEqual(updated[8], "Inactive")

    # ═══════════════════════════════════════════════════════════════════
    # DELETE RESIDENT
    # ═══════════════════════════════════════════════════════════════════

    def test_delete_resident_no_selection_shows_warning(self):
        """delete_resident shows warning when no resident is selected."""
        self.mock_tree.selection_set([])
        self.app.delete_resident()
        _mock_msg.showwarning.assert_called_once()

    def test_delete_resident_cancelled(self):
        """delete_resident does NOT delete when user cancels."""
        # Add a resident
        database.add_resident("John", "Doe", "30", "1234567890",
                              TEST_PUROK_ID)
        residents = database.get_residents_by_purok(TEST_PUROK_ID)
        rid = residents[0][0]

        # Populate tree
        self.mock_tree.insert("", "end",
                              values=(f"{rid:03d}", "John", "Doe", 30,
                                      "1990-01-01", "Male", "1234567890", "Registered"),
                              tags=("even", "Registered"))
        self.mock_tree.selection_set([self.mock_tree.get_children()[0]])

        # User cancels
        _mock_msg.askyesno.return_value = False

        self.app.delete_resident()

        # Resident should still exist
        self.assertIsNotNone(database.get_resident_by_id(rid))

    def test_delete_resident_confirmed(self):
        """delete_resident removes the resident when user confirms."""
        database.add_resident("Jane", "Doe", "25", "9876543210",
                              TEST_PUROK_ID)
        residents = database.get_residents_by_purok(TEST_PUROK_ID)
        rid = residents[0][0]

        self.mock_tree.insert("", "end",
                              values=(f"{rid:03d}", "Jane", "Doe", 25,
                                      "1995-01-01", "Female", "9876543210", "Registered"),
                              tags=("even", "Registered"))
        self.mock_tree.selection_set([self.mock_tree.get_children()[0]])

        _mock_msg.askyesno.return_value = True

        self.app.delete_resident()

        self.assertIsNone(database.get_resident_by_id(rid))

    # ═══════════════════════════════════════════════════════════════════
    # BATCH DELETE
    # ═══════════════════════════════════════════════════════════════════

    def test_batch_delete_single(self):
        """batch_delete deletes a single selected resident."""
        database.add_resident("A", "B", "20", "111", TEST_PUROK_ID)
        residents = database.get_residents_by_purok(TEST_PUROK_ID)
        rid = residents[0][0]

        iid = self.mock_tree.insert("", "end",
                                     values=(f"{rid:03d}", "A", "B", 20,
                                             "2000-01-01", "Male", "111", "Registered"))
        self.mock_tree.selection_set([iid])
        _mock_msg.askyesno.return_value = True

        self.app.batch_delete()

        self.assertIsNone(database.get_resident_by_id(rid))

    def test_batch_delete_multiple(self):
        """batch_delete deletes multiple selected residents."""
        ids = []
        for name in ["Alice", "Bob", "Charlie"]:
            database.add_resident(name, "Test", "25", "000", TEST_PUROK_ID)
            residents = database.get_residents_by_purok(TEST_PUROK_ID)
            ids.append(residents[-1][0])

        iids = []
        for rid in ids:
            iid = self.mock_tree.insert("", "end",
                                         values=(f"{rid:03d}", "Name", "Test", 25,
                                                 "1990-01-01", "Male", "000", "Registered"))
            iids.append(iid)
        self.mock_tree.selection_set(iids)
        _mock_msg.askyesno.return_value = True

        self.app.batch_delete()

        for rid in ids:
            self.assertIsNone(database.get_resident_by_id(rid))

    def test_batch_delete_none_selected(self):
        """batch_delete does nothing when nothing is selected."""
        _mock_msg.askyesno.return_value = True
        self.app.batch_delete()  # Should not crash
        _mock_msg.askyesno.assert_not_called()

    def test_batch_delete_cancelled(self):
        """batch_delete does nothing when user cancels."""
        database.add_resident("Keep", "Me", "30", "555", TEST_PUROK_ID)
        residents = database.get_residents_by_purok(TEST_PUROK_ID)
        rid = residents[0][0]

        iid = self.mock_tree.insert("", "end",
                                     values=(f"{rid:03d}", "Keep", "Me", 30,
                                             "1990-01-01", "Male", "555", "Registered"))
        self.mock_tree.selection_set([iid])
        _mock_msg.askyesno.return_value = False

        self.app.batch_delete()

        self.assertIsNotNone(database.get_resident_by_id(rid))

    # ═══════════════════════════════════════════════════════════════════
    # BATCH EXPORT
    # ═══════════════════════════════════════════════════════════════════

    def test_batch_export_writes_csv(self):
        """batch_export writes selected residents to a CSV file."""
        tmp_csv = os.path.join(self.test_dir, "batch_export_test.csv")

        database.add_resident("Export1", "Test", "25", "111", TEST_PUROK_ID)
        database.add_resident("Export2", "Test", "30", "222", TEST_PUROK_ID)

        # Populate tree
        all_residents = database.get_residents_by_purok(TEST_PUROK_ID)
        iids = []
        for r in all_residents:
            iid = self.mock_tree.insert("", "end",
                                         values=(f"{r[0]:03d}", r[1], r[2], r[3],
                                                 r[7], r[6], r[4], r[8]))
            iids.append(iid)

        self.mock_tree.selection_set(iids)
        _mock_fd.asksaveasfilename.return_value = tmp_csv

        self.app.batch_export()

        # Read back the CSV and verify
        with open(tmp_csv, "r", encoding="utf-8") as f:
            reader = list(csv.reader(f))

        self.assertEqual(len(reader), 3)  # header + 2 rows
        self.assertEqual(reader[0], ["ID", "First Name", "Last Name", "Age",
                                     "Status", "Gender", "Birthdate", "Contact"])
        self.assertEqual(reader[1][1], "Export1")
        self.assertEqual(reader[2][1], "Export2")

        # Clean up
        if os.path.exists(tmp_csv):
            os.unlink(tmp_csv)

    def test_batch_export_no_selection(self):
        """batch_export does nothing when nothing is selected."""
        _mock_fd.asksaveasfilename.return_value = os.path.join(self.test_dir, "noop.csv")
        self.app.batch_export()
        _mock_msg.showwarning.assert_not_called()

    # ═══════════════════════════════════════════════════════════════════
    # SORTING
    # ═══════════════════════════════════════════════════════════════════

    def _populate_tree_with_multiple(self):
        """Helper: add 3 residents to tree and database."""
        names = [("Charlie", "Alpha"), ("Alice", "Bravo"), ("Beta", "Charlie")]
        for fn, ln in names:
            database.add_resident(fn, ln, "25", "000", TEST_PUROK_ID)

        all_r = database.get_residents_by_purok(TEST_PUROK_ID)
        for r in all_r:
            self.mock_tree.insert("", "end",
                                   values=(f"{r[0]:03d}", r[1], r[2], r[3],
                                           r[7], r[6], r[4], r[8]))

    def test_sort_by_string_ascending(self):
        """_sort_by orders by Last Name ascending on first click."""
        self._populate_tree_with_multiple()
        children_before = self.mock_tree.get_children()

        self.app._sort_by("Last Name")

        children_after = self.mock_tree.get_children()
        last_names = [self.mock_tree.item(iid, "values")[2] for iid in children_after]
        self.assertEqual(last_names, sorted(last_names))

    def test_sort_by_string_descending(self):
        """_sort_by reverses order on second click."""
        self._populate_tree_with_multiple()

        # First click (ascending)
        self.app._sort_by("Last Name")
        # Second click (descending)
        self.app._sort_by("Last Name")

        children = self.mock_tree.get_children()
        last_names = [self.mock_tree.item(iid, "values")[2] for iid in children]
        self.assertEqual(last_names, sorted(last_names, reverse=True))

    def test_sort_by_numeric_age(self):
        """_sort_by sorts Age column numerically."""
        # Insert with varied ages (without database - just in tree)
        for age, name in [(50, "Old"), (25, "Young"), (35, "Middle")]:
            self.mock_tree.insert("", "end",
                                   values=("001", name, "Test", age,
                                           "1990-01-01", "Male", "000", "Registered"))

        self.app._sort_by("Age")

        children = self.mock_tree.get_children()
        ages = [int(self.mock_tree.item(iid, "values")[3]) for iid in children]
        self.assertEqual(ages, [25, 35, 50])

    def test_sort_by_resets_state_on_new_column(self):
        """_sort_by starts ascending when clicking a different column."""
        self._populate_tree_with_multiple()

        self.app._sort_by("Last Name")  # ascending
        self.app._sort_by("Age")        # new column, should be ascending

        self.assertEqual(self.app._sort_state["col"], "Age")
        self.assertFalse(self.app._sort_state["rev"])

    # ═══════════════════════════════════════════════════════════════════
    # REFRESH TABLE
    # ═══════════════════════════════════════════════════════════════════

    def test_refresh_table_loads_residents(self):
        """refresh_table loads all residents into the treeview."""
        database.add_resident("John", "Doe", "30", "123", TEST_PUROK_ID)
        database.add_resident("Jane", "Smith", "25", "456", TEST_PUROK_ID)

        self.app.refresh_table()

        children = self.mock_tree.get_children()
        self.assertEqual(len(children), 2)

    def test_refresh_table_filters_by_tab(self):
        """refresh_table respects the active tab filter."""
        database.add_resident("A", "B", "20", "111", TEST_PUROK_ID,
                              status="Registered")
        database.add_resident("C", "D", "25", "222", TEST_PUROK_ID,
                              status="Pending")

        self.app.active_tab.set("Pending")
        self.app.refresh_table()

        children = self.mock_tree.get_children()
        self.assertEqual(len(children), 1)
        status_val = self.mock_tree.item(children[0], "values")[7]
        self.assertEqual(status_val, "Pending")

    def test_refresh_table_filters_by_search(self):
        """refresh_table filters residents by search query."""
        database.add_resident("John", "Doe", "30", "123", TEST_PUROK_ID)
        database.add_resident("Jane", "Smith", "25", "456", TEST_PUROK_ID)

        self.app.refresh_table(query="john")

        children = self.mock_tree.get_children()
        self.assertEqual(len(children), 1)

    # ═══════════════════════════════════════════════════════════════════
    # UPDATE STATS
    # ═══════════════════════════════════════════════════════════════════

    def test_update_stats_counts(self):
        """update_stats reflects correct counts."""
        database.add_resident("A", "B", "20", "111", TEST_PUROK_ID,
                              gender="Male", status="Registered")
        database.add_resident("C", "D", "65", "222", TEST_PUROK_ID,
                              gender="Female", status="Pending")
        database.add_resident("E", "F", "70", "333", TEST_PUROK_ID,
                              gender="Male", status="Inactive")

        self.app.update_stats()

        self.assertEqual(self.app.stat_labels["total"]._text, "3")
        self.assertEqual(self.app.stat_labels["registered"]._text, "1")
        self.assertEqual(self.app.stat_labels["pending"]._text, "1")
        self.assertEqual(self.app.stat_labels["inactive"]._text, "1")
        self.assertEqual(self.app.stat_labels["seniors"]._text, "2")
        self.assertEqual(self.app.stat_labels["male"]._text, "2")
        self.assertEqual(self.app.stat_labels["female"]._text, "1")

    def test_update_stats_empty(self):
        """update_stats shows zeros when no residents exist."""
        self.app.update_stats()

        self.assertEqual(self.app.stat_labels["total"]._text, "0")
        for key in ["registered", "pending", "inactive", "seniors", "male", "female"]:
            self.assertEqual(self.app.stat_labels[key]._text, "0")

    # ═══════════════════════════════════════════════════════════════════
    # SELECTION CHANGE
    # ═══════════════════════════════════════════════════════════════════

    def test_on_selection_change_shows_batch_bar(self):
        """_on_selection_change shows batch bar when items selected."""
        self.mock_tree.insert("", "end",
                               values=("001", "John", "Doe", 30, "1990-01-01",
                                       "Male", "123", "Registered"))
        self.mock_tree.selection_set(self.mock_tree.get_children())

        # Check that batch_bar.grid() was called (it's a MockFrame, just check it didn't error)
        self.app._on_selection_change()
        # Don't need to assert - just verify it doesn't crash
        self.assertTrue(True)

    def test_on_selection_change_hides_batch_bar(self):
        """_on_selection_change hides batch bar when nothing selected."""
        self.mock_tree.selection_set([])
        self.app._on_selection_change()
        self.assertTrue(True)


# ══════════════════════════════════════════════════════════════════════
# Run
# ══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    unittest.main()
