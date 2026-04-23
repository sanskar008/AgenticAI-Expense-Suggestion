"""DB Tool - Handles all database operations"""

import sqlite3
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class DBTool:
    def __init__(self, db_path: str = "database/expenses.db"):
        self.db_path = db_path

    def execute_query(self, query: str, params: tuple = (), fetch: bool = True) -> Any:
        conn = sqlite3.connect(self.db_path)
        if fetch:
            conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            if fetch:
                return [dict(row) for row in cursor.fetchall()]
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"DB Query Error: {e}")
            if not fetch: conn.rollback()
            return None
        finally:
            conn.close()

    def insert_expense(self, amount, description, category, date, merchant, source):
        query = "INSERT INTO expenses (amount, description, category, date, merchant, source) VALUES (?, ?, ?, ?, ?, ?)"
        return self.execute_query(query, (amount, description, category, date, merchant, source), fetch=False)

    def get_expenses(self, filter_query: str = "", params: tuple = ()):
        query = "SELECT * FROM expenses"
        if filter_query:
            query += f" WHERE {filter_query}"
        query += " ORDER BY date DESC"
        return self.execute_query(query, params)
