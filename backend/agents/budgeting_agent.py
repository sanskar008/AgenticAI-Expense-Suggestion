"""Budgeting Agent - Tracks spending against monthly budgets"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from .base_agent import Agent
from .memory_manager import MemoryManager

logger = logging.getLogger(__name__)

class BudgetingAgent(Agent):
    """Agent responsible for budget management and tracking"""

    def __init__(self, memory_manager: Optional[MemoryManager] = None):
        super().__init__("BudgetingAgent")
        self.memory = memory_manager or MemoryManager()

    def plan(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Plan budgeting operation"""
        task_lower = task.lower()
        
        if "set" in task_lower and "budget" in task_lower:
            operation = "set_budget"
        elif "track" in task_lower or "check" in task_lower or "budget" in task_lower:
            operation = "track_budget"
        else:
            operation = "track_budget"

        return {
            "task": task,
            "operation": operation,
            "steps": [
                f"Identify operation: {operation}",
                "Execute budgeting logic",
                "Return alerts if any"
            ]
        }

    def act(self, plan: Dict[str, Any]) -> Any:
        """Execute budgeting operation"""
        operation = plan.get("operation")
        
        if operation == "set_budget":
            return self._set_budget_from_context()
        else:
            return self._track_spending()

    def _set_budget_from_context(self) -> Dict[str, Any]:
        """Set budget based on context data"""
        category = self.context.get("category")
        amount = self.context.get("amount")
        month = self.context.get("month", datetime.now().month)
        year = self.context.get("year", datetime.now().year)

        if not category or amount is None:
            return {"success": False, "error": "Category and amount required"}

        success = self.memory.set_budget(category, amount, month, year)
        return {"success": success, "category": category, "amount": amount}

    def _track_spending(self) -> Dict[str, Any]:
        """Track current spending against budgets and generate alerts"""
        now = datetime.now()
        month = self.context.get("month", now.month)
        year = self.context.get("year", now.year)

        budgets = self.memory.get_budgets(month, year)
        spending = self.memory.get_spending_by_category(month, year)

        alerts = []
        status = []

        for b in budgets:
            category = b['category']
            budget_amount = b['amount']
            spent_amount = spending.get(category, 0)
            
            percentage = (spent_amount / budget_amount) * 100 if budget_amount > 0 else 0
            
            status_item = {
                "category": category,
                "budget": budget_amount,
                "spent": spent_amount,
                "percentage": percentage
            }
            status.append(status_item)

            if percentage >= 100:
                alerts.append({
                    "level": "CRITICAL",
                    "category": category,
                    "message": f"Budget exceeded for {category}! Spent {spent_amount} of {budget_amount} ({percentage:.1f}%)"
                })
            elif percentage >= 80:
                alerts.append({
                    "level": "WARNING",
                    "category": category,
                    "message": f"Budget warning for {category}. Spent {spent_amount} of {budget_amount} ({percentage:.1f}%)"
                })

        return {
            "month": month,
            "year": year,
            "status": status,
            "alerts": alerts
        }
