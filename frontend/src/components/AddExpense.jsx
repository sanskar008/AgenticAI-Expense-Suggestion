import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FaSave, FaArrowLeft } from 'react-icons/fa'
import { ImSpinner2 } from 'react-icons/im'
import { expenseService } from '../services/api'
import './AddExpense.css'

function AddExpense() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)
  const [formData, setFormData] = useState({
    amount: '',
    description: '',
    date: new Date().toISOString().split('T')[0] + 'T' + new Date().toTimeString().slice(0, 5),
    merchant: '',
    category: '',
  })

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSuccess(false)

    try {
      // Validate required fields
      if (!formData.amount || !formData.description) {
        throw new Error('Amount and description are required')
      }

      const expense = {
        amount: parseFloat(formData.amount),
        description: formData.description,
        date: formData.date || new Date().toISOString(),
        merchant: formData.merchant || '',
        category: formData.category || '',
      }

      const data = await expenseService.addExpenses([expense])

      if (data.success) {
        setSuccess(true)
        // Reset form
        setFormData({
          amount: '',
          description: '',
          date: new Date().toISOString().split('T')[0] + 'T' + new Date().toTimeString().slice(0, 5),
          merchant: '',
          category: '',
        })
        // Redirect after 2 seconds
        setTimeout(() => {
          navigate('/expenses')
        }, 2000)
      } else {
        throw new Error(data.error || 'Failed to add expense')
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="add-expense-page">
      <div className="page-header">
        <button className="btn btn-secondary" onClick={() => navigate(-1)}>
          <FaArrowLeft size={16} />
          <span>Back</span>
        </button>
        <h1>Add New Expense</h1>
      </div>

      <div className="card">
        {success && (
          <div className="alert alert-success">
            <span>Expense added successfully! Redirecting...</span>
          </div>
        )}

        {error && (
          <div className="alert alert-error">
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="expense-form">
          <div className="form-group">
            <label htmlFor="amount" className="form-label">
              Amount (₹) *
            </label>
              <div className="amount-input-wrapper">
                <span className="currency-symbol">₹</span>
                <input
                  type="number"
                  id="amount"
                  name="amount"
                  value={formData.amount}
                  onChange={handleChange}
                  className="form-input amount-input"
                  placeholder="0.00"
                  step="0.01"
                  min="0"
                  required
                />
              </div>
          </div>

          <div className="form-group">
            <label htmlFor="description" className="form-label">
              Description *
            </label>
            <input
              type="text"
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              className="form-input"
              placeholder="e.g., Lunch at restaurant"
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="date" className="form-label">
                Date & Time
              </label>
              <input
                type="datetime-local"
                id="date"
                name="date"
                value={formData.date}
                onChange={handleChange}
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label htmlFor="merchant" className="form-label">
                Merchant
              </label>
              <input
                type="text"
                id="merchant"
                name="merchant"
                value={formData.merchant}
                onChange={handleChange}
                className="form-input"
                placeholder="e.g., Restaurant Name"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="category" className="form-label">
              Category (will be auto-classified if empty)
            </label>
            <select
              id="category"
              name="category"
              value={formData.category}
              onChange={handleChange}
              className="form-select"
            >
              <option value="">Auto-classify</option>
              <option value="Food">Food</option>
              <option value="Rent">Rent</option>
              <option value="Travel">Travel</option>
              <option value="Entertainment">Entertainment</option>
              <option value="Utilities">Utilities</option>
              <option value="Healthcare">Healthcare</option>
              <option value="Shopping">Shopping</option>
              <option value="Transportation">Transportation</option>
              <option value="Education">Education</option>
              <option value="Insurance">Insurance</option>
              <option value="Savings">Savings</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? (
                <>
                  <ImSpinner2 size={16} className="spinner-icon" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <FaSave size={16} />
                  <span>Save Expense</span>
                </>
              )}
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => navigate(-1)}
              disabled={loading}
            >
              Cancel
            </button>
          </div>
        </form>
      </div>

      <div className="card info-card">
        <h3>💡 Tip</h3>
        <p>
          If you leave the category empty, our AI will automatically classify your expense based on
          the description and merchant information.
        </p>
      </div>
    </div>
  )
}

export default AddExpense

