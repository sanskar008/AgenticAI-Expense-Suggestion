"""Prediction Agent - Predicts future spending trends using ML"""

import logging
import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
try:
    from sklearn.linear_model import LinearRegression
except ImportError:
    LinearRegression = None

from .base_agent import Agent
from .memory_manager import MemoryManager
from tools.ml_tool import MLTool

logger = logging.getLogger(__name__)

class PredictionAgent(Agent):
    """Agent responsible for predicting future spending"""

    def __init__(self, memory_manager: Optional[MemoryManager] = None):
        super().__init__("PredictionAgent")
        self.memory = memory_manager or MemoryManager()
        self.ml_tool = MLTool()

    def plan(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Plan prediction operation"""
        return {
            "task": task,
            "steps": [
                "Retrieve historical expense data",
                "Preprocess data for ML modeling",
                "Train prediction models",
                "Generate forecasts",
                "Return structured predictions"
            ]
        }

    def act(self, plan: Dict[str, Any]) -> Any:
        """Execute prediction operation"""
        expenses = self.memory.get_all_expenses()
        if not expenses:
            return {"predicted_total": 0, "category_forecast": {}, "error": "No data available"}

        df = pd.DataFrame(expenses)
        df['date'] = pd.to_datetime(df['date'])
        df['amount'] = pd.to_numeric(df['amount'])

        # Get current month info
        now = datetime.now()
        current_month = now.month
        current_year = now.year
        
        # Calculate days in current month
        if current_month == 12:
            next_month = datetime(current_year + 1, 1, 1)
        else:
            next_month = datetime(current_year, current_month + 1, 1)
        days_in_month = (next_month - datetime(current_year, current_month, 1)).days
        current_day = now.day

        # Total Prediction
        predicted_total = self._predict_total_spending(df, current_day, days_in_month)
        
        # Category Prediction
        category_forecast = self._predict_category_spending(df, current_day, days_in_month)

        return {
            "predicted_total": round(predicted_total, 2),
            "category_forecast": {cat: round(amt, 2) for cat, amt in category_forecast.items()},
            "confidence": "medium" if len(expenses) > 20 else "low"
        }

    def _predict_total_spending(self, df: pd.DataFrame, current_day: int, days_in_month: int) -> float:
        """Predict total spending using MLTool"""
        now = datetime.now()
        current_month_df = df[(df['date'].dt.month == now.month) & (df['date'].dt.year == now.year)]
        spent_so_far = current_month_df['amount'].sum()
        
        remaining_days = max(0, days_in_month - current_day)
        
        # Use ML tool for prediction
        predicted_remaining = self.ml_tool.train_and_predict(df.to_dict('records'), remaining_days)
        
        return spent_so_far + predicted_remaining

    def _predict_category_spending(self, df: pd.DataFrame, current_day: int, days_in_month: int) -> Dict[str, float]:
        """Predict spending per category using MLTool"""
        now = datetime.now()
        categories = df['category'].unique()
        forecasts = {}
        remaining_days = max(0, days_in_month - current_day)

        for cat in categories:
            cat_df = df[df['category'] == cat]
            current_cat_df = cat_df[(cat_df['date'].dt.month == now.month) & (cat_df['date'].dt.year == now.year)]
            spent_so_far = current_cat_df['amount'].sum()
            
            # Use ML tool for each category
            predicted_remaining = self.ml_tool.train_and_predict(cat_df.to_dict('records'), remaining_days)
            forecasts[cat] = spent_so_far + predicted_remaining

        return forecasts
