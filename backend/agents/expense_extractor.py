"""Expense Extractor Agent - Reads expense data from various formats"""

import json
import csv
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging
import sys

from .base_agent import Agent
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.helpers import validate_expense

logger = logging.getLogger(__name__)


class ExpenseExtractor(Agent):
    """Extracts expense data from JSON, CSV, text, or SMS formats"""
    
    def __init__(self):
        super().__init__("ExpenseExtractor")
        self.supported_formats = ['json', 'csv', 'txt', 'sms', 'ocr']
    
    def plan(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Plan extraction approach based on input format"""
        if context:
            self.context.update(context)
        
        # Get actual input data from context, not from task description
        input_data = self.context.get('input_data', '')
        if not input_data:
            # Fallback: check if task itself contains the data
            if task and (task.strip().startswith('[') or task.strip().startswith('{') or Path(task).exists()):
                input_data = task
            else:
                # Try to extract from task description (e.g., "Extract expenses from: [data]")
                if 'from:' in task.lower():
                    parts = task.split('from:', 1)
                    if len(parts) > 1:
                        input_data = parts[1].strip()
        
        if not input_data:
            self.logger.warning("No input data found for format detection")
            input_data = task  # Fallback to task
        
        plan = {
            'task': task,
            'format': self._detect_format(input_data),
            'steps': [
                'Detect input format',
                'Parse input data',
                'Extract expense entries',
                'Normalize expense format',
                'Validate expenses'
            ]
        }
        return plan
    
    def act(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute extraction based on plan"""
        format_type = plan['format']
        
        # Get the actual input data from context, not from task description
        input_data = self.context.get('input_data', '')
        if not input_data:
            # Fallback: try to extract from task if it contains the data
            task = plan.get('task', '')
            # Check if task contains the actual data (not just description)
            if task and (task.strip().startswith('[') or task.strip().startswith('{') or Path(task).exists()):
                input_data = task
            elif task and 'from:' in task.lower():
                # Extract from task description (e.g., "Extract expenses from: [data]")
                parts = task.split('from:', 1)
                if len(parts) > 1:
                    input_data = parts[1].strip()
            
            if not input_data:
                self.logger.error("ERROR: No input_data found in context or task")
                return []
        
        if format_type == 'json':
            return self._extract_from_json(input_data)
        elif format_type == 'csv':
            return self._extract_from_csv(input_data)
        elif format_type == 'sms':
            return self._extract_from_sms(input_data)
        elif format_type == 'txt':
            return self._extract_from_text(input_data)
        elif format_type == 'ocr':
            return self._extract_from_ocr(input_data)
        else:
            # Try to parse as direct JSON string or file path
            return self._extract_from_json(input_data)
    
    def _detect_format(self, input_data: str) -> str:
        """Detect the format of input data"""
        input_lower = input_data.lower().strip()
        
        # Check if it's a file path - try multiple path resolutions
        file_path = Path(input_data)
        if not file_path.is_absolute():
            # Try relative to current working directory
            if (Path.cwd() / input_data).exists():
                file_path = Path.cwd() / input_data
            # Try relative to script directory
            elif (Path(__file__).parent.parent / input_data).exists():
                file_path = Path(__file__).parent.parent / input_data
        
        if file_path.exists():
            ext = file_path.suffix.lower()
            if ext == '.json':
                return 'json'
            elif ext == '.csv':
                return 'csv'
            elif ext == '.txt':
                return 'txt'
            elif ext in ['.jpg', '.jpeg', '.png', '.pdf']:
                return 'ocr'
        
        # Check if it's JSON string
        if input_data.strip().startswith('{') or input_data.strip().startswith('['):
            try:
                json.loads(input_data)
                return 'json'
            except:
                pass
        
        # Check if it looks like SMS
        if any(keyword in input_lower for keyword in ['debit', 'credit', 'rs.', 'inr', 'spent', 'payment']):
            return 'sms'
        
        # Check if it's CSV-like
        if ',' in input_data and '\n' in input_data:
            return 'csv'
        
        return 'txt'
    
    def _extract_from_json(self, input_data: str) -> List[Dict[str, Any]]:
        """Extract expenses from JSON format"""
        expenses = []
        
        try:
            # Try as file path first - resolve to absolute path
            file_path = Path(input_data)
            if not file_path.is_absolute():
                # Try relative to current working directory
                file_path = Path.cwd() / input_data
                if not file_path.exists():
                    # Try relative to script directory
                    file_path = Path(__file__).parent.parent / input_data
            
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                # Try as JSON string
                data = json.loads(input_data)
            
            # Handle different JSON structures
            if isinstance(data, list):
                expenses = data
            elif isinstance(data, dict):
                if 'expenses' in data:
                    expenses = data['expenses']
                elif 'transactions' in data:
                    expenses = data['transactions']
                else:
                    expenses = [data]
            else:
                self.logger.error(f"Unexpected data type: {type(data)}")
                return []
            
            # Normalize expenses
            normalized = []
            for i, exp in enumerate(expenses):
                try:
                    normalized_exp = self._normalize_expense(exp)
                    if validate_expense(normalized_exp):
                        normalized.append(normalized_exp)
                    else:
                        self.logger.warning(f"Expense {i} failed validation")
                except Exception as e:
                    self.logger.error(f"Error normalizing expense {i}: {e}")
            return normalized
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")
            return []
        except FileNotFoundError as e:
            self.logger.error(f"File not found: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error extracting from JSON: {e}", exc_info=True)
            return []
    
    def _extract_from_csv(self, input_data: str) -> List[Dict[str, Any]]:
        """Extract expenses from CSV format"""
        expenses = []
        
        try:
            # Try as file path first
            if Path(input_data).exists():
                file_path = input_data
            else:
                # Write string to temp file
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                    f.write(input_data)
                    file_path = f.name
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    normalized_exp = self._normalize_expense(row)
                    if validate_expense(normalized_exp):
                        expenses.append(normalized_exp)
            
            if not Path(input_data).exists():
                Path(file_path).unlink()
            
            return expenses
            
        except Exception as e:
            self.logger.error(f"Error extracting from CSV: {e}")
            return []
    
    def _extract_from_sms(self, input_data: str) -> List[Dict[str, Any]]:
        """Extract expenses from bank SMS formats"""
        expenses = []
        
        # Enhanced bank SMS patterns
        patterns = [
            r'(?:Rs\.?|INR|₹)\s*([\d,]+(?:\.\d+)?)\s+(?:debited|spent|paid|withdrawn|used)\s+at\s+([^.\n]+)',
            r'Spent\s+(?:Rs\.?|INR|₹)\s*([\d,]+(?:\.\d+)?)\s+on\s+[^ ]+\s+at\s+([^.\n]+)',
            r'(?:debited|spent|paid|withdrawn)\s+by\s+(?:Rs\.?|INR|₹)\s*([\d,]+(?:\.\d+)?)',
            r'(?:Rs\.?|INR|₹)\s*([\d,]+(?:\.\d+)?)\s+(?:debited|spent|paid|withdrawn)',
        ]
        
        lines = input_data.split('\n')
        for line in lines:
            line = line.strip()
            if not line: continue
            
            amount = None
            merchant = ""
            
            for pattern in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    # Clean amount (remove commas)
                    amount_str = match.group(1).replace(',', '')
                    amount = float(amount_str)
                    if len(match.groups()) > 1:
                        merchant = match.group(2).strip()
                    break
            
            if amount:
                expense = {
                    'amount': amount,
                    'description': f"SMS: {merchant or line}",
                    'merchant': merchant,
                    'date': datetime.now().isoformat(),
                    'source': 'sms'
                }
                expenses.append(expense)
        
        return expenses

    def _extract_from_ocr(self, input_data: str) -> List[Dict[str, Any]]:
        """Stub for OCR input support (e.g. receipts)"""
        # In a real implementation, this would use Tesseract or an AI service
        print("🔍 OCR STUB: Analyzing image text...")
        return self._extract_from_text(input_data)
    
    def _extract_from_text(self, input_data: str) -> List[Dict[str, Any]]:
        """Extract expenses from plain text format"""
        expenses = []
        
        # Try to find amount patterns
        amount_pattern = r'(\d+(?:\.\d+)?)'
        lines = input_data.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for numbers that might be amounts
            matches = re.findall(amount_pattern, line)
            if matches:
                # Use the largest number as amount
                amounts = [float(m) for m in matches]
                amount = max(amounts) if amounts else None
                
                if amount and amount > 0:
                    expense = {
                        'amount': amount,
                        'description': line,
                        'date': datetime.now().isoformat(),
                        'source': 'text'
                    }
                    expenses.append(expense)
        
        return expenses
    
    def _normalize_expense(self, expense: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize expense dictionary to standard format"""
        normalized = {
            'amount': float(expense.get('amount', expense.get('value', expense.get('price', 0)))),
            'description': str(expense.get('description', expense.get('desc', expense.get('note', expense.get('memo', ''))))),
            'date': expense.get('date', expense.get('timestamp', datetime.now().isoformat())),
        }
        
        # Add optional fields
        if 'category' in expense:
            normalized['category'] = expense['category']
        if 'merchant' in expense:
            normalized['merchant'] = expense['merchant']
        if 'source' in expense:
            normalized['source'] = expense['source']
        
        return normalized

