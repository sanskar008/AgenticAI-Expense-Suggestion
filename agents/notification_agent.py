"""Notification Agent - Sends notifications and suggestions"""

from typing import Any, Dict, List, Optional
import logging
import sys
from datetime import datetime
from pathlib import Path

from .base_agent import Agent
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.helpers import format_currency

logger = logging.getLogger(__name__)


class NotificationAgent(Agent):
    """Sends notifications and suggestions to user"""
    
    def __init__(self, output_format: str = 'console'):
        super().__init__("NotificationAgent")
        self.output_format = output_format  # 'console' or 'api'
        self.notifications = []
    
    def plan(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Plan notification approach"""
        plan = {
            'task': task,
            'output_format': self.output_format,
            'steps': [
                'Collect insights and alerts',
                'Format notifications',
                'Send notifications',
                'Return notification summary'
            ]
        }
        return plan
    
    def act(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute notification sending"""
        analysis = self.context.get('analysis', {})
        alerts = analysis.get('overspending_alerts', [])
        insights = analysis.get('insights', [])
        recommendations = analysis.get('recommendations', [])
        trends = analysis.get('trends', [])
        
        notifications = []
        
        # Create notification for alerts
        if alerts:
            notifications.append({
                'type': 'alert',
                'priority': 'high',
                'title': 'Overspending Alerts',
                'message': '\n'.join(f"⚠️  {alert}" for alert in alerts),
                'timestamp': datetime.now().isoformat()
            })
        
        # Create notification for insights
        if insights:
            notifications.append({
                'type': 'insight',
                'priority': 'medium',
                'title': 'Spending Insights',
                'message': '\n'.join(f"💡 {insight}" for insight in insights),
                'timestamp': datetime.now().isoformat()
            })
        
        # Create notification for recommendations
        if recommendations:
            notifications.append({
                'type': 'recommendation',
                'priority': 'medium',
                'title': 'Recommendations',
                'message': '\n'.join(f"📌 {rec}" for rec in recommendations),
                'timestamp': datetime.now().isoformat()
            })
        
        # Create notification for trends
        if trends:
            notifications.append({
                'type': 'trend',
                'priority': 'low',
                'title': 'Spending Trends',
                'message': '\n'.join(f"📊 {trend}" for trend in trends),
                'timestamp': datetime.now().isoformat()
            })
        
        # Create summary notification
        total_spending = analysis.get('total_spending', 0)
        if total_spending > 0:
            notifications.append({
                'type': 'summary',
                'priority': 'info',
                'title': 'Spending Summary',
                'message': f"Total spending: {format_currency(total_spending)}",
                'timestamp': datetime.now().isoformat()
            })
        
        # Send notifications
        sent_count = 0
        for notification in notifications:
            if self._send_notification(notification):
                sent_count += 1
                self.notifications.append(notification)
        
        return {
            'notifications_sent': sent_count,
            'notifications': notifications,
            'success': True
        }
    
    def _send_notification(self, notification: Dict[str, Any]) -> bool:
        """Send a single notification"""
        if self.output_format == 'console':
            return self._send_console_notification(notification)
        elif self.output_format == 'api':
            return self._send_api_notification(notification)
        else:
            self.logger.warning(f"Unknown output format: {self.output_format}")
            return False
    
    def _send_console_notification(self, notification: Dict[str, Any]) -> bool:
        """Send notification to console"""
        try:
            priority_icons = {
                'high': '🔴',
                'medium': '💡',
                'low': '📊',
                'info': 'ℹ️'
            }
            
            icon = priority_icons.get(notification['priority'], 'ℹ️')
            title = notification['title']
            message = notification['message']
            
            print(f"\n{icon} {title}")
            print("-" * 60)
            print(message)
            print()
            
            return True
        except Exception as e:
            self.logger.error(f"Error sending console notification: {e}")
            return False
    
    def _send_api_notification(self, notification: Dict[str, Any]) -> bool:
        """Send notification via API (placeholder for future implementation)"""
        # This would integrate with external notification services
        # For now, just log it
        self.logger.info(f"API notification: {notification}")
        return True
    
    def get_notifications(self) -> List[Dict[str, Any]]:
        """Get all sent notifications"""
        return self.notifications
    
    def clear_notifications(self):
        """Clear notification history"""
        self.notifications = []

