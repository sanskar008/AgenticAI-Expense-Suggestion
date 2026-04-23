import sqlite3
import json
from datetime import datetime, timedelta
import random
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.memory_manager import MemoryManager

def seed_database():
    print("Seeding database...")
    
    # Initialize MemoryManager to ensure tables exist
    memory = MemoryManager()
    
    # Clear old data using raw SQL via a temporary connection
    conn = sqlite3.connect(memory.db_path)
    cursor = conn.cursor()
    print("Clearing old data...")
    tables = ['expenses', 'budgets', 'goals', 'insights', 'notifications', 'metrics', 'analysis_cache']
    for table in tables:
        try:
            cursor.execute(f"DELETE FROM {table}")
        except:
            pass
    conn.commit()
    conn.close()
    
    now = datetime.now()
    current_month = now.month
    current_year = now.year
    
    # 1. Seed Budgets
    print("Seeding budgets...")
    budgets = [
        ("Food", 15000.0),
        ("Travel", 5000.0),
        ("Entertainment", 3000.0),
        ("Shopping", 8000.0),
        ("Utilities", 4000.0)
    ]
    for cat, amt in budgets:
        memory.set_budget(cat, amt, current_month, current_year)
    
    # 2. Seed Expenses
    print("Seeding expenses...")
    categories = ["Food", "Travel", "Entertainment", "Shopping", "Utilities", "Other"]
    merchants = {
        "Food": ["Zomato", "Swiggy", "Starbucks", "Blinkit", "Local Grocery"],
        "Travel": ["Uber", "Ola", "Metro", "Petrol Pump"],
        "Entertainment": ["Netflix", "PVR", "Spotify", "Gaming"],
        "Shopping": ["Amazon", "Myntra", "Zara", "Nike"],
        "Utilities": ["Electricity Bill", "Water Bill", "Internet", "Mobile Recharge"]
    }
    
    # Seed for last 45 days
    expenses_to_insert = []
    for i in range(45):
        date = now - timedelta(days=i)
        for _ in range(random.randint(1, 3)):
            cat = random.choice(categories)
            merchant_list = merchants.get(cat, ["General Store", "Cash Withdrawal"])
            merchant = random.choice(merchant_list)
            amount = random.uniform(50, 2000)
            expenses_to_insert.append({
                "amount": round(amount, 2),
                "description": f"Purchase at {merchant}",
                "category": cat,
                "date": date.isoformat(),
                "merchant": merchant,
                "source": "manual"
            })
    
    # Use MemoryManager to store expenses (it handles connections)
    memory.context = {"expenses": expenses_to_insert}
    memory._store_memory()
    
    # 3. Seed Goals
    print("Seeding goals...")
    target_date = (now + timedelta(days=90)).isoformat()
    memory.add_goal("New Laptop", 80000.0, target_date)
    
    print("Seeding complete!")

if __name__ == "__main__":
    seed_database()
