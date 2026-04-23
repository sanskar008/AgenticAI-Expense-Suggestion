"""Expense Classifier Agent - Classifies expenses into categories using Gemini API"""

import os
import json
from typing import Any, Dict, List, Optional
import logging
import sys
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from .base_agent import Agent

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.prompts import EXPENSE_CLASSIFICATION_PROMPT
from utils.helpers import parse_json_response

logger = logging.getLogger(__name__)


class ExpenseClassifier(Agent):
    """Classifies expenses into categories using Gemini API"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__("ExpenseClassifier")
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment variables")

        if OpenAI is None:
            raise ImportError(
                "openai package not installed. Install with: pip install openai"
            )

        self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
        self.model = "deepseek-chat"
        self.categories = [
            "Food",
            "Rent",
            "Travel",
            "Entertainment",
            "Utilities",
            "Healthcare",
            "Shopping",
            "Transportation",
            "Education",
            "Insurance",
            "Savings",
            "Other",
        ]

    def plan(
        self, task: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Plan classification approach"""
        expenses = context.get("expenses", []) if context else []

        plan = {
            "task": task,
            "expense_count": len(expenses),
            "steps": [
                "Load expenses from context",
                "Classify each expense using Gemini API",
                "Validate classifications",
                "Return classified expenses",
            ],
            "batch_size": 10,  # Process in batches to avoid rate limits
        }
        return plan

    def act(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute classification"""
        expenses = self.context.get("expenses", [])

        if not expenses:
            self.logger.warning("No expenses to classify")
            return []

        classified_expenses = []
        batch_size = plan.get("batch_size", 10)

        for i in range(0, len(expenses), batch_size):
            batch = expenses[i : i + batch_size]

            for expense in batch:
                classified = self._classify_single_expense(expense)
                if classified:
                    classified_expenses.append(classified)

        # Classification completed
        return classified_expenses

    def _classify_single_expense(
        self, expense: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Classify a single expense using DeepSeek API"""
        try:
            # Build expense text for classification
            expense_text = f"Amount: {expense.get('amount', 0)}, Description: {expense.get('description', '')}"
            if "merchant" in expense:
                expense_text += f", Merchant: {expense['merchant']}"

            # Create prompt
            prompt = EXPENSE_CLASSIFICATION_PROMPT.format(expense_text=expense_text)

            # Call DeepSeek API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that classifies expenses into categories.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )
            response_text = response.choices[0].message.content.strip()

            # Parse response
            classification = parse_json_response(response_text)

            if classification and "category" in classification:
                expense["category"] = classification["category"]
                expense["classification_confidence"] = classification.get(
                    "confidence", 0.5
                )
                expense["classification_reasoning"] = classification.get(
                    "reasoning", ""
                )

                # Validate category
                if expense["category"] not in self.categories:
                    self.logger.warning(
                        f"Invalid category {expense['category']}, defaulting to Other"
                    )
                    expense["category"] = "Other"

                return expense
            else:
                self.logger.warning(f"Failed to classify expense: {expense_text}")
                expense["category"] = "Other"
                expense["classification_confidence"] = 0.0
                return expense

        except Exception as e:
            self.logger.error(f"Error classifying expense: {e}")
            expense["category"] = "Other"
            expense["classification_confidence"] = 0.0
            return expense

    def reflect(self, result: Any, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Reflect on classification results"""
        reflection = super().reflect(result, plan)

        if result:
            # Calculate classification statistics
            categories = {}
            total_confidence = 0
            for exp in result:
                cat = exp.get("category", "Other")
                categories[cat] = categories.get(cat, 0) + 1
                total_confidence += exp.get("classification_confidence", 0)

            avg_confidence = total_confidence / len(result) if result else 0

            reflection["insights"].extend(
                [
                    f"Classified {len(result)} expenses",
                    f"Category distribution: {categories}",
                    f"Average confidence: {avg_confidence:.2f}",
                ]
            )

        return reflection
