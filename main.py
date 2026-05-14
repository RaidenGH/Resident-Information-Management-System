import login
import database

if __name__ == "__main__":
    print("Starting Resident Information Management System...")
    database.create_tables()   # <-- this ensures residents & puroks tables exist
    login.run_login()
