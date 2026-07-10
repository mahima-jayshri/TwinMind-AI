import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Brain } from 'lucide-react'

export default function Login() {
  const { login, user } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    console.log('Login page - user state changed:', user)
    if (user) {
      console.log('User logged in, is_onboarded:', user.is_onboarded)
      if (user.is_onboarded) {
        console.log('Navigating to dashboard')
        navigate('/dashboard')
      } else {
        console.log('Navigating to onboarding')
        navigate('/onboarding')
      }
    }
  }, [user, navigate])

  const handleGoogleLogin = async () => {
    try {
      console.log('Attempting login...')
      // For demo purposes, simulate Google login
      // In production, use actual Google OAuth
      const mockToken = 'mock_google_token'
      const user = await login(mockToken)
      console.log('Login successful:', user)
      
      // Manual navigation fallback
      if (user && !user.is_onboarded) {
        console.log('Manual navigation to onboarding')
        setTimeout(() => navigate('/onboarding'), 100)
      } else if (user && user.is_onboarded) {
        console.log('Manual navigation to dashboard')
        setTimeout(() => navigate('/dashboard'), 100)
      }
    } catch (error) {
      console.error('Login failed:', error)
      alert('Login failed: ' + (error.response?.data?.detail || error.message))
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-dark-bg via-slate-900 to-dark-bg">
      <div className="max-w-md w-full mx-4">
        <div className="text-center mb-8 animate-fade-in">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-primary-600 rounded-2xl mb-4">
            <Brain className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-2">TwinMind AI</h1>
          <p className="text-gray-400">Your Digital Twin, Evolved</p>
        </div>

        <div className="card animate-slide-up">
          <h2 className="text-2xl font-semibold text-white mb-6 text-center">
            Welcome Back
          </h2>

          <button
            onClick={handleGoogleLogin}
            className="w-full flex items-center justify-center gap-3 bg-primary-600 text-white font-medium py-3 px-4 rounded-lg hover:bg-primary-700 transition-colors mb-4"
          >
            <Brain className="w-5 h-5" />
            Quick Start (Demo Mode)
          </button>

          <button
            onClick={handleGoogleLogin}
            className="w-full flex items-center justify-center gap-3 bg-white text-gray-900 font-medium py-3 px-4 rounded-lg hover:bg-gray-100 transition-colors mb-4"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path
                fill="currentColor"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="currentColor"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="currentColor"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="currentColor"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            Continue with Google
          </button>

          <p className="text-center text-gray-400 text-sm">
            By continuing, you agree to our Terms of Service and Privacy Policy
          </p>
        </div>

        <div className="mt-8 text-center text-gray-500 text-sm">
          <p>An AI that understands YOU</p>
          <p className="mt-1">Not just another chatbot</p>
        </div>
      </div>
    </div>
  )
}
