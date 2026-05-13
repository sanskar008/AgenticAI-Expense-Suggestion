"""Flask API server for Expense Management Frontend"""

import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger
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
CORS(app, resources={r"/api/*": {"origins": "*", "allow_headers": ["Content-Type", "X-User-Id"]}})  # Enable CORS for frontend

# Initialize Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

template = {
    "swagger": "2.0",
    "info": {
        "title": "Agentic AI Expense Manager API",
        "description": "API documentation for the Agentic Personal Finance Manager",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "UserId": {
            "type": "apiKey",
            "name": "X-User-Id",
            "in": "header"
        }
    }
}

swagger = Swagger(app, config=swagger_config, template=template)

# Initialize controller
api_key = os.getenv("DEEPSEEK_API_KEY")
controller = MainAgentController(api_key=api_key)
memory_manager = MemoryManager()

def get_user_id():
    """Helper to get user_id from headers"""
    user_id = request.headers.get('X-User-Id')
    return int(user_id) if user_id and user_id.isdigit() else None

@app.route('/api/auth/send-otp', methods=['POST'])
def send_otp():
    """
    Send OTP to phone number
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            phone_number:
              type: string
              example: "+919876543210"
    responses:
      200:
        description: OTP sent successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
    """
    data = request.get_json()
    phone = data.get('phone_number')
    if not phone:
        return jsonify({"success": False, "error": "Phone number required"}), 400
    
    # In demo mode, we just return success
    logger.info(f"OTP 123456 requested for {phone}")
    return jsonify({"success": True, "message": "OTP sent successfully"})

