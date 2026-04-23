"""Prompt templates for DeepSeek API interactions"""

EXPENSE_CLASSIFICATION_PROMPT = """You are an expert expense classifier. Analyze the following expense entry and classify it into one of these categories:

Categories: Food, Rent, Travel, Entertainment, Utilities, Healthcare, Shopping, Transportation, Education, Insurance, Savings, Other

Expense Entry: {expense_text}

Provide your response in JSON format:
{{
    "category": "category_name",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}}

Only return the JSON, no additional text."""


EXPENSE_ANALYSIS_PROMPT = """You are a financial analyst. Analyze the following expense data and provide insights:

Expense Data:
{expense_data}

Previous Month Data (if available):
{previous_data}

Provide insights in JSON format:
{{
    "total_spending": number,
    "category_breakdown": {{"category": amount}},
    "trends": ["trend1", "trend2"],
    "overspending_alerts": ["alert1", "alert2"],
    "insights": ["insight1", "insight2"],
    "recommendations": ["recommendation1", "recommendation2"]
}}

Only return the JSON, no additional text."""


REASONING_PROMPT = """You are an AI financial copilot. Analyze the current state and task to plan the execution.

Context: {context}
Previous Analysis: {previous_analysis}
Task: {task}

Available Agents:
- extractor: Extract expenses from text
- classifier: Categorize expenses
- analyzer: Generate spending insights
- memory: Store/Retrieve data
- budgeter: Check against budgets (Invoke if spending is high or user asks)
- predictor: Forecast end-of-month spending (Invoke if trends detected)
- goal_planner: Analyze savings goals (Invoke if goals exist)
- notifier: Send notifications

Plan the execution dynamically. If data is missing or incomplete, set is_clarification_needed to true.

Provide your reasoning and plan in JSON format:
{{
    "reasoning": "brief explanation of your logic",
    "required_agents": ["agent1", "agent2"],
    "is_clarification_needed": boolean,
    "clarification_question": "question to user if data is missing",
    "approach": "sequential or conditional",
    "next_steps": ["step1", "step2"]
}}

Only return the JSON, no additional text."""


MEMORY_RETRIEVAL_PROMPT = """You are a memory retrieval system. Given the following query and stored memories:

Query: {query}

Stored Memories:
{memories}

Identify the most relevant memories and provide context in JSON format:
{{
    "relevant_memories": [
        {{"memory": "memory_text", "relevance_score": 0.0-1.0}}
    ],
    "context_summary": "summary of relevant context"
}}

Only return the JSON, no additional text."""
