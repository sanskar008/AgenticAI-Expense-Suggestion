"""Notification Agent - Sends notifications and suggestions"""

from typing import Any, Dict, List, Optional
import logging
import sys
import hashlib
from datetime import datetime
from pathlib import Path

from .base_agent import Agent
sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.notification_tool import NotificationTool
from utils.helpers import format_currency

logger = logging.getLogger(__name__)


class NotificationAgent(Agent):
    """Agent responsible for sending smart notifications"""
    
    def __init__(self, output_format: str = 'console', memory_manager: Optional[Any] = None):
        super().__init__("NotificationAgent")
        self.notification_tool = NotificationTool(output_format=output_format)
        self.memory = memory_manager
        self.notifications = []
    
    def plan(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Plan notification approach"""
        plan = {
            'task': task,
            'steps': [
                'Collect insights and alerts',
                'Format notifications',
                'Send notifications',
                'Return notification summary'
            ]
        }
        return plan
    
    def act(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute smart notification sending with prioritization and de-duplication"""
        analysis = self.context.get('analysis', {})
        results = self.context.get('results', {})
        
        raw_notifications = []
        
        # 1. Critical Alerts (Budgets)
        budget_alerts = results.get('budgeting', {}).get('result', {}).get('alerts', [])
        for alert in budget_alerts:
            raw_notifications.append({
                'type': 'alert', 'priority': 'high', 'title': f"Budget {alert['level']}",
                'message': alert['message']
            })
            
        # 2. Trends & Insights
        trends = analysis.get('trends', [])
        for trend in trends:
            raw_notifications.append({
                'type': 'trend', 'priority': 'medium', 'title': 'Spending Trend',
                'message': trend
            })
            
        # 3. Recommendations
        recs = analysis.get('recommendations', [])
        for rec in recs:
            raw_notifications.append({
                'type': 'recommendation', 'priority': 'medium', 'title': 'Suggestion',
                'message': rec
            })

        # 4. Predictions (Contextual)
        pred = results.get('prediction', {}).get('result', {})
        if pred.get('predicted_total', 0) > analysis.get('total_spending', 0) * 1.5:
             raw_notifications.append({
                'type': 'prediction', 'priority': 'high', 'title': 'Spending Warning',
                'message': f"End-of-month forecast (₹{pred['predicted_total']:.2f}) is significantly higher than current spending."
            })

        # Process and filter duplicates
        sent_count = 0
        final_notifications = []
        
        for n in raw_notifications:
            content_hash = hashlib.md5(f"{n['title']}{n['message']}".encode()).hexdigest()
            
            # Check for duplicates in memory if available
            is_duplicate = False
            if self.memory:
                is_duplicate = self.memory.is_notification_duplicate(content_hash)
            
            if not is_duplicate:
                if self._send_notification(n):
                    sent_count += 1
                    if self.memory:
                        self.memory.log_notification(n['title'], n['message'], content_hash)
                    final_notifications.append(n)
            else:
                self.logger.info(f"Skipping duplicate notification: {n['title']}")

        return {
            'notifications_sent': sent_count,
            'notifications': final_notifications,
            'success': True
        }
    
    def _send_notification(self, notification: Dict[str, Any]) -> bool:
        """Send a single notification using NotificationTool"""
        return self.notification_tool.send_alert(
            title=notification['title'],
            message=notification['message'],
            level=notification.get('priority', 'info')
        )
    
    def get_notifications(self) -> List[Dict[str, Any]]:
        """Get all sent notifications"""
        return self.notifications
    
    def clear_notifications(self):
        """Clear notification history"""
        self.notifications = []