@app.route('/api/auth/verify-otp', methods=['POST'])
def verify_otp():
    """
    Verify OTP and return user data
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            phone_number:
              type: string
              example: "+919876543210"
            otp:
              type: string
              example: "123456"
    responses:
      200:
        description: Verification successful
        schema:
          type: object
          properties:
            success:
              type: boolean
            user:
              type: object
            token:
              type: string
      401:
        description: Invalid OTP
    """
    data = request.get_json()
    phone = data.get('phone_number')
    otp = data.get('otp')
    
    if not phone or not otp:
        return jsonify({"success": False, "error": "Phone and OTP required"}), 400
    
    if otp != '123456':
        return jsonify({"success": False, "error": "Invalid OTP"}), 401
    
    try:
        # Get or create user
        import sqlite3
        conn = sqlite3.connect(memory_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE phone_number = ?", (phone,))
        user = cursor.fetchone()
        
        if not user:
            cursor.execute("INSERT INTO users (phone_number) VALUES (?)", (phone,))
            conn.commit()
            cursor.execute("SELECT * FROM users WHERE phone_number = ?", (phone,))
            user = cursor.fetchone()
        
        user_dict = dict(user)
        conn.close()
        
        return jsonify({
            "success": True, 
            "user": user_dict,
            "token": f"demo-token-{user_dict['id']}" # Simple demo token
        })
    except Exception as e:
        logger.error(f"Auth error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "API is running"})


@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    """
    Get all expenses from database
    ---
    tags:
      - Expenses
    security:
      - UserId: []
    responses:
      200:
        description: List of expenses
        schema:
          type: object
          properties:
            success:
              type: boolean
            expenses:
              type: array
              items:
                type: object
      401:
        description: Authentication required
    """
    try:
        # Ensure database exists
        memory_manager._ensure_db_exists()
        user_id = get_user_id()
        logger.info(f"📋 GET /api/expenses - User ID: {user_id}")
        if not user_id:
            return jsonify({"success": False, "error": "Authentication required"}), 401

        import sqlite3
        conn = sqlite3.connect(memory_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC LIMIT 1000", (user_id,))
        rows = cursor.fetchall()
        expenses = [dict(row) for row in rows]
        conn.close()
        
        return jsonify({"success": True, "expenses": expenses})
    except Exception as e:
        logger.error(f"Error fetching expenses: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/expenses', methods=['POST'])
def add_expenses():
    """
    Add new expenses and process them through the agent pipeline
    ---
    tags:
      - Expenses
    security:
      - UserId: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          oneOf:
            - type: object
              properties:
                amount:
                  type: number
                description:
                  type: string
                date:
                  type: string
                merchant:
                  type: string
            - type: array
              items:
                type: object
    responses:
      200:
        description: Expenses added and processed
        schema:
          type: object
          properties:
            success:
              type: boolean
            expenses:
              type: array
            analysis:
              type: object
            message:
              type: string
      401:
        description: Authentication required
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False, "error": "Authentication required"}), 401

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
        result = controller.run(expenses_json, user_id=user_id)
        
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
    """
    Delete an expense by ID
    ---
    tags:
      - Expenses
    security:
      - UserId: []
    parameters:
      - name: expense_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Expense deleted
      404:
        description: Expense not found
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False, "error": "Authentication required"}), 401

        import sqlite3
        conn = sqlite3.connect(memory_manager.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM expenses WHERE id = ? AND user_id = ?", (expense_id, user_id))
        conn.commit()
        conn.close()
        
        if cursor.rowcount > 0:
            return jsonify({"success": True, "message": "Expense deleted"})
        else:
            return jsonify({"success": False, "error": "Expense not found or unauthorized"}), 404
            
    except Exception as e:
        logger.error(f"Error deleting expense: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/analysis', methods=['GET'])
def get_analysis():
    """
    Get spending analysis
    ---
    tags:
      - Analysis
    security:
      - UserId: []
    responses:
      200:
        description: Spending analysis data
        schema:
          type: object
          properties:
            success:
              type: boolean
            analysis:
              type: object
            current_expenses:
              type: array
            previous_expenses:
              type: array
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False, "error": "Authentication required"}), 401

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
            WHERE user_id = ? AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
            ORDER BY date DESC
        """, (user_id, str(year), f"{month:02d}"))
        
        current_expenses = [dict(row) for row in cursor.fetchall()]
        
        # Get previous month expenses
        from utils.helpers import get_previous_month
        prev_year, prev_month = get_previous_month()
        
        cursor.execute("""
            SELECT * FROM expenses
            WHERE user_id = ? AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
            ORDER BY date DESC
        """, (user_id, str(prev_year), f"{prev_month:02d}"))
        
        previous_expenses = [dict(row) for row in cursor.fetchall()]
        
        # Get cached analysis
        cursor.execute("""
            SELECT analysis_data FROM analysis_cache
            WHERE user_id = ? AND year = ? AND month = ?
        """, (user_id, year, month))
        
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
                        "previous_data": previous_expenses,
                        "user_id": user_id
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
    """
    Get stored insights and recommendations
    ---
    tags:
      - Analysis
    security:
      - UserId: []
    responses:
      200:
        description: List of insights
        schema:
          type: object
          properties:
            success:
              type: boolean
            insights:
              type: array
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False, "error": "Authentication required"}), 401

        from utils.helpers import get_current_month
        year, month = get_current_month()
        
        import sqlite3
        conn = sqlite3.connect(memory_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM insights
            WHERE user_id = ? AND year = ? AND month = ?
            ORDER BY created_at DESC
        """, (user_id, year, month))
        
        insights = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({"success": True, "insights": insights})
        
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    Get quick statistics
    ---
    tags:
      - Analysis
    security:
      - UserId: []
    responses:
      200:
        description: Quick statistics
        schema:
          type: object
          properties:
            success:
              type: boolean
            stats:
              type: object
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False, "error": "Authentication required"}), 401

        import sqlite3
        conn = sqlite3.connect(memory_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Total expenses count
        cursor.execute("SELECT COUNT(*) as count FROM expenses WHERE user_id = ?", (user_id,))
        total_count = cursor.fetchone()["count"]
        
        # Total spending
        cursor.execute("SELECT SUM(amount) as total FROM expenses WHERE user_id = ?", (user_id,))
        total_spending = cursor.fetchone()["total"] or 0
        
        # This month's spending
        from utils.helpers import get_current_month
        year, month = get_current_month()
        cursor.execute("""
            SELECT SUM(amount) as total FROM expenses
            WHERE user_id = ? AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
        """, (user_id, str(year), f"{month:02d}"))
        month_spending = cursor.fetchone()["total"] or 0
        
        # Category breakdown
        cursor.execute("""
            SELECT category, SUM(amount) as total, COUNT(*) as count
            FROM expenses
            WHERE user_id = ?
            GROUP BY category
            ORDER BY total DESC
        """, (user_id,))
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


@app.route('/api/budgets', methods=['GET'])
def get_budgets():
    """
    Get budget status
    ---
    tags:
      - Budgets
    security:
      - UserId: []
    responses:
      200:
        description: Budget status for current month
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False, "error": "Authentication required"}), 401

        from utils.helpers import get_current_month
        year, month = get_current_month()
        
        budgets = memory_manager.get_budgets(user_id, month, year)
        spending = memory_manager.get_spending_by_category(user_id, month, year)
        
        status = []
        for b in budgets:
            cat = b['category']
            spent = spending.get(cat, 0)
            status.append({
                "category": cat,
                "budget": b['amount'],
                "spent": spent,
                "remaining": b['amount'] - spent,
                "percent": (spent / b['amount'] * 100) if b['amount'] > 0 else 0
            })
            
        return jsonify({"success": True, "budgets": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    """
    Get spending predictions
    ---
    tags:
      - Analysis
    security:
      - UserId: []
    responses:
      200:
        description: Spending predictions
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False, "error": "Authentication required"}), 401

        result = controller.predictor.execute(task="Predict end-of-month spending", context={"user_id": user_id})
        return jsonify({"success": True, "prediction": result.get("result", {})})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/goals', methods=['GET'])
def get_goals():
    """
    Get savings goals
    ---
    tags:
      - Budgets
    security:
      - UserId: []
    responses:
      200:
        description: Savings goals
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False, "error": "Authentication required"}), 401

        result = controller.goal_planner.execute(task="Analyze goals", context={"user_id": user_id})
        return jsonify({"success": True, "goals": result.get("result", {})})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Chat with the AI Copilot
    ---
    tags:
      - Chat
    security:
      - UserId: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            message:
              type: string
    responses:
      200:
        description: AI response
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False, "error": "Authentication required"}), 401

        data = request.get_json()
        message = data.get("message", "")
        
        # Use controller to reason and act based on chat
        result = controller.run(f"User Question: {message}", user_id=user_id)
        
        # Format a nice response based on agent results
        response = "I've analyzed your data. "
        if result.get("result"):
            res = result["result"]
            if "analysis" in res:
                response += " ".join(res["analysis"].get("result", {}).get("insights", []))
        
        return jsonify({"success": True, "response": response, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

