"""Main entry point for Agentic Personal Finance Manager"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.main_agent_controller import MainAgentController

# Configure logging - only show warnings and errors
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

logger = logging.getLogger(__name__)


def load_environment():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        pass  # Environment loaded
    else:
        pass  # Using system environment variables


def load_expenses_from_json() -> str:
    """
    Get hardcoded expense data.

    Returns:
        JSON string containing expenses (for ExpenseExtractor to process)
    """
    # Hardcoded expense data (Indian expenses in rupees)
    expenses = [
        {
            "amount": 450.00,
            "description": "Lunch at Punjabi Dhaba",
            "date": "2024-11-12T12:30:00",
            "merchant": "Punjabi Tadka",
        },
        {
            "amount": 25000.00,
            "description": "Monthly Rent Payment",
            "date": "2024-11-01T09:00:00",
            "merchant": "Landlord",
        },
        {
            "amount": 3500.00,
            "description": "Grocery Shopping at D-Mart",
            "date": "2024-11-10T15:20:00",
            "merchant": "D-Mart",
        },
        {
            "amount": 350.00,
            "description": "Ola ride to airport",
            "date": "2024-11-08T06:00:00",
            "merchant": "Ola",
        },
        {
            "amount": 8500.00,
            "description": "Flight ticket to Mumbai",
            "date": "2024-11-08T10:00:00",
            "merchant": "IndiGo Airlines",
        },
        {
            "amount": 4500.00,
            "description": "Hotel booking for business trip",
            "date": "2024-11-08T14:00:00",
            "merchant": "OYO Rooms",
        },
        {
            "amount": 499.00,
            "description": "Netflix subscription",
            "date": "2024-11-05T00:00:00",
            "merchant": "Netflix",
        },
        {
            "amount": 2500.00,
            "description": "Electricity bill",
            "date": "2024-11-03T00:00:00",
            "merchant": "BSES",
        },
        {
            "amount": 1500.00,
            "description": "Gym membership",
            "date": "2024-11-01T00:00:00",
            "merchant": "Gold's Gym",
        },
        {
            "amount": 5000.00,
            "description": "Shopping at Reliance Trends - clothes",
            "date": "2024-11-11T16:30:00",
            "merchant": "Reliance Trends",
        },
        {
            "amount": 280.00,
            "description": "Coffee and breakfast at Cafe Coffee Day",
            "date": "2024-11-13T08:15:00",
            "merchant": "CCD",
        },
        {
            "amount": 2000.00,
            "description": "Petrol fill-up",
            "date": "2024-11-13T18:30:00",
            "merchant": "Indian Oil",
        },
        {
            "amount": 8999.00,
            "description": "New headphones purchase",
            "date": "2024-11-14T14:20:00",
            "merchant": "Croma",
        },
        {
            "amount": 1800.00,
            "description": "Dinner with friends at Barbeque Nation",
            "date": "2024-11-14T19:45:00",
            "merchant": "Barbeque Nation",
        },
        {
            "amount": 600.00,
            "description": "Movie tickets at PVR",
            "date": "2024-11-15T20:00:00",
            "merchant": "PVR Cinemas",
        },
    ]

    # Using hardcoded expenses

    # Convert to JSON string
    return json.dumps(expenses, indent=2)


def main():
    """Main execution function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Agentic Personal Finance Manager - AI-powered expense analysis"
    )
    # Removed --json-file argument since we're using hardcoded expenses
    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("🤖 AGENTIC PERSONAL FINANCE MANAGER")
    print("=" * 70 + "\n")

    # Load environment variables
    load_environment()

    # Check for API key
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("⚠️  WARNING: DEEPSEEK_API_KEY not found in environment variables.")
        print("   Some features (AI classification, analysis) will be limited.")
        print("   Please set DEEPSEEK_API_KEY in .env file or environment.\n")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != "y":
            print("Exiting...")
            return

    try:
        # Initialize main controller
        controller = MainAgentController(api_key=api_key)

        # Get hardcoded expense data
        expenses_json = load_expenses_from_json()

        # Run the agent pipeline (ExpenseExtractor will process the JSON string)
        result = controller.run(expenses_json)

        # Display final summary
        if result.get("result"):
            results = result["result"]
            if results.get("analysis"):
                analysis = results["analysis"].get("result", {})
                total = analysis.get("total_spending", 0)
                print(f"\n📊 Total Spending: ₹{total:,.2f}")

    except KeyboardInterrupt:
        print("\n⚠️  Execution interrupted by user.")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")


if __name__ == "__main__":
    main()
