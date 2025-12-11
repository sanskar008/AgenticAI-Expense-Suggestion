import { useState, useEffect } from 'react'
import { FaTrash, FaEdit, FaSearch, FaFilter } from 'react-icons/fa'
import { expenseService } from '../services/api'
import { formatCurrency } from '../utils/currency'
import './Expenses.css'

function Expenses() {
  const [expenses, setExpenses] = useState([])
  const [filteredExpenses, setFilteredExpenses] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterCategory, setFilterCategory] = useState('all')

  useEffect(() => {
    loadExpenses()
  }, [])

  useEffect(() => {
    filterExpenses()
  }, [expenses, searchTerm, filterCategory])

  const loadExpenses = async () => {
    try {
      setLoading(true)
      const data = await expenseService.getExpenses()
      if (data.success) {
        setExpenses(data.expenses)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const filterExpenses = () => {
    let filtered = [...expenses]

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(
        (exp) =>
          exp.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          exp.merchant?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          exp.category?.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Filter by category
    if (filterCategory !== 'all') {
      filtered = filtered.filter((exp) => exp.category === filterCategory)
    }

    setFilteredExpenses(filtered)
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this expense?')) {
      return
    }

    try {
      const data = await expenseService.deleteExpense(id)
      if (data.success) {
        setExpenses(expenses.filter((exp) => exp.id !== id))
      }
    } catch (err) {
      alert('Error deleting expense: ' + err.message)
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const categories = [...new Set(expenses.map((exp) => exp.category).filter(Boolean))]

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="alert alert-error">
        <span>Error loading expenses: {error}</span>
      </div>
    )
  }

  return (
    <div className="expenses-page">
      <div className="page-header">
        <h1>All Expenses</h1>
        <div className="expenses-summary">
          Total: {formatCurrency(expenses.reduce((sum, exp) => sum + (exp.amount || 0), 0))}
        </div>
      </div>

      {/* Filters */}
      <div className="filters">
        <div className="search-box">
          <FaSearch size={20} />
          <input
            type="text"
            placeholder="Search expenses..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="form-input"
          />
        </div>
        <div className="filter-group">
          <FaFilter size={20} />
          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="form-select"
          >
            <option value="all">All Categories</option>
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Expenses Table */}
      {filteredExpenses.length > 0 ? (
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Description</th>
                <th>Merchant</th>
                <th>Category</th>
                <th>Amount</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredExpenses.map((expense) => (
                <tr key={expense.id}>
                  <td>{formatDate(expense.date)}</td>
                  <td>
                    <div className="expense-description-cell">{expense.description}</div>
                  </td>
                  <td>{expense.merchant || '-'}</td>
                  <td>
                    <span className="badge badge-primary">{expense.category || 'Other'}</span>
                  </td>
                  <td>
                    <span className="expense-amount-cell">{formatCurrency(expense.amount)}</span>
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button
                        className="btn-icon btn-danger"
                        onClick={() => handleDelete(expense.id)}
                        title="Delete"
                      >
                        <FaTrash size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="empty-state">
          <p>No expenses found</p>
        </div>
      )}
    </div>
  )
}

export default Expenses

