"""Notification Tool - Handles alerts and messaging"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class NotificationTool:
    def __init__(self, output_format: str = "console"):
        self.output_format = output_format

    def send_alert(self, title: str, message: str, level: str = "info"):
        formatted_msg = f"[{level.upper()}] {title}: {message}"
        
        if self.output_format == "console":
            print(formatted_msg)
        
        # Here you could add Slack, Email, or Push notifications
        logger.info(f"Notification Sent: {formatted_msg}")
        return True

    def batch_alerts(self, alerts: List[Dict[str, str]]):
        for alert in alerts:
            self.send_alert(
                alert.get("title", "Alert"),
                alert.get("message", ""),
                alert.get("level", "info")
            )
        return len(alerts)
