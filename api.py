"""Flask API server for Expense Management Frontend"""

import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
from dotenv import load_dotenv
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.main_agent_controller import MainAgentController
from agents.memory_manager import MemoryManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Initialize controller
api_key = os.getenv("DEEPSEEK_API_KEY")
controller = MainAgentController(api_key=api_key)
memory_manager = MemoryManager()


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "API is running"})


@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    """Get all expenses from database"""
    try:
        # Ensure database exists
        memory_manager._ensure_db_exists()
        import sqlite3
        conn = sqlite3.connect(memory_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM expenses ORDER BY date DESC LIMIT 1000")
        rows = cursor.fetchall()
        expenses = [dict(row) for row in rows]
        conn.close()
        
        return jsonify({"success": True, "expenses": expenses})
    except Exception as e:
        logger.error(f"Error fetching expenses: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/expenses', methods=['POST'])
def add_expenses():
    """Add new expenses and process them through the agent pipeline"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        # Handle both single expense and array of expenses
        if isinstance(data, dict):
            expenses = [data]
        elif isinstance(data, list):
            expenses = data
        else:
            return jsonify({"success": False, "error": "Invalid data format"}), 400
        
        # Convert to JSON string for the controller
        expenses_json = json.dumps(expenses)
        
        # Run through the agent pipeline
        result = controller.run(expenses_json)
        
        # Extract results
        if result.get("result"):
            results = result["result"]
            classified_expenses = results.get("classification", {}).get("result", expenses)
            analysis = results.get("analysis", {}).get("result", {})
            
            return jsonify({
                "success": True,
                "expenses": classified_expenses,
                "analysis": analysis,
                "message": "Expenses processed successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to process expenses"
            }), 500
            
    except Exception as e:
        logger.error(f"Error adding expenses: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """Delete an expense by ID"""
    try:
        import sqlite3
        conn = sqlite3.connect(memory_manager.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
        conn.close()
        
        if cursor.rowcount > 0:
            return jsonify({"success": True, "message": "Expense deleted"})
        else:
            return jsonify({"success": False, "error": "Expense not found"}), 404
            
    except Exception as e:
        logger.error(f"Error deleting expense: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/analysis', methods=['GET'])
def get_analysis():
    """Get spending analysis"""
    try:
        # Get current month expenses
        from utils.helpers import get_current_month
        year, month = get_current_month()
        
        # Get expenses for current month
        import sqlite3
        conn = sqlite3.connect(memory_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM expenses
            WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
            ORDER BY date DESC
        """, (str(year), f"{month:02d}"))
        
        current_expenses = [dict(row) for row in cursor.fetchall()]
        
        # Get previous month expenses
        from utils.helpers import get_previous_month
        prev_year, prev_month = get_previous_month()
        
        cursor.execute("""
            SELECT * FROM expenses
            WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
            ORDER BY date DESC
        """, (str(prev_year), f"{prev_month:02d}"))
        
        previous_expenses = [dict(row) for row in cursor.fetchall()]
        
        # Get cached analysis
        cursor.execute("""
            SELECT analysis_data FROM analysis_cache
            WHERE year = ? AND month = ?
        """, (year, month))
        
        row = cursor.fetchone()
        cached_analysis = json.loads(row["analysis_data"]) if row else None
        
        conn.close()
        
        # If no cached analysis, generate one
        if not cached_analysis and current_expenses:
            if controller.analyzer:
                analysis_result = controller.analyzer.execute(
                    task="Analyze spending patterns",
                    context={
                        "expenses": current_expenses,
                        "previous_data": previous_expenses
                    }
                )
                cached_analysis = analysis_result.get("result", {})
        
        return jsonify({
            "success": True,
            "analysis": cached_analysis or {},
            "current_expenses": current_expenses,
            "previous_expenses": previous_expenses
        })
        
    except Exception as e:
        logger.error(f"Error getting analysis: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/insights', methods=['GET'])
def get_insights():
    """Get stored insights and recommendations"""
    try:
        from utils.helpers import get_current_month
        year, month = get_current_month()
        
        import sqlite3
        conn = sqlite3.connect(memory_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM insights
            WHERE year = ? AND month = ?
            ORDER BY created_at DESC
        """, (year, month))
        
        insights = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({"success": True, "insights": insights})
        
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get quick statistics"""
    try:
        import sqlite3
        conn = sqlite3.connect(memory_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Total expenses count
        cursor.execute("SELECT COUNT(*) as count FROM expenses")
        total_count = cursor.fetchone()["count"]
        
        # Total spending
        cursor.execute("SELECT SUM(amount) as total FROM expenses")
        total_spending = cursor.fetchone()["total"] or 0
        
        # This month's spending
        from utils.helpers import get_current_month
        year, month = get_current_month()
        cursor.execute("""
            SELECT SUM(amount) as total FROM expenses
            WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
        """, (str(year), f"{month:02d}"))
        month_spending = cursor.fetchone()["total"] or 0
        
        # Category breakdown
        cursor.execute("""
            SELECT category, SUM(amount) as total, COUNT(*) as count
            FROM expenses
            GROUP BY category
            ORDER BY total DESC
        """)
        category_stats = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            "success": True,
            "stats": {
                "total_expenses": total_count,
                "total_spending": total_spending,
                "month_spending": month_spending,
                "category_breakdown": category_stats
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

