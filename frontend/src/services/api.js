import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add user ID to headers and log request
api.interceptors.request.use((config) => {
  const user = JSON.parse(localStorage.getItem('user'))
  if (user && user.id) {
    config.headers['X-User-Id'] = user.id
  }
  console.log(`🚀 [API Request] ${config.method.toUpperCase()} ${config.url}`, config.data || '')
  return config
})

// Response interceptor to log response
api.interceptors.response.use(
  (response) => {
    console.log(`✅ [API Response] ${response.config.method.toUpperCase()} ${response.config.url}`, response.data)
    return response
  },
  (error) => {
    console.error(`❌ [API Error] ${error.config?.method?.toUpperCase()} ${error.config?.url}`, error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export const authService = {
  sendOtp: async (phoneNumber) => {
    try {
      const response = await api.post('/auth/send-otp', { phone_number: phoneNumber })
      return response.data
    } catch (error) {
      console.error('Error sending OTP:', error)
      throw error
    }
  },
  verifyOtp: async (phoneNumber, otp) => {
    try {
      const response = await api.post('/auth/verify-otp', { phone_number: phoneNumber, otp })
      if (response.data.success) {
        localStorage.setItem('user', JSON.stringify(response.data.user))
        localStorage.setItem('token', response.data.token)
      }
      return response.data
    } catch (error) {
      console.error('Error verifying OTP:', error)
      throw error
    }
  },
  logout: () => {
    localStorage.removeItem('user')
    localStorage.removeItem('token')
  },
  getCurrentUser: () => {
    return JSON.parse(localStorage.getItem('user'))
  }
}

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
