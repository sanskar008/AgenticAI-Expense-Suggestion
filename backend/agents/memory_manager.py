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

logger = logging.getLogger(__name__)


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
        """Ensure database directory and tables exist"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Table creation queries
        queries = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT UNIQUE NOT NULL,
                name TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL NOT NULL,
                description TEXT NOT NULL,
                category TEXT,
                date TEXT NOT NULL,
                merchant TEXT,
                source TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                month INTEGER NOT NULL,
                year INTEGER NOT NULL,
                insight_type TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, month, year, insight_type, content),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS analysis_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                month INTEGER NOT NULL,
                year INTEGER NOT NULL,
                analysis_data TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, month, year),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                month INTEGER NOT NULL,
                year INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, category, month, year),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT NOT NULL,
                target_amount REAL NOT NULL,
                target_date TEXT NOT NULL,
                current_amount REAL DEFAULT 0,
                status TEXT DEFAULT 'active',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                hash TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, hash),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                metric_name TEXT NOT NULL,
                value REAL NOT NULL,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        ]
        
        for q in queries:
            self.db.execute_query(q, fetch=False)

    def plan(
        self, task: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Plan memory operation"""
        task_lower = task.lower()

        if "store" in task_lower or "save" in task_lower:
            operation = "store"
        elif "retrieve" in task_lower or "get" in task_lower or "recall" in task_lower:
            operation = "retrieve"
        else:
            operation = "store"  # Default to store

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
        """Store expenses and insights in database"""
        expenses = self.context.get("expenses", [])
        analysis = self.context.get("analysis", {})

        stored_count = 0
        insights_stored = 0

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Store expenses
            for expense in expenses:
                cursor.execute(
                    """
                    INSERT INTO expenses (amount, description, category, date, merchant, source)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        expense.get("amount", 0),
                        expense.get("description", ""),
                        expense.get("category", "Other"),
                        expense.get("date", datetime.now().isoformat()),
                        expense.get("merchant", ""),
                        expense.get("source", ""),
                    ),
                )
                stored_count += 1
            
            # Clear cache on update
            self.get_spending_by_category.cache_clear()

            # Store insights
            if analysis:
                now = datetime.now()
                month = now.month
                year = now.year

                # Store analysis cache
                analysis_json = json.dumps(analysis)
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO analysis_cache (month, year, analysis_data)
                    VALUES (?, ?, ?)
                """,
                    (month, year, analysis_json),
                )

                # Store individual insights
                insights = analysis.get("insights", [])
                for insight in insights:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO insights (month, year, insight_type, content, metadata)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        (month, year, "insight", insight, json.dumps({})),
                    )
                    insights_stored += 1

                # Store recommendations
                recommendations = analysis.get("recommendations", [])
                for rec in recommendations:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO insights (month, year, insight_type, content, metadata)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        (month, year, "recommendation", rec, json.dumps({})),
                    )
                    insights_stored += 1

            conn.commit()

        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error storing memory: {e}")
            raise
        finally:
            conn.close()

        return {
            "expenses_stored": stored_count,
            "insights_stored": insights_stored,
            "success": True,
        }

    def _retrieve_memory(self) -> Dict[str, Any]:
        """Retrieve stored expenses and insights"""
        query = self.context.get("query", "")
        month = self.context.get("month")
        year = self.context.get("year")

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        results = {"expenses": [], "insights": [], "previous_analysis": None}

        try:
            # Retrieve expenses
            if month and year:
                cursor.execute(
                    """
                    SELECT * FROM expenses
                    WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
                    ORDER BY date DESC
                """,
                    (str(year), f"{month:02d}"),
                )
            else:
                cursor.execute("SELECT * FROM expenses ORDER BY date DESC LIMIT 100")

            for row in cursor.fetchall():
                expense = dict(row)
                results["expenses"].append(expense)

            # Retrieve insights
            if month and year:
                cursor.execute(
                    """
                    SELECT * FROM insights
                    WHERE year = ? AND month = ?
                    ORDER BY created_at DESC
                """,
                    (year, month),
                )
            else:
                cursor.execute(
                    "SELECT * FROM insights ORDER BY created_at DESC LIMIT 50"
                )

            for row in cursor.fetchall():
                insight = dict(row)
                results["insights"].append(insight)

            # Retrieve previous analysis
            if month and year:
                cursor.execute(
                    """
                    SELECT analysis_data FROM analysis_cache
                    WHERE year = ? AND month = ?
                """,
                    (year, month),
                )
                row = cursor.fetchone()
                if row:
                    results["previous_analysis"] = json.loads(row["analysis_data"])

        except Exception as e:
            self.logger.error(f"Error retrieving memory: {e}")
        finally:
            conn.close()

        # Use AI to find relevant memories if query provided
        if query and self.model and results["insights"]:
            results["relevant_memories"] = self._find_relevant_memories(
                query, results["insights"]
            )

        return results

    def _find_relevant_memories(
        self, query: str, memories: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Use AI to find relevant memories for a query"""
        try:
            memories_text = json.dumps(memories[:20], indent=2)  # Limit for prompt size

            prompt = MEMORY_RETRIEVAL_PROMPT.format(query=query, memories=memories_text)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that finds relevant memories based on queries.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )
            response_text = response.choices[0].message.content.strip()

            result = parse_json_response(response_text)

            if result and "relevant_memories" in result:
                return result["relevant_memories"]
        except Exception as e:
            self.logger.error(f"Error finding relevant memories: {e}")

        return []

    def get_previous_month_data(self) -> List[Dict[str, Any]]:
        """Get expenses from previous month"""
        from utils.helpers import get_previous_month

        year, month = get_previous_month()
        self.context = {"month": month, "year": year}

        result = self._retrieve_memory()
        return result.get("expenses", [])

    def get_previous_month_analysis(self) -> Optional[Dict[str, Any]]:
        """Get analysis from previous month"""
        from utils.helpers import get_previous_month

        year, month = get_previous_month()
        self.context = {"month": month, "year": year}

        result = self._retrieve_memory()
        return result.get("previous_analysis")

    def set_budget(self, category: str, amount: float, month: int, year: int) -> bool:
        """Set or update budget for a category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO budgets (category, amount, month, year)
                VALUES (?, ?, ?, ?)
            """,
                (category, amount, month, year),
            )
            conn.commit()
            self.get_budgets.cache_clear()
            return True
        except Exception as e:
            self.logger.error(f"Error setting budget: {e}")
            return False
        finally:
            conn.close()

    @functools.lru_cache(maxsize=32)
    def get_budgets(self, month: int, year: int) -> List[Dict[str, Any]]:
        """Get all budgets for a specific month/year (cached)"""
        # We need to bypass cache if database is updated - for now simple cache
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT category, amount FROM budgets WHERE month = ? AND year = ?",
                (month, year),
            )
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Error getting budgets: {e}")
            return []
        finally:
            conn.close()

    @functools.lru_cache(maxsize=32)
    def get_spending_by_category(self, month: int, year: int) -> Dict[str, float]:
        """Get total spending per category for a month/year (cached)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Note: strftime('%m', date) returns '01' for January, so we need to match that
            month_str = f"{month:02d}"
            year_str = str(year)
            cursor.execute(
                """
                SELECT category, SUM(amount) FROM expenses
                WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
                GROUP BY category
            """,
                (year_str, month_str),
            )
            return {row[0]: row[1] for row in cursor.fetchall()}
        except Exception as e:
            self.logger.error(f"Error getting spending by category: {e}")
            return {}
        finally:
            conn.close()

    def get_all_expenses(self) -> List[Dict[str, Any]]:
        """Get all expenses from the database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM expenses ORDER BY date ASC")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Error getting all expenses: {e}")
            return []
        finally:
            conn.close()

    def add_goal(self, name: str, target_amount: float, target_date: str) -> bool:
        """Add a new savings goal"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO goals (name, target_amount, target_date) VALUES (?, ?, ?)",
                (name, target_amount, target_date),
            )
            conn.commit()
            return True
        except Exception as e:
            self.logger.error(f"Error adding goal: {e}")
            return False
        finally:
            conn.close()

    def get_goals(self) -> List[Dict[str, Any]]:
        """Get all active goals"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM goals WHERE status = 'active'")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Error getting goals: {e}")
            return []
        finally:
            conn.close()

    def is_notification_duplicate(self, content_hash: str) -> bool:
        """Check if notification with same hash was recently sent (last 24h)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id FROM notifications WHERE hash = ? AND created_at > datetime('now', '-1 day')",
                (content_hash,),
            )
            return cursor.fetchone() is not None
        except Exception as e:
            self.logger.error(f"Error checking duplicate notification: {e}")
            return False
        finally:
            conn.close()

    def log_notification(self, title: str, message: str, content_hash: str):
        """Log a sent notification"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT OR REPLACE INTO notifications (title, message, hash) VALUES (?, ?, ?)",
                (title, message, content_hash),
            )
            conn.commit()
        except Exception as e:
            self.logger.error(f"Error logging notification: {e}")
        finally:
            conn.close()

    def log_metric(self, name: str, value: float, metadata: Optional[Dict] = None):
        """Log a system metric"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO metrics (metric_name, value, metadata) VALUES (?, ?, ?)",
                (name, value, json.dumps(metadata) if metadata else None),
            )
            conn.commit()
        except Exception as e:
            self.logger.error(f"Error logging metric: {e}")
        finally:
            conn.close()
