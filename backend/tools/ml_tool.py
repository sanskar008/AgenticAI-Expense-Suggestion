"""ML Tool - Handles predictions and model training"""

import pandas as pd
import numpy as np
import logging
from typing import Any, Dict, List, Optional
try:
    from sklearn.linear_model import LinearRegression
except ImportError:
    LinearRegression = None

logger = logging.getLogger(__name__)

class MLTool:
    def __init__(self):
        self.model = LinearRegression() if LinearRegression else None

    def train_and_predict(self, historical_data: List[Dict[str, Any]], target_days: int) -> float:
        if not self.model or len(historical_data) < 5:
            return self._rule_based_fallback(historical_data, target_days)

        try:
            df = pd.DataFrame(historical_data)
            df['date'] = pd.to_datetime(df['date'])
            daily_spent = df.groupby(df['date'].dt.date)['amount'].sum().reset_index()
            
            X = np.array(range(len(daily_spent))).reshape(-1, 1)
            y = daily_spent['amount'].values
            
            self.model.fit(X, y)
            prediction = self.model.predict([[len(daily_spent) + target_days]])[0]
            return max(float(prediction), float(df['amount'].mean()))
        except Exception as e:
            logger.error(f"ML Tool Error: {e}")
            return self._rule_based_fallback(historical_data, target_days)

    def _rule_based_fallback(self, data: List[Dict[str, Any]], days: int) -> float:
        if not data: return 0.0
        amounts = [float(d['amount']) for d in data]
        avg = sum(amounts) / len(amounts)
        return avg * days
