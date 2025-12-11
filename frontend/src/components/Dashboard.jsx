import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  FaArrowUp,
  FaArrowDown,
  FaWallet,
  FaReceipt,
  FaArrowRight,
} from "react-icons/fa";
import { expenseService } from "../services/api";
import { formatCurrency } from "../utils/currency";
import "./Dashboard.css";

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [recentExpenses, setRecentExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [statsData, expensesData] = await Promise.all([
        expenseService.getStats(),
        expenseService.getExpenses(),
      ]);

      if (statsData.success) {
        setStats(statsData.stats);
      } else if (statsData.error) {
        setError(statsData.error);
      }

      if (expensesData.success) {
        setRecentExpenses(expensesData.expenses.slice(0, 5));
      } else if (expensesData.error) {
        setError(expensesData.error);
      }
    } catch (err) {
      console.error("Dashboard error:", err);
      setError(err.message || "Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString("en-IN", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard">
        <div className="alert alert-error">
          <span>⚠️ Error loading dashboard: {error}</span>
          <p
            style={{
              marginTop: "0.5rem",
              fontSize: "0.875rem",
              color: "var(--text-muted)",
            }}
          >
            Make sure the backend API server is running on http://localhost:5000
          </p>
          <button
            onClick={loadDashboardData}
            className="btn btn-primary"
            style={{ marginTop: "1rem" }}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <Link to="/add" className="btn btn-primary">
          <span>Add Expense</span>
          <FaArrowRight size={16} />
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">
            <FaWallet size={24} />
          </div>
          <div className="stat-label">Total Spending</div>
          <div className="stat-value">
            {formatCurrency(stats?.total_spending || 0)}
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <FaReceipt size={24} />
          </div>
          <div className="stat-label">This Month</div>
          <div className="stat-value">
            {formatCurrency(stats?.month_spending || 0)}
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <FaArrowUp size={24} />
          </div>
          <div className="stat-label">Total Expenses</div>
          <div className="stat-value">{stats?.total_expenses || 0}</div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <FaArrowDown size={24} />
          </div>
          <div className="stat-label">Categories</div>
          <div className="stat-value">
            {stats?.category_breakdown?.length || 0}
          </div>
        </div>
      </div>

      {/* Category Breakdown */}
      {stats?.category_breakdown && stats.category_breakdown.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Top Categories</h2>
          </div>
          <div className="category-list">
            {stats.category_breakdown.slice(0, 5).map((cat, index) => {
              const percentage = (
                (cat.total / stats.total_spending) *
                100
              ).toFixed(1);
              return (
                <div key={index} className="category-item">
                  <div className="category-info">
                    <span className="category-name">
                      {cat.category || "Other"}
                    </span>
                    <span className="category-count">{cat.count} expenses</span>
                  </div>
                  <div className="category-amount">
                    <div className="category-total">
                      {formatCurrency(cat.total)}
                    </div>
                    <div className="category-percentage">{percentage}%</div>
                  </div>
                  <div className="category-bar">
                    <div
                      className="category-bar-fill"
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Recent Expenses */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Recent Expenses</h2>
          <Link to="/expenses" className="btn btn-secondary">
            View All
          </Link>
        </div>
        {recentExpenses.length > 0 ? (
          <div className="expenses-list">
            {recentExpenses.map((expense) => (
              <div key={expense.id} className="expense-item">
                <div className="expense-info">
                  <div className="expense-description">
                    {expense.description}
                  </div>
                  <div className="expense-meta">
                    <span className="badge badge-primary">
                      {expense.category || "Other"}
                    </span>
                    <span className="expense-date">
                      {formatDate(expense.date)}
                    </span>
                  </div>
                </div>
                <div className="expense-amount">
                  {formatCurrency(expense.amount)}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <FaReceipt size={48} className="empty-state-icon" />
            <p>No expenses yet. Add your first expense!</p>
            <Link
              to="/add"
              className="btn btn-primary"
              style={{ marginTop: "1rem" }}
            >
              Add Expense
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
