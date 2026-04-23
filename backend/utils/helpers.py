"""Helper utility functions"""

import json
import re
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def parse_json_response(text: str) -> Optional[Dict[str, Any]]:
    """Extract JSON from text response, handling markdown code blocks"""
    try:
        # Try direct JSON parsing first
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to extract JSON from markdown code blocks
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try to find JSON object in text
    json_match = re.search(r"\{.*\}", text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass

    logger.warning(f"Failed to parse JSON from response: {text[:200]}")
    return None


def format_currency(amount: float) -> str:
    """Format amount as currency in Indian Rupees"""
    return f"₹{amount:,.2f}"


def get_month_range(year: int, month: int) -> tuple:
    """Get start and end dates for a given month"""
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)
    return start_date, end_date


def get_current_month() -> tuple:
    """Get current year and month"""
    now = datetime.now()
    return now.year, now.month


def get_previous_month() -> tuple:
    """Get previous year and month"""
    now = datetime.now()
    if now.month == 1:
        return now.year - 1, 12
    return now.year, now.month - 1


def validate_expense(expense: Dict[str, Any]) -> bool:
    """Validate expense dictionary has required fields"""
    required_fields = ["amount", "date", "description"]

    # Check all required fields exist
    if not all(field in expense for field in required_fields):
        return False

    # Validate amount is a number and > 0
    try:
        amount = float(expense.get("amount", 0))
        if amount <= 0:
            return False
    except (ValueError, TypeError):
        return False

    # Validate description is not empty
    description = str(expense.get("description", "")).strip()
    if not description:
        return False

    return True


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    return re.sub(r"[^\w\-_\.]", "_", filename)
