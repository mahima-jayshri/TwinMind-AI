import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Brain, Sparkles, ArrowRight, ShieldCheck, Zap } from 'lucide-react'

export default function Login() {
  const { user, loginDemo } = useAuth()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (user) {
      if (user.is_onboarded) {
        navigate('/dashboard')
      } else {
        navigate('/onboarding')
      }
    }
  }, [user, navigate])

  const handleDemoLogin = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const loggedUser = await loginDemo('demo@twinmind.ai')
      if (loggedUser.is_onboarded) {
        navigate('/dashboard')
      } else {
        navigate('/onboarding')
      }
    } catch (err) {
      console.error('Login error:', err)
      setError('Unable to log in. Please ensure the backend server is running.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 p-4">
      <div className="max-w-md w-full mx-auto">
        {/* Logo & Header */}
        <div className="text-center mb-8 animate-fade-in">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-tr from-primary-600 to-indigo-500 rounded-3xl shadow-lg shadow-primary-500/20 mb-4 transform hover:scale-105 transition-transform">
            <Brain className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl font-extrabold text-white tracking-tight mb-2">
            TwinMind <span className="text-transparent bg-clip-text bg-gradient-to-r from-sky-400 to-indigo-400">AI</span>
          </h1>
          <p className="text-gray-400 text-sm">Your Digital Twin, Evolved & Intelligent</p>
        </div>

        {/* Card */}
        <div className="bg-slate-900/80 backdrop-blur-xl border border-slate-800 rounded-2xl p-8 shadow-2xl animate-slide-up">
          <div className="flex items-center gap-2 mb-6">
            <Sparkles className="w-5 h-5 text-sky-400" />
            <h2 className="text-xl font-bold text-white">Experience Your Digital Twin</h2>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm">
              {error}
            </div>
          )}

          {/* Quick Demo Login Button */}
          <button
            onClick={handleDemoLogin}
            disabled={loading}
            className="w-full flex items-center justify-center gap-3 bg-gradient-to-r from-primary-600 to-indigo-600 hover:from-primary-500 hover:to-indigo-500 text-white font-semibold py-3.5 px-4 rounded-xl shadow-lg shadow-primary-600/30 transition-all transform active:scale-95 disabled:opacity-50 cursor-pointer mb-4"
          >
            {loading ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <>
                <Zap className="w-5 h-5 text-yellow-300" />
                <span>Launch Interactive Demo</span>
                <ArrowRight className="w-4 h-4 ml-auto" />
              </>
            )}
          </button>

          {/* Google SSO Button */}
          <button
            onClick={handleDemoLogin}
            disabled={loading}
            className="w-full flex items-center justify-center gap-3 bg-slate-800/80 hover:bg-slate-800 border border-slate-700 text-gray-200 font-medium py-3 px-4 rounded-xl transition-all mb-6 cursor-pointer"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            <span>Continue with Google</span>
          </button>

          <div className="flex items-center gap-2 justify-center text-xs text-slate-400">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Secure & private digital twin environment</span>
          </div>
        </div>

        {/* Footer features */}
        <div className="mt-8 grid grid-cols-3 gap-2 text-center text-xs text-gray-500">
          <div className="p-2 rounded-lg bg-slate-900/40 border border-slate-800/50">
            <span className="font-semibold text-gray-300">5 AI Modes</span>
            <p className="mt-0.5 text-gray-400">Mentor to Roast</p>
          </div>
          <div className="p-2 rounded-lg bg-slate-900/40 border border-slate-800/50">
            <span className="font-semibold text-gray-300">Digital DNA</span>
            <p className="mt-0.5 text-gray-400">Adaptive Memory</p>
          </div>
          <div className="p-2 rounded-lg bg-slate-900/40 border border-slate-800/50">
            <span className="font-semibold text-gray-300">Predictor</span>
            <p className="mt-0.5 text-gray-400">Productivity AI</p>
          </div>
        </div>
      </div>
    </div>
  )
}

