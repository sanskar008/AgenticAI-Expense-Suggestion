import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import Dashboard from './components/Dashboard'
import Expenses from './components/Expenses'
import AddExpense from './components/AddExpense'
import Analysis from './components/Analysis'
import { FaWallet, FaPlusCircle, FaList, FaChartBar } from 'react-icons/fa'
import './App.css'

function App() {
  return (
    <Router>
      <div className="app">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/expenses" element={<Expenses />} />
            <Route path="/add" element={<AddExpense />} />
            <Route path="/analysis" element={<Analysis />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

function Navbar() {
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
      </div>
    </nav>
  )
}

export default App
