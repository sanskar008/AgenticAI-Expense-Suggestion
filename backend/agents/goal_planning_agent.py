"""Goal Planning Agent - Helps users plan and track savings goals"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from .base_agent import Agent
from .memory_manager import MemoryManager

logger = logging.getLogger(__name__)

class GoalPlanningAgent(Agent):
    """Agent responsible for savings goals and reduction suggestions"""

    def __init__(self, memory_manager: Optional[MemoryManager] = None):
        super().__init__("GoalPlanningAgent")
        self.memory = memory_manager or MemoryManager()

    def plan(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Plan goal operation"""
        return {
            "task": task,
            "steps": [
                "Analyze current savings goals",
                "Calculate required weekly targets",
                "Identify potential category reductions",
                "Generate actionable plan"
            ]
        }

    def act(self, plan: Dict[str, Any]) -> Any:
        """Execute goal planning operation"""
        goals = self.memory.get_goals()
        if not goals:
            return {"plans": [], "message": "No active goals found"}

        plans = []
        for goal in goals:
            plan_item = self._create_goal_plan(goal)
            plans.append(plan_item)

        return {
            "goals_analyzed": len(goals),
            "plans": plans
        }

    def _create_goal_plan(self, goal: Dict[str, Any]) -> Dict[str, Any]:
        """Create a detailed savings plan for a goal"""
        target_amount = goal['target_amount']
        current_amount = goal['current_amount']
        target_date = datetime.fromisoformat(goal['target_date'])
        
        remaining_amount = target_amount - current_amount
        days_left = (target_date - datetime.now()).days
        
        if days_left <= 0:
            return {"goal": goal['name'], "error": "Target date has passed"}

        weeks_left = max(1, days_left / 7)
        weekly_target = remaining_amount / weeks_left

        # Get spending to suggest reductions
        now = datetime.now()
        spending = self.memory.get_spending_by_category(now.month, now.year)
        
        # Simple reduction logic: Suggest 10% reduction in top 3 categories
        sorted_spending = sorted(spending.items(), key=lambda x: x[1], reverse=True)
        suggestions = []
        for cat, amt in sorted_spending[:3]:
            potential_saving = amt * 0.1
            suggestions.append({
                "category": cat,
                "suggestion": f"Reduce {cat} spending by 10% to save ₹{potential_saving:,.2f}",
                "potential_saving": potential_saving
            })

        return {
            "goal_name": goal['name'],
            "target_amount": target_amount,
            "weekly_saving_target": round(weekly_target, 2),
            "days_remaining": days_left,
            "suggested_reductions": suggestions
        }
