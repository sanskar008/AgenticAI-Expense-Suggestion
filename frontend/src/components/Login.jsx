import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authService } from '../services/api'
import { FaPhone, FaLock, FaWallet } from 'react-icons/fa'
import './Login.css'

function Login({ onLogin }) {
  const [phoneNumber, setPhoneNumber] = useState('')
  const [otp, setOtp] = useState('')
  const [step, setStep] = useState(1) // 1: Phone, 2: OTP
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSendOtp = async (e) => {
    e.preventDefault()
    if (!phoneNumber) return
    
    setLoading(true)
    setError('')
    try {
      await authService.sendOtp(phoneNumber)
      setStep(2)
    } catch (err) {
      setError('Failed to send OTP. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleVerifyOtp = async (e) => {
    e.preventDefault()
    if (!otp) return

    setLoading(true)
    setError('')
    try {
      const data = await authService.verifyOtp(phoneNumber, otp)
      if (data.success) {
        onLogin(data.user)
        navigate('/')
      } else {
        setError(data.error || 'Invalid OTP')
      }
    } catch (err) {
      setError('Verification failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <div className="logo-container">
            <FaWallet className="login-logo" />
          </div>
          <h2>Expense Manager</h2>
          <p>{step === 1 ? 'Enter your phone number to continue' : 'Enter the OTP sent to your phone'}</p>
        </div>

        {error && <div className="error-message">{error}</div>}

        {step === 1 ? (
          <form onSubmit={handleSendOtp} className="login-form">
            <div className="input-group">
              <FaPhone className="input-icon" />
              <input
                type="tel"
                placeholder="Phone Number"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                required
              />
            </div>
            <button type="submit" disabled={loading} className="login-button">
              {loading ? 'Sending...' : 'Send OTP'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleVerifyOtp} className="login-form">
            <div className="input-group">
              <FaLock className="input-icon" />
              <input
                type="text"
                placeholder="Enter OTP (123456)"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                required
              />
            </div>
            <button type="submit" disabled={loading} className="login-button">
              {loading ? 'Verifying...' : 'Verify & Login'}
            </button>
            <button 
              type="button" 
              className="back-button"
              onClick={() => setStep(1)}
            >
              Back to Phone
            </button>
          </form>
        )}
        
        <div className="login-footer">
          <p>Demo OTP: <strong>123456</strong></p>
        </div>
      </div>
    </div>
  )
}

export default Login
