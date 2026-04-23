# 🚀 How to Run and Test the Financial Copilot

Follow these steps to get your Agentic Financial Copilot up and running.

## 1. Prerequisites
- **Python 3.10+** installed.
- **Node.js 18+** installed.
- **DeepSeek API Key**: Ensure your `.env` file has a valid `DEEPSEEK_API_KEY`.

## 2. Backend Setup
1. Open a terminal and enter the backend directory:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Seed the database with dummy data:
   ```bash
   python seed_data.py
   ```
4. Start the Flask server:
   ```bash
   python api.py
   ```
   The backend will run on `http://localhost:5000`.

## 3. Frontend Setup
1. Open a new terminal in the `frontend` directory.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   The frontend will run on `http://localhost:5173` (or similar).

## 4. Testing the System

### A. Dashboard Overview
- Visit the frontend URL in your browser.
- You should see the **AI Copilot** section with a "Forecast" chart and "Budget vs Actual" progress bars (if you seeded the data).

### B. Adding Expenses (Agentic Pipeline)
- Go to the "Add Expense" section.
- Try adding a raw description like: `"Spent ₹1200 on Zomato for dinner tonight"`
- The **Agentic Pipeline** will:
  1. **Extract**: Identify amount (1200) and merchant (Zomato).
  2. **Classify**: Categorize as "Food".
  3. **Analyze**: Check if this puts you over budget.
  4. **Notify**: Show a smart notification if needed.

### C. Testing the AI Copilot Chat
- Scroll to the **Chat** widget.
- Ask questions like:
  - `"How much did I spend on food this month?"`
  - `"Am I overspending anywhere?"`
  - `"Will I be able to save ₹10,000 this month?"`

### D. Testing SMS/Bank Data
- You can paste a bank SMS into the "Add Expense" area to test the parser:
  - `"Debited by Rs.500.00 on 23-APR-26 at Amazon. Ref No: 12345"`

## 5. Metrics & Performance
- Check the terminal output where `api.py` is running to see **Agentic Reasoning** logs and execution times.
- Each run logs metrics to the database for long-term evaluation.
