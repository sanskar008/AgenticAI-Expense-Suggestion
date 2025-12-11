import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const expenseService = {
  // Get all expenses
  getExpenses: async () => {
    try {
      const response = await api.get('/expenses')
      return response.data
    } catch (error) {
      console.error('Error fetching expenses:', error)
      // Return empty data if API is not available
      if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
        return { success: false, expenses: [], error: 'API server is not running' }
      }
      throw error
    }
  },

  // Add new expenses
  addExpenses: async (expenses) => {
    try {
      const response = await api.post('/expenses', expenses)
      return response.data
    } catch (error) {
      console.error('Error adding expenses:', error)
      throw error
    }
  },

  // Delete expense
  deleteExpense: async (id) => {
    try {
      const response = await api.delete(`/expenses/${id}`)
      return response.data
    } catch (error) {
      console.error('Error deleting expense:', error)
      throw error
    }
  },

  // Get analysis
  getAnalysis: async () => {
    try {
      const response = await api.get('/analysis')
      return response.data
    } catch (error) {
      console.error('Error fetching analysis:', error)
      if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
        return { success: false, analysis: {}, error: 'API server is not running' }
      }
      throw error
    }
  },

  // Get stats
  getStats: async () => {
    try {
      const response = await api.get('/stats')
      return response.data
    } catch (error) {
      console.error('Error fetching stats:', error)
      if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
        return { 
          success: false, 
          stats: {
            total_expenses: 0,
            total_spending: 0,
            month_spending: 0,
            category_breakdown: []
          },
          error: 'API server is not running' 
        }
      }
      throw error
    }
  },

  // Get insights
  getInsights: async () => {
    try {
      const response = await api.get('/insights')
      return response.data
    } catch (error) {
      console.error('Error fetching insights:', error)
      if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
        return { success: false, insights: [], error: 'API server is not running' }
      }
      throw error
    }
  },
}

export default api

