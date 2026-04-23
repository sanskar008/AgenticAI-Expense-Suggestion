"""Expense Analyzer Agent - Analyzes spending patterns and generates insights"""

import os
import json
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import logging
import sys
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from .base_agent import Agent

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.prompts import EXPENSE_ANALYSIS_PROMPT
from utils.helpers import (
    parse_json_response,
    get_current_month,
    get_previous_month,
    format_currency,
)

logger = logging.getLogger(__name__)


class ExpenseAnalyzer(Agent):
    """Analyzes expense patterns and generates insights using Gemini API"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__("ExpenseAnalyzer")
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")

        if OpenAI and self.api_key:
            self.client = OpenAI(
                api_key=self.api_key, base_url="https://api.deepseek.com"
            )
            self.model = "deepseek-chat"
        else:
            self.client = None
            self.model = None
            self.logger.warning("DeepSeek API not available, using rule-based analysis")

    def plan(
        self, task: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Plan analysis approach"""
        expenses = context.get("expenses", []) if context else []
        previous_data = context.get("previous_data", []) if context else []

        plan = {
            "task": task,
            "current_expense_count": len(expenses),
            "previous_expense_count": len(previous_data),
            "steps": [
                "Calculate basic statistics",
                "Analyze category breakdown",
                "Compare with previous period",
                "Detect trends and anomalies",
                "Generate insights using AI",
                "Create recommendations",
            ],
            "use_ai": self.model is not None,
        }
        return plan

    def act(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute analysis"""
        expenses = self.context.get("expenses", [])
        previous_data = self.context.get("previous_data", [])

        if not expenses:
            self.logger.warning("No expenses to analyze")
            return {}

        # Analyzing expenses

        # Calculate basic statistics
        analysis = self._calculate_statistics(expenses)

        # Analyze category breakdown
        analysis["category_breakdown"] = self._analyze_categories(expenses)

        # Compare with previous period
        if previous_data:
            analysis["comparison"] = self._compare_periods(expenses, previous_data)

        # Detect trends
        analysis["trends"] = self._detect_trends(expenses, previous_data)

        # Generate AI insights if available
        if plan.get("use_ai") and self.model:
            ai_insights = self._generate_ai_insights(expenses, previous_data)
            analysis.update(ai_insights)
        else:
            # Use rule-based insights
            analysis["insights"] = self._generate_rule_based_insights(analysis)
            analysis["recommendations"] = self._generate_recommendations(analysis)

        # Detect overspending
        analysis["overspending_alerts"] = self._detect_overspending(analysis)

        return analysis

    def _calculate_statistics(self, expenses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate basic expense statistics"""
        total = sum(exp.get("amount", 0) for exp in expenses)
        avg = total / len(expenses) if expenses else 0
        max_expense = (
            max(expenses, key=lambda x: x.get("amount", 0)) if expenses else None
        )
        min_expense = (
            min(expenses, key=lambda x: x.get("amount", 0)) if expenses else None
        )

        return {
            "total_spending": total,
            "average_expense": avg,
            "expense_count": len(expenses),
            "max_expense": max_expense,
            "min_expense": min_expense,
        }

    def _analyze_categories(self, expenses: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze spending by category"""
        category_totals = defaultdict(float)

        for exp in expenses:
            category = exp.get("category", "Other")
            amount = exp.get("amount", 0)
            category_totals[category] += amount

        return dict(category_totals)

    def _compare_periods(
        self, current: List[Dict[str, Any]], previous: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compare current period with previous period"""
        current_total = sum(exp.get("amount", 0) for exp in current)
        previous_total = sum(exp.get("amount", 0) for exp in previous)

        difference = current_total - previous_total
        percent_change = (
            (difference / previous_total * 100) if previous_total > 0 else 0
        )

        # Compare by category
        current_cats = self._analyze_categories(current)
        previous_cats = self._analyze_categories(previous)

        category_changes = {}
        for cat in set(list(current_cats.keys()) + list(previous_cats.keys())):
            current_amt = current_cats.get(cat, 0)
            previous_amt = previous_cats.get(cat, 0)
            if previous_amt > 0:
                change_pct = ((current_amt - previous_amt) / previous_amt) * 100
                category_changes[cat] = {
                    "current": current_amt,
                    "previous": previous_amt,
                    "change": current_amt - previous_amt,
                    "percent_change": change_pct,
                }

        return {
            "total_change": difference,
            "percent_change": percent_change,
            "category_changes": category_changes,
        }

    def _detect_trends(
        self, current: List[Dict[str, Any]], previous: List[Dict[str, Any]]
    ) -> List[str]:
        """Detect spending trends"""
        trends = []

        if not previous:
            return trends

        comparison = self._compare_periods(current, previous)

        if comparison["percent_change"] > 20:
            trends.append(
                f"Significant increase in spending: {comparison['percent_change']:.1f}%"
            )
        elif comparison["percent_change"] < -20:
            trends.append(
                f"Significant decrease in spending: {comparison['percent_change']:.1f}%"
            )

        # Check category trends
        for cat, changes in comparison.get("category_changes", {}).items():
            if changes["percent_change"] > 30:
                trends.append(
                    f"{cat} spending increased by {changes['percent_change']:.1f}%"
                )
            elif changes["percent_change"] < -30:
                trends.append(
                    f"{cat} spending decreased by {changes['percent_change']:.1f}%"
                )

        return trends

    def _generate_ai_insights(
        self, expenses: List[Dict[str, Any]], previous_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate insights using DeepSeek API"""
        try:
            # Prepare data for AI
            expense_data = json.dumps(
                expenses[:50], indent=2
            )  # Limit to 50 for prompt size
            previous_data_str = (
                json.dumps(previous_data[:50], indent=2) if previous_data else "None"
            )

            prompt = EXPENSE_ANALYSIS_PROMPT.format(
                expense_data=expense_data, previous_data=previous_data_str
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful financial advisor that analyzes spending patterns and provides insights.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )
            response_text = response.choices[0].message.content.strip()

            insights = parse_json_response(response_text)

            if insights:
                return {
                    "insights": insights.get("insights", []),
                    "recommendations": insights.get("recommendations", []),
                    "ai_generated": True,
                }
        except Exception as e:
            self.logger.error(f"Error generating AI insights: {e}")

        # Fallback to rule-based
        return self._generate_rule_based_insights(self._calculate_statistics(expenses))

    def _generate_rule_based_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate insights using rule-based approach"""
        insights = []

        total = analysis.get("total_spending", 0)
        category_breakdown = analysis.get("category_breakdown", {})

        if total > 0:
            # Find top spending category
            if category_breakdown:
                top_category = max(category_breakdown.items(), key=lambda x: x[1])
                top_pct = (top_category[1] / total) * 100
                insights.append(
                    f"Top spending category: {top_category[0]} ({top_pct:.1f}% of total)"
                )

            # Check for high spending
            if total > 5000:
                insights.append(f"Total spending this period: {format_currency(total)}")

        return insights

    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []

        category_breakdown = analysis.get("category_breakdown", {})
        comparison = analysis.get("comparison", {})

        # Check for high spending in specific categories
        total = analysis.get("total_spending", 0)
        if total > 0:
            for cat, amount in category_breakdown.items():
                pct = (amount / total) * 100
                if pct > 40 and cat != "Rent":
                    recommendations.append(
                        f"Consider reducing {cat} spending (currently {pct:.1f}% of total)"
                    )

        # Check for increases
        if comparison:
            for cat, changes in comparison.get("category_changes", {}).items():
                if changes["percent_change"] > 30:
                    recommendations.append(
                        f"Monitor {cat} spending - increased by {changes['percent_change']:.1f}%"
                    )

        if not recommendations:
            recommendations.append(
                "Your spending patterns look balanced. Keep tracking!"
            )

        return recommendations

    def _detect_overspending(self, analysis: Dict[str, Any]) -> List[str]:
        """Detect potential overspending"""
        alerts = []

        category_breakdown = analysis.get("category_breakdown", {})
        comparison = analysis.get("comparison", {})

        # Check for category overspending
        for cat, amount in category_breakdown.items():
            if amount > 2000 and cat in ["Entertainment", "Shopping"]:
                alerts.append(f"High spending in {cat}: {format_currency(amount)}")

        # Check for significant increases
        if comparison:
            for cat, changes in comparison.get("category_changes", {}).items():
                if changes["percent_change"] > 50:
                    alerts.append(
                        f"{cat} spending increased significantly: {changes['percent_change']:.1f}%"
                    )

        return alerts
