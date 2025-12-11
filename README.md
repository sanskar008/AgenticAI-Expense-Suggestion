# 💰 AgenticAI - Expense Manager

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-19.2-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![DeepSeek](https://img.shields.io/badge/DeepSeek-AI-00A8E8?style=for-the-badge)

**An intelligent, AI-powered personal finance management system with a modern web interface**

[Features](#-features) • [Tech Stack](#-tech-stack) • [Installation](#-installation) • [Usage](#-usage) • [API Documentation](#-api-documentation)

</div>

---

## 📖 Overview

AgenticAI Expense Manager is a full-stack personal finance application that leverages **AI agents** and **DeepSeek AI** to intelligently manage, classify, and analyze your expenses. Built with a modern React frontend and Flask backend, it provides real-time insights, spending pattern analysis, and actionable recommendations.

### Key Highlights

- 🤖 **AI-Powered Classification** - Automatically categorizes expenses using DeepSeek AI
- 📊 **Real-time Analytics** - Interactive charts and visualizations
- 🧠 **Agentic Architecture** - Modular agent system with plan-act-reflect pattern
- 💾 **Persistent Storage** - SQLite database with intelligent caching
- 🎨 **Modern UI** - Beautiful, responsive dark-themed interface
- 🔄 **Multi-format Support** - JSON, CSV, text, and SMS-like formats

---

## ✨ Features

### Core Functionality

- **📥 Multi-format Expense Extraction**
  - JSON, CSV, plain text, and SMS-like formats
  - Automatic format detection
  - Data normalization and validation

- **🤖 AI-Powered Classification**
  - Automatic expense categorization using DeepSeek AI
  - 12+ predefined categories (Food, Rent, Travel, Entertainment, etc.)
  - Context-aware classification with confidence scores

- **📈 Advanced Analytics**
  - Spending pattern analysis
  - Month-over-month comparisons
  - Category breakdown with visual charts
  - Trend detection and anomaly identification
  - Overspending alerts

- **💡 Intelligent Insights**
  - AI-generated spending insights
  - Personalized recommendations
  - Budget suggestions
  - Spending pattern recognition

- **💾 Long-term Memory**
  - Persistent SQLite database
  - Historical data tracking
  - Cached analysis results
  - Smart memory retrieval

### Frontend Features

- **🎨 Modern Dashboard**
  - Real-time statistics
  - Category breakdown with progress bars
  - Recent expenses list
  - Quick actions

- **📋 Expense Management**
  - Add, view, and delete expenses
  - Search and filter functionality
  - Category-based filtering
  - Date-based sorting

- **📊 Visual Analytics**
  - Interactive bar charts
  - Pie charts for category distribution
  - Trend visualizations
  - Responsive design

- **💰 Currency Support**
  - Indian Rupees (₹) formatting
  - Proper number formatting (lakhs, crores)
  - Consistent currency display

---

## 🛠️ Tech Stack

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 19.2.0 | UI framework |
| **Vite** | 7.2.4 | Build tool & dev server |
| **React Router** | 6.20.0 | Client-side routing |
| **Axios** | 1.6.0 | HTTP client |
| **Recharts** | 2.10.0 | Chart library |
| **React Icons** | 5.0.1 | Icon library |

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.10+ | Programming language |
| **Flask** | 3.0.0 | Web framework |
| **Flask-CORS** | 4.0.0 | Cross-origin resource sharing |
| **SQLite** | Built-in | Database |
| **OpenAI SDK** | 1.0.0+ | DeepSeek API client |
| **Pandas** | 2.0.0+ | Data processing |
| **Python-dotenv** | 1.0.0+ | Environment variables |

### AI & Services

- **DeepSeek AI** - Expense classification and analysis
- **Agentic Architecture** - Modular agent system

### Development Tools

- **ESLint** - Code linting
- **Vite** - Fast HMR and build
- **Git** - Version control

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────┐
│  React Frontend │
│  (Port 3000)    │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  Flask API     │
│  (Port 5000)   │
└────────┬────────┘
         │
         ├──► Agent System
         │    ├── ExpenseExtractor
         │    ├── ExpenseClassifier (AI)
         │    ├── ExpenseAnalyzer (AI)
         │    ├── MemoryManager
         │    └── NotificationAgent
         │
         ├──► SQLite Database
         │    ├── expenses
         │    ├── insights
         │    └── analysis_cache
         │
         └──► DeepSeek AI API
              └── Classification & Analysis
```

### Agent System

The application uses an **agentic architecture** where specialized agents handle different tasks:

1. **ExpenseExtractor** - Extracts and parses expense data from various formats
2. **ExpenseClassifier** - Uses AI to categorize expenses intelligently
3. **ExpenseAnalyzer** - Analyzes spending patterns and generates insights
4. **MemoryManager** - Handles database operations and data persistence
5. **NotificationAgent** - Generates and sends notifications
6. **MainAgentController** - Orchestrates all agents with planning and reasoning

Each agent follows the **Plan → Act → Reflect** pattern:
- **Plan**: Determines the approach for a task
- **Act**: Executes the planned actions
- **Reflect**: Reviews execution and updates context

---

## 📁 Project Structure

```
AgenticAI-Expense-Suggestion/
│
├── frontend/                    # React frontend application
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── Dashboard.jsx   # Main dashboard
│   │   │   ├── Expenses.jsx    # Expense list & management
│   │   │   ├── AddExpense.jsx  # Add expense form
│   │   │   ├── Analysis.jsx    # Analytics & charts
│   │   │   └── ErrorBoundary.jsx
│   │   ├── services/
│   │   │   └── api.js          # API service layer
│   │   ├── utils/
│   │   │   └── currency.js     # Currency formatting
│   │   ├── App.jsx             # Main app component
│   │   └── main.jsx            # Entry point
│   ├── package.json
│   └── vite.config.js
│
├── agents/                      # Agent system
│   ├── base_agent.py           # Base agent class
│   ├── expense_extractor.py    # Extraction agent
│   ├── expense_classifier.py   # Classification agent (AI)
│   ├── analyzer.py             # Analysis agent (AI)
│   ├── memory_manager.py       # Database agent
│   ├── notification_agent.py   # Notification agent
│   └── main_agent_controller.py # Main orchestrator
│
├── utils/                        # Utility functions
│   ├── helpers.py              # Helper functions
│   └── prompts.py              # AI prompts
│
├── database/                    # SQLite database
│   └── expenses.db             # Auto-created database
│
├── data/                        # Sample data
│   └── expenses.json
│
├── api.py                       # Flask API server
├── main.py                      # CLI entry point
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
└── README.md                    # This file
```

---

## 🚀 Installation

### Prerequisites

- **Python** 3.10 or higher
- **Node.js** 18+ and npm
- **DeepSeek API Key** ([Get one here](https://platform.deepseek.com/))

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/AgenticAI-Expense-Suggestion.git
cd AgenticAI-Expense-Suggestion
```

### Step 2: Backend Setup

1. **Create a virtual environment** (recommended):

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

2. **Install Python dependencies**:

```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:

Create a `.env` file in the project root:

```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
PORT=5000
```

### Step 3: Frontend Setup

1. **Navigate to frontend directory**:

```bash
cd frontend
```

2. **Install dependencies**:

```bash
npm install
```

3. **Create `.env` file** (optional):

```env
VITE_API_URL=http://localhost:5000/api
```

### Step 4: Run the Application

1. **Start the backend server** (in project root):

```bash
python api.py
```

The API will run on `http://localhost:5000`

2. **Start the frontend** (in a new terminal, from `frontend/` directory):

```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

3. **Open your browser** and navigate to `http://localhost:3000`

---

## 💻 Usage

### Web Interface

1. **Dashboard** - View overview statistics and recent expenses
2. **Add Expense** - Add new expenses with automatic AI classification
3. **Expenses** - Browse, search, and filter all expenses
4. **Analysis** - View detailed analytics, charts, and insights

### CLI Usage

Run the command-line interface:

```bash
python main.py
```

This processes sample expenses and displays results in the terminal.

### Programmatic Usage

```python
from agents.main_agent_controller import MainAgentController
import json

# Initialize controller
controller = MainAgentController(api_key="your_api_key")

# Prepare expense data
expenses = [
    {
        "amount": 450.00,
        "description": "Lunch at Punjabi Dhaba",
        "date": "2024-11-12T12:30:00",
        "merchant": "Punjabi Tadka"
    }
]

# Process expenses
input_data = json.dumps(expenses)
result = controller.run(input_data)

# Access results
analysis = result['result']['analysis']['result']
print(f"Total spending: ₹{analysis['total_spending']:,.2f}")
```

### Input Formats

#### JSON
```json
[
  {
    "amount": 450.00,
    "description": "Lunch at restaurant",
    "date": "2024-11-12T12:30:00",
    "merchant": "Restaurant Name"
  }
]
```

#### CSV
```csv
amount,description,date,merchant
450.00,Lunch at restaurant,2024-11-12T12:30:00,Restaurant Name
25000.00,Monthly Rent,2024-11-01T09:00:00,Landlord
```

#### SMS-like Text
```
Rs. 450.00 debited for lunch at restaurant
INR 25000.00 spent on monthly rent payment
```

---

## 📡 API Documentation

### Base URL

```
http://localhost:5000/api
```

### Endpoints

#### Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

#### Get All Expenses
```http
GET /api/expenses
```

**Response:**
```json
{
  "success": true,
  "expenses": [
    {
      "id": 1,
      "amount": 450.00,
      "description": "Lunch at restaurant",
      "category": "Food",
      "date": "2024-11-12T12:30:00",
      "merchant": "Restaurant Name"
    }
  ]
}
```

#### Add Expenses
```http
POST /api/expenses
Content-Type: application/json
```

**Request Body:**
```json
{
  "amount": 450.00,
  "description": "Lunch at restaurant",
  "date": "2024-11-12T12:30:00",
  "merchant": "Restaurant Name"
}
```

**Response:**
```json
{
  "success": true,
  "expenses": [...],
  "analysis": {...},
  "message": "Expenses processed successfully"
}
```

#### Delete Expense
```http
DELETE /api/expenses/{id}
```

#### Get Analysis
```http
GET /api/analysis
```

Returns spending analysis with insights and recommendations.

#### Get Statistics
```http
GET /api/stats
```

Returns quick statistics (total spending, category breakdown, etc.).

#### Get Insights
```http
GET /api/insights
```

Returns stored insights and recommendations.

---

## 🎯 Key Features Explained

### AI-Powered Classification

The system uses **DeepSeek AI** to intelligently classify expenses based on:
- Description text
- Merchant information
- Amount context
- Historical patterns

Categories include: Food, Rent, Travel, Entertainment, Utilities, Healthcare, Shopping, Transportation, Education, Insurance, Savings, Other

### Agentic Architecture

Each agent operates independently with:
- **Planning**: Determines the best approach
- **Execution**: Performs the task
- **Reflection**: Reviews and learns from results

This allows for:
- Modular development
- Easy testing
- Scalable architecture
- Independent agent updates

### Data Persistence

- **SQLite Database**: Lightweight, file-based storage
- **Automatic Schema**: Tables created on first run
- **Caching**: Monthly analysis results cached for performance
- **Historical Tracking**: All expenses stored with timestamps

---

## 🎨 Screenshots

> **Note**: Add screenshots of your application here

- Dashboard view
- Expense management
- Analytics charts
- Add expense form

---

## 🔧 Configuration

### Environment Variables

**Backend (`.env`):**
```env
DEEPSEEK_API_KEY=your_api_key_here
PORT=5000
```

**Frontend (`frontend/.env`):**
```env
VITE_API_URL=http://localhost:5000/api
```

### Customization

#### Adding Categories

Edit `agents/expense_classifier.py`:
```python
self.categories = [
    'Food', 'Rent', 'Travel', 'Entertainment',
    'YourCustomCategory',  # Add here
]
```

#### Modifying Analysis

Edit `agents/analyzer.py` to customize:
- Spending thresholds
- Trend detection
- Recommendation logic

---

## 🐛 Troubleshooting

### Common Issues

**Blank Page / Frontend Not Loading**
- Check browser console for errors
- Ensure backend API is running on port 5000
- Verify all dependencies are installed: `npm install`

**API Connection Errors**
- Ensure Flask server is running: `python api.py`
- Check CORS is enabled in `api.py`
- Verify API URL in frontend `.env`

**Database Issues**
- Database auto-creates on first run
- Delete `database/expenses.db` to reset
- Check file permissions

**Import Errors**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- Check Python version (3.10+)

For more details, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 🚧 Roadmap

- [ ] User authentication and multi-user support
- [ ] Budget planning and tracking
- [ ] Recurring expense detection
- [ ] Export to PDF/Excel
- [ ] Mobile app (React Native)
- [ ] Bank account integration
- [ ] Email/SMS notifications
- [ ] Advanced reporting
- [ ] Multi-currency support

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Areas for Contribution

- Additional data source integrations
- Enhanced analysis algorithms
- UI/UX improvements
- Documentation
- Testing
- Performance optimizations

---

## 📝 License

This project is provided as-is for educational and personal use.

---

## 🙏 Acknowledgments

- **DeepSeek AI** for powerful language model capabilities
- **React** and **Flask** communities for excellent frameworks
- **Font Awesome** for icons
- All open-source contributors

---

## 📧 Contact & Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
- Review [Quick Start Guide](QUICK_START.md)

---

<div align="center">

**Built with ❤️ using Python, React, and DeepSeek AI**

⭐ Star this repo if you find it helpful!

</div>
