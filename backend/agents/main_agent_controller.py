"""Main Agent Controller - Orchestrates all agents with planning and reasoning"""

import os
from typing import Any, Dict, List, Optional
import logging
import sys
from pathlib import Path
from datetime import datetime

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from .base_agent import Agent
from .expense_extractor import ExpenseExtractor
from .expense_classifier import ExpenseClassifier
from .analyzer import ExpenseAnalyzer
from .memory_manager import MemoryManager
from .notification_agent import NotificationAgent
from .budgeting_agent import BudgetingAgent
from .prediction_agent import PredictionAgent
from .goal_planning_agent import GoalPlanningAgent

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.prompts import REASONING_PROMPT
from utils.helpers import parse_json_response, get_current_month, get_previous_month

logger = logging.getLogger(__name__)


class MainAgentController(Agent):
    """Main controller that orchestrates all agents with planning and reasoning"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__("MainAgentController")
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")

        # Initialize sub-agents
        self.extractor = ExpenseExtractor()
        self.classifier = (
            ExpenseClassifier(api_key=self.api_key) if self.api_key else None
        )
        self.analyzer = ExpenseAnalyzer(api_key=self.api_key) if self.api_key else None
        self.memory = MemoryManager()
        self.notifier = NotificationAgent(output_format="console")
        self.budgeter = BudgetingAgent(memory_manager=self.memory)
        self.predictor = PredictionAgent(memory_manager=self.memory)
        self.goal_planner = GoalPlanningAgent(memory_manager=self.memory)

        if OpenAI and self.api_key:
            self.client = OpenAI(
                api_key=self.api_key, base_url="https://api.deepseek.com"
            )
            self.model = "deepseek-chat"
        else:
            self.client = None
            self.model = None
            logger.warning("DeepSeek API not available, using rule-based reasoning")

    def plan(
        self, task: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Plan the overall execution strategy"""
        if context:
            self.context.update(context)

        # Use AI reasoning if available
        if self.model:
            reasoning = self._reason_about_task(task)
            plan = {
                "task": task,
                "reasoning": reasoning,
                "steps": reasoning.get(
                    "required_actions",
                    [
                        "Extract expenses",
                        "Classify expenses",
                        "Retrieve previous data",
                        "Analyze spending",
                        "Store insights",
                        "Send notifications",
                    ],
                ),
                "approach": reasoning.get("approach", "sequential"),
                "next_steps": reasoning.get("next_steps", []),
            }
        else:
            # Default plan
            plan = {
                "task": task,
                "steps": [
                    "Extract expenses from input",
                    "Classify expenses into categories",
                    "Retrieve previous month data from memory",
                    "Analyze spending patterns and trends",
                    "Store current data and insights in memory",
                    "Generate and send notifications",
                ],
                "approach": "sequential",
            }

        # Plan created
        return plan

    def act(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the planned actions dynamically"""
        results = {}
        
        required_agents = plan.get("required_agents", [])
        if not required_agents:
            # Fallback to default sequence if no agents specified
            required_agents = ["extractor", "classifier", "analyzer", "memory", "budgeter", "predictor", "goal_planner", "notifier"]

        if plan.get("is_clarification_needed"):
            print(f"🤔 CLARIFICATION NEEDED: {plan.get('clarification_question')}")
            return {"status": "clarification_needed", "question": plan.get("clarification_question")}

        # Execution context for agents
        agent_map = {
            "extractor": self.extractor,
            "classifier": self.classifier,
            "analyzer": self.analyzer,
            "memory": self.memory,
            "budgeter": self.budgeter,
            "predictor": self.predictor,
            "goal_planner": self.goal_planner,
            "notifier": self.notifier
        }

        try:
            for agent_name in required_agents:
                agent = agent_map.get(agent_name)
                if not agent:
                    continue

                print(f"🚀 INVOKING: {agent_name.upper()}...")
                
                # Dynamic task/context for each agent
                task, context = self._prepare_agent_input(agent_name, results)
                
                agent_result = agent.execute(task=task, context=context)
                results[agent_name] = agent_result
                
                # Check for stopping conditions
                if agent_name == "extractor" and not agent_result.get("result"):
                    print("⚠️ No expenses extracted. Stopping.")
                    break
                
                print(f"✓ {agent_name.capitalize()} completed\n")

            # Final context update
            self.context.update({"results": results})

        except Exception as e:
            logger.error(f"Dynamic execution error: {e}", exc_info=True)
            results["error"] = str(e)

        return results

    def _prepare_agent_input(self, agent_name: str, results: Dict[str, Any]) -> tuple:
        """Prepare specific task and context for each agent"""
        context = self.context.copy()
        
        if agent_name == "extractor":
            return f"Extract from: {self.context.get('input_data')}", {"input_data": self.context.get("input_data"), "user_id": self.context.get("user_id")}
        
        elif agent_name == "classifier":
            expenses = results.get("extractor", {}).get("result", [])
            return "Classify expenses", {"expenses": expenses, "user_id": self.context.get("user_id")}
        
        elif agent_name == "analyzer":
            expenses = results.get("classifier", {}).get("result", [])
            user_id = self.context.get("user_id")
            prev_expenses = self.memory.get_previous_month_data(user_id=user_id) if hasattr(self.memory, 'get_previous_month_data_with_user') else self.memory.get_previous_month_data()
            return "Analyze spending", {"expenses": expenses, "previous_data": prev_expenses, "user_id": user_id}
        
        elif agent_name == "memory":
            expenses = results.get("classifier", {}).get("result", [])
            analysis = results.get("analyzer", {}).get("result", {})
            return "Store data", {"expenses": expenses, "analysis": analysis, "user_id": self.context.get("user_id")}
        
        elif agent_name == "budgeter":
            now = datetime.now()
            return "Track budgets", {"month": now.month, "year": now.year, "user_id": self.context.get("user_id")}
        
        elif agent_name == "predictor":
            return "Predict spending", {"user_id": self.context.get("user_id")}
        
        elif agent_name == "goal_planner":
            return "Analyze goals", {"user_id": self.context.get("user_id")}
        
        elif agent_name == "notifier":
            analysis = results.get("analyzer", {}).get("result", {})
            return "Send notifications", {"analysis": analysis, "user_id": self.context.get("user_id")}

        return f"Perform {agent_name} task", {}

    def reflect(self, result: Any, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Reflect on execution results"""
        reflection = super().reflect(result, plan)

        if result and isinstance(result, dict):
            # Check each step's success
            steps_completed = []
            steps_failed = []

            for step_name, step_result in result.items():
                if step_result and isinstance(step_result, dict):
                    if step_result.get("result") is not None:
                        steps_completed.append(step_name)
                    else:
                        steps_failed.append(step_name)

            reflection["insights"].extend(
                [
                    f"Completed steps: {', '.join(steps_completed)}",
                    f"Failed steps: {', '.join(steps_failed) if steps_failed else 'None'}",
                ]
            )

            # Check for errors
            if "error" in result:
                reflection["insights"].append(f"Execution error: {result['error']}")
                reflection["success"] = False

        # Reflection completed
        return reflection

    def _reason_about_task(self, task: str) -> Dict[str, Any]:
        """Use AI to reason about the task"""
        try:
            previous_analysis = self.memory.get_previous_month_analysis()
            previous_analysis_str = (
                str(previous_analysis) if previous_analysis else "None"
            )

            prompt = REASONING_PROMPT.format(
                context=str(self.context),
                previous_analysis=previous_analysis_str,
                task=task,
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant that reasons about tasks and creates execution plans.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )
            response_text = response.choices[0].message.content.strip()

            reasoning = parse_json_response(response_text)

            if reasoning:
                return reasoning
        except Exception as e:
            logger.error(f"Error in AI reasoning: {e}")

        # Default reasoning
        return {
            "current_state": "Ready to process expenses",
            "required_actions": ["extract", "classify", "analyze", "store", "notify"],
            "potential_issues": [],
            "approach": "sequential",
            "next_steps": [],
        }

    def run(self, input_data: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Main entry point to run the full agent pipeline with metric tracking"""
        import time
        start_time = time.time()
        print(f"🤖 AGENTIC PERSONAL FINANCE MANAGER (User ID: {user_id})\n")

        # Set input data and user_id in context
        self.context = {"input_data": input_data, "user_id": user_id}

        # Execute full cycle
        result = self.execute(
            task="Process expenses and generate insights", context=self.context
        )
        
        # Log metrics
        duration = time.time() - start_time
        self.memory.log_metric(user_id, "response_time", duration)
        
        # Log classification accuracy (confidence)
        if result.get("result", {}).get("classifier"):
            conf = result["result"]["classifier"]["reflection"].get("insights", ["0.0"])[-1]
            try:
                avg_conf = float(conf.split(": ")[1])
                self.memory.log_metric(user_id, "classification_confidence", avg_conf)
            except: pass

        print(f"✅ EXECUTION COMPLETE (Duration: {duration:.2f}s)\n")

        return result
