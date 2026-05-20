"""Check all files for syntax errors and import issues."""
import ast
import os
import sys

os.chdir(os.path.dirname(__file__) or ".")

errors = []
files = [
    'login.py','purok.py','ui.py','admin_panel.py','register.py',
    'resident_info.py','camera_capture.py','logo.py','database.py',
    'users_database.py','theme.py','main.py'
]

print("=== SYNTAX CHECKS ===")
for fname in files:
    try:
        with open(fname, encoding='utf-8') as f:
            ast.parse(f.read())
        print(f"  OK: {fname}")
    except SyntaxError as e:
        msg = f"  SYNTAX ERROR in {fname}: line {e.lineno}: {e.msg}"
        print(msg)
        errors.append(msg)
    except FileNotFoundError:
        print(f"  SKIP: {fname} not found")

print("\n=== IMPORT TESTS ===")
try:
    import database
    database.create_tables()
    print("  OK: database")
except Exception as e:
    msg = f"  ERROR importing database: {e}"
    print(msg)
    errors.append(msg)

try:
    import users_database
    users_database.create_users_table()
    print("  OK: users_database")
except Exception as e:
    msg = f"  ERROR importing users_database: {e}"
    print(msg)
    errors.append(msg)

try:
    import theme as t
    print(f"  OK: theme (current: {t.get_current_theme()})")
    # Test font function
    r = t.font("Courier", 9, "bold")
    print(f"      font test: {r}")
    t.set_font_scale("large")
    print(f"      large font: {t.font('Courier', 9, 'bold')}")
    t.set_font_scale("medium")
except Exception as e:
    msg = f"  ERROR importing theme: {e}"
    print(msg)
    errors.append(msg)

# Test importing each module
import importlib.util
for name in ['logo', 'login', 'purok', 'resident_info']:
    try:
        spec = importlib.util.spec_from_file_location(name, f"{name}.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        print(f"  OK: {name}.py")
    except Exception as e:
        msg = f"  ERROR importing {name}.py: {e}"
        print(msg)
        errors.append(msg)

# Test ui.py specifically (it had the font bug fix)
try:
    import ui
    print("  OK: ui.py")
except Exception as e:
    msg = f"  ERROR importing ui.py: {e}"
    print(msg)
    errors.append(msg)

# Test camera_capture.py
try:
    spec = importlib.util.spec_from_file_location('camera_capture', 'camera_capture.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print("  OK: camera_capture.py")
except Exception as e:
    msg = f"  ERROR importing camera_capture.py: {e}"
    print(msg)
    errors.append(msg)

if errors:
    print(f"\n❌ {len(errors)} ERROR(S) FOUND:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("\n✅ ALL CHECKS PASSED!")
