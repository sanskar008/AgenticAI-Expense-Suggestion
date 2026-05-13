"""Memory Manager Agent - Stores and retrieves long-term insights"""

import os
import sqlite3
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path
import logging
import sys
import functools
from tools.db_tool import DBTool

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from .base_agent import Agent

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.prompts import MEMORY_RETRIEVAL_PROMPT
from utils.helpers import parse_json_response

class MemoryManager(Agent):
    """Manages long-term memory for expense insights and patterns"""

    def __init__(self, db_path: str = "database/expenses.db"):
        super().__init__("MemoryManager")
        self.db_path = db_path
        self.db = DBTool(db_path)
        self._ensure_db_exists()
        self.api_key = os.getenv("DEEPSEEK_API_KEY")

        if OpenAI and self.api_key:
            self.client = OpenAI(
                api_key=self.api_key, base_url="https://api.deepseek.com"
            )
            self.model = "deepseek-chat"
        else:
            self.client = None
            self.model = None

    def _ensure_db_exists(self):
        """Ensure database directory and tables exist using schema.sql"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        schema_path = Path(__file__).parent.parent / "database" / "schema.sql"
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if schema_path.exists():
                with open(schema_path, 'r') as f:
                    schema = f.read()
                    cursor.executescript(schema)
                self.logger.info("Database schema applied from schema.sql")
            else:
                self.logger.warning("schema.sql not found, using internal fallback")
                # Fallback to internal queries if schema.sql is missing
                self._apply_fallback_schema(cursor)
                
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Error ensuring database exists: {e}")

    def _apply_fallback_schema(self, cursor):
        """Minimal fallback schema if schema.sql is missing"""
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, phone_number TEXT UNIQUE, name TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY, user_id INTEGER, amount REAL, description TEXT, category TEXT, date TEXT)")

    def plan(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Plan memory operation"""
        if context:
            self.context.update(context)

        operation = "retrieve" if "retrieve" in task.lower() or "get" in task.lower() else "store"
        if "input_data" in self.context:
            operation = "store"

        plan = {
            "task": task,
            "operation": operation,
            "steps": [
                f"Determine operation type: {operation}",
                "Execute memory operation",
                "Return results",
            ],
        }
        return plan

    def act(self, plan: Dict[str, Any]) -> Any:
        """Execute memory operation"""
        operation = plan.get("operation", "store")

        if operation == "store":
            return self._store_memory()
        else:
            return self._retrieve_memory()

    def _store_memory(self) -> Dict[str, Any]:
        """Store expense data and generated insights"""
        input_data = self.context.get("input_data", {})
        user_id = self.context.get("user_id")
        
        if not input_data:
            return {"success": False, "error": "No input data to store"}

        try:
            # Store insights if present
            if "insights" in input_data:
                self._store_insights(user_id, input_data["insights"])
            
            # Store analysis if present
            if "analysis" in input_data:
                self._store_analysis(user_id, input_data["analysis"])

            return {"success": True, "message": "Memory stored successfully"}
        except Exception as e:
            self.logger.error(f"Error storing memory: {e}")
            return {"success": False, "error": str(e)}

    def _store_insights(self, user_id: int, insights: List[Dict]):
        now = datetime.now()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        for insight in insights:
            cursor.execute(
                """INSERT OR IGNORE INTO insights 
                   (user_id, month, year, insight_type, content, metadata) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    user_id,
                    now.month,
                    now.year,
                    insight.get("type", "general"),
                    insight.get("content", ""),
                    json.dumps(insight.get("metadata", {})),
                ),
            )
        conn.commit()
        conn.close()

    def _store_analysis(self, user_id: int, analysis: Dict):
        now = datetime.now()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT OR REPLACE INTO analysis_cache 
               (user_id, month, year, analysis_data) 
               VALUES (?, ?, ?, ?)""",
            (user_id, now.month, now.year, json.dumps(analysis)),
        )
        conn.commit()
        conn.close()

    def _retrieve_memory(self) -> Dict[str, Any]:
        """Retrieve stored expenses and insights"""
        user_id = self.context.get("user_id")
        now = datetime.now()
        month = self.context.get("month", now.month)
        year = self.context.get("year", now.year)
        
        if not user_id:
            self.logger.warning("No user_id provided for retrieving memory")

        results = {"expenses": [], "insights": [], "previous_analysis": None}

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Retrieve expenses
            cursor.execute(
                "SELECT * FROM expenses WHERE user_id = ? AND strftime('%m', date) = ? AND strftime('%Y', date) = ?",
                (user_id, f"{month:02d}", str(year)),
            )
            results["expenses"] = [dict(row) for row in cursor.fetchall()]

            # Retrieve insights
            cursor.execute(
                "SELECT * FROM insights WHERE user_id = ? AND month = ? AND year = ?",
                (user_id, month, year),
            )
            results["insights"] = [dict(row) for row in cursor.fetchall()]

            # Retrieve cached analysis
            cursor.execute(
                "SELECT analysis_data FROM analysis_cache WHERE user_id = ? AND month = ? AND year = ?",
                (user_id, month, year),
            )
            row = cursor.fetchone()
            if row:
                results["previous_analysis"] = json.loads(row["analysis_data"])

            conn.close()
            return results
        except Exception as e:
            self.logger.error(f"Error retrieving memory: {e}")
            return results

    # --- CRUD Helper Methods ---

    def get_all_expenses(self, user_id: Optional[int] = None) -> List[Dict]:
        """Get all expenses, optionally filtered by user"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if user_id:
            cursor.execute("SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC", (user_id,))
        else:
            cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_spending_by_category(self, user_id: int, month: int, year: int) -> Dict[str, float]:
        """Get spending totals by category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """SELECT category, SUM(amount) FROM expenses 
               WHERE user_id = ? AND strftime('%m', date) = ? AND strftime('%Y', date) = ?
               GROUP BY category""",
            (user_id, f"{month:02d}", str(year)),
        )
        results = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        return results

    def get_insights(self, user_id: int, month: int, year: int) -> List[Dict]:
        """Get stored insights for a specific month"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM insights WHERE user_id = ? AND month = ? AND year = ? ORDER BY created_at DESC",
                (user_id, month, year),
            )
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Error getting insights: {e}")
            return []

    def get_budgets(self, user_id: int, month: int, year: int) -> List[Dict]:
        """Get budgets for a specific month"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM budgets WHERE user_id = ? AND month = ? AND year = ?",
            (user_id, month, year),
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_goals(self, user_id: int) -> List[Dict]:
        """Get all savings goals for a user"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM goals WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def update_profile(self, user_id: int, name: str = None, email: str = None) -> bool:
        """Update user profile details"""
        updates = []
        params = []
        if name:
            updates.append("name = ?")
            params.append(name)
        if email:
            updates.append("email = ?")
            params.append(email)
        
        if not updates: return False
            
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"Error updating profile: {e}")
            return False

    def get_settings(self, user_id: int) -> Dict[str, Any]:
        """Get user settings"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_settings WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            
            if not row:
                cursor.execute("INSERT INTO user_settings (user_id) VALUES (?)", (user_id,))
                conn.commit()
                cursor.execute("SELECT * FROM user_settings WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
            
            conn.close()
            return dict(row)
        except Exception as e:
            self.logger.error(f"Error getting settings: {e}")
            return {}

    def update_settings(self, user_id: int, settings: Dict[str, Any]) -> bool:
        """Update user settings"""
        fields = []
        params = []
        for key, value in settings.items():
            if key in ["dark_mode", "currency", "budget_alerts"]:
                fields.append(f"{key} = ?")
                params.append(value)
        
        if not fields: return False
            
        params.append(user_id)
        query = f"UPDATE user_settings SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?"
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            self.logger.error(f"Error updating settings: {e}")
            return False

    def update_goal_progress(self, user_id: int, goal_id: int, amount: float) -> bool:
        """Add savings to a goal"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE goals SET current_amount = current_amount + ? WHERE id = ? AND user_id = ?", (amount, goal_id, user_id))
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"Error updating goal: {e}")
            return False

    def create_goal(self, user_id: int, name: str, target_amount: float, target_date: str, emoji: str = '💰') -> bool:
        """Create a new savings goal"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO goals (user_id, name, target_amount, target_date, emoji) VALUES (?, ?, ?, ?, ?)", (user_id, name, target_amount, target_date, emoji))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            self.logger.error(f"Error creating goal: {e}")
            return False

    def set_budget(self, user_id: int, category: str, amount: float, month: int, year: int) -> bool:
        """Set or update a budget"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO budgets (user_id, category, amount, month, year)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id, category, month, year) DO UPDATE SET amount = excluded.amount
            """, (user_id, category, amount, month, year))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            self.logger.error(f"Error setting budget: {e}")
            return False

    def reset_account(self, user_id: int) -> bool:
        """Wipe all data for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            tables = ["expenses", "insights", "analysis_cache", "budgets", "goals", "notifications", "metrics", "user_settings"]
            for table in tables:
                cursor.execute(f"DELETE FROM {table} WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            self.logger.error(f"Error resetting account: {e}")
            return False

    def get_notifications(self, user_id: int) -> List[Dict[str, Any]]:
        """Get notification history"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 50", (user_id,))
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Error getting notifications: {e}")
            return []
