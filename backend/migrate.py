import sqlite3
import os

def migrate():
    db_path = "database/expenses.db"
    if not os.path.exists(db_path):
        print("Database not found, no migration needed.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    tables = ["expenses", "insights", "analysis_cache", "budgets", "goals", "notifications", "metrics"]
    
    for table in tables:
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN user_id INTEGER")
            print(f"Added user_id to {table}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"user_id already exists in {table}")
            else:
                print(f"Error migrating {table}: {e}")
    
    # Create users table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone_number TEXT UNIQUE NOT NULL,
        name TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
