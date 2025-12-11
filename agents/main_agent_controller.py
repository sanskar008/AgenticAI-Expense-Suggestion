"""Main Agent Controller - Orchestrates all agents with planning and reasoning"""

import os
from typing import Any, Dict, List, Optional
import logging
import sys
from pathlib import Path

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
        """Execute the planned actions"""
        results = {
            "extraction": None,
            "classification": None,
            "analysis": None,
            "memory": None,
            "notifications": None,
        }

        try:
            # Step 1: Extract expenses
            print("STEP 1: Extracting expenses...")
            input_data = self.context.get("input_data", "")
            extraction_result = self.extractor.execute(
                task=f"Extract expenses from: {input_data}",
                context={"input_data": input_data},
            )
            expenses = extraction_result["result"]
            results["extraction"] = extraction_result

            if not expenses:
                print("ERROR: No expenses extracted. Stopping execution.")
                return results

            print(f"✓ Extracted {len(expenses)} expenses\n")

            # Step 2: Classify expenses
            print("STEP 2: Classifying expenses...")
            if self.classifier:
                classification_result = self.classifier.execute(
                    task="Classify all expenses into categories",
                    context={"expenses": expenses},
                )
                classified_expenses = classification_result["result"]
                results["classification"] = classification_result
                print(f"✓ Classified {len(classified_expenses)} expenses\n")
            else:
                print("WARNING: Classifier not available, skipping classification\n")
                classified_expenses = expenses

            # Step 3: Retrieve previous data
            print("STEP 3: Retrieving previous month data...")
            previous_expenses = self.memory.get_previous_month_data()
            previous_analysis = self.memory.get_previous_month_analysis()
            print(f"✓ Retrieved {len(previous_expenses)} previous expenses\n")

            # Step 4: Analyze spending
            print("STEP 4: Analyzing spending patterns...")
            if self.analyzer:
                analysis_result = self.analyzer.execute(
                    task="Analyze spending patterns and generate insights",
                    context={
                        "expenses": classified_expenses,
                        "previous_data": previous_expenses,
                    },
                )
                analysis = analysis_result["result"]
                results["analysis"] = analysis_result
                print("✓ Analysis completed\n")
            else:
                print("WARNING: Analyzer not available, creating basic analysis\n")
                analysis = {
                    "total_spending": sum(
                        exp.get("amount", 0) for exp in classified_expenses
                    ),
                    "insights": ["Basic analysis completed"],
                    "recommendations": ["Continue tracking expenses"],
                }

            # Step 5: Store in memory
            print("STEP 5: Storing data in memory...")
            memory_result = self.memory.execute(
                task="Store expenses and insights",
                context={"expenses": classified_expenses, "analysis": analysis},
            )
            results["memory"] = memory_result
            print("✓ Data stored in memory\n")

            # Step 6: Send notifications
            print("STEP 6: Sending notifications...")
            notification_result = self.notifier.execute(
                task="Send notifications with insights and recommendations",
                context={"analysis": analysis},
            )
            results["notifications"] = notification_result
            notif_count = notification_result.get("result", {}).get(
                "notifications_sent", 0
            )
            print(f"✓ {notif_count} notifications sent\n")

            # Store final results in context
            self.context.update(
                {
                    "expenses": classified_expenses,
                    "analysis": analysis,
                    "results": results,
                }
            )

        except Exception as e:
            logger.error(f"Error in MainAgentController execution: {e}", exc_info=True)
            results["error"] = str(e)

        return results

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

    def run(self, input_data: str) -> Dict[str, Any]:
        """Main entry point to run the full agent pipeline"""
        print("🤖 AGENTIC PERSONAL FINANCE MANAGER\n")

        # Set input data in context
        self.context = {"input_data": input_data}

        # Execute full cycle
        result = self.execute(
            task="Process expenses and generate insights", context=self.context
        )

        print("✅ EXECUTION COMPLETE\n")

        return result
