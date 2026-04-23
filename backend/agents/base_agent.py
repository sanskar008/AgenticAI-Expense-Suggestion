"""Base Agent class with plan, act, and reflect methods"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class Agent(ABC):
    """Base class for all agents implementing the plan → act → reflect pattern"""
    
    def __init__(self, name: str):
        self.name = name
        self.context: Dict[str, Any] = {}
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    def plan(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Plan the approach for the given task.
        
        Args:
            task: Description of the task to perform
            context: Additional context information
            
        Returns:
            Dictionary containing the plan with steps and approach
        """
        pass
    
    @abstractmethod
    def act(self, plan: Dict[str, Any]) -> Any:
        """
        Execute the planned actions.
        
        Args:
            plan: The plan dictionary from plan() method
            
        Returns:
            Result of the execution
        """
        pass
    
    def reflect(self, result: Any, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reflect on the execution results and update context.
        
        Args:
            result: The result from act() method
            plan: The original plan
            
        Returns:
            Reflection dictionary with insights and improvements
        """
        reflection = {
            'success': result is not None,
            'result': result,
            'plan': plan,
            'insights': []
        }
        
        if result is None:
            reflection['insights'].append(f"{self.name} execution returned None")
        else:
            reflection['insights'].append(f"{self.name} execution completed successfully")
        
        # Reflection completed
        return reflection
    
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute the full plan → act → reflect cycle.
        
        Args:
            task: Description of the task to perform
            context: Additional context information
            
        Returns:
            Result of the execution with reflection
        """
        if context:
            self.context.update(context)
        
        plan = self.plan(task, self.context)
        result = self.act(plan)
        reflection = self.reflect(result, plan)
        
        return {
            'result': result,
            'reflection': reflection,
            'context': self.context
        }

