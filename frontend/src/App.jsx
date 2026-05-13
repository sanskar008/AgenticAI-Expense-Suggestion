import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation, Navigate } from 'react-router-dom'
import Dashboard from './components/Dashboard'
import Expenses from './components/Expenses'
import AddExpense from './components/AddExpense'
import Analysis from './components/Analysis'
import Login from './components/Login'
import { FaWallet, FaPlusCircle, FaList, FaChartBar, FaSignOutAlt } from 'react-icons/fa'
import { authService } from './services/api'
import './App.css'

function App() {
  const [user, setUser] = useState(authService.getCurrentUser())

  const handleLogin = (userData) => {
    setUser(userData)
  }

  const handleLogout = () => {
    authService.logout()
    setUser(null)
  }

  return (
    <Router>
      <div className="app">
        {user ? (
          <>
            <Navbar onLogout={handleLogout} />
            <main className="main-content">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/expenses" element={<Expenses />} />
                <Route path="/add" element={<AddExpense />} />
                <Route path="/analysis" element={<Analysis />} />
                <Route path="*" element={<Navigate to="/" />} />
              </Routes>
            </main>
          </>
        ) : (
          <Routes>
            <Route path="/login" element={<Login onLogin={handleLogin} />} />
            <Route path="*" element={<Navigate to="/login" />} />
          </Routes>
        )}
      </div>
    </Router>
  )
}

function Navbar({ onLogout }) {
  const location = useLocation()
  
  const navItems = [
    { path: '/', icon: FaWallet, label: 'Dashboard' },
    { path: '/expenses', icon: FaList, label: 'Expenses' },
    { path: '/add', icon: FaPlusCircle, label: 'Add Expense' },
    { path: '/analysis', icon: FaChartBar, label: 'Analysis' },
  ]

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <FaWallet className="brand-icon" />
        <h1>Expense Manager</h1>
      </div>
      <div className="navbar-links">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-link ${isActive ? 'active' : ''}`}
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </Link>
          )
        })}
        <button onClick={onLogout} className="nav-link logout-btn">
          <FaSignOutAlt size={20} />
          <span>Logout</span>
        </button>
      </div>
    </nav>
  )
}

export default App
