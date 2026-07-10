import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import { 
  Brain, Target, TrendingUp, Clock, MessageSquare, 
  Settings, LogOut, BarChart3, Zap, Calendar
} from 'lucide-react'

export default function Dashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (user && !user.is_onboarded) {
      navigate('/onboarding')
      return
    }
    loadDashboard()
  }, [user, navigate])

  const loadDashboard = async () => {
    try {
      const response = await api.get('/predictions/dashboard')
      setDashboardData(response.data)
    } catch (error) {
      console.error('Failed to load dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-dark-bg">
      {/* Header */}
      <header className="border-b border-dark-border bg-dark-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">TwinMind AI</h1>
                <p className="text-xs text-gray-400">Welcome back, {user?.name}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <button
                onClick={() => navigate('/chat')}
                className="btn-primary flex items-center gap-2"
              >
                <MessageSquare className="w-4 h-4" />
                Chat
              </button>
              <button
                onClick={() => navigate('/profile')}
                className="p-2 rounded-lg hover:bg-dark-border transition-colors"
              >
                <Settings className="w-5 h-5 text-gray-400" />
              </button>
              <button
                onClick={handleLogout}
                className="p-2 rounded-lg hover:bg-dark-border transition-colors"
              >
                <LogOut className="w-5 h-5 text-gray-400" />
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <Target className="w-8 h-8 text-primary-600" />
              <span className="text-2xl font-bold text-white">
                {dashboardData?.goals?.active || 0}
              </span>
            </div>
            <p className="text-gray-400 text-sm">Active Goals</p>
          </div>

          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <TrendingUp className="w-8 h-8 text-green-500" />
              <span className="text-2xl font-bold text-white">
                {dashboardData?.goals?.completed || 0}
              </span>
            </div>
            <p className="text-gray-400 text-sm">Completed Goals</p>
          </div>

          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <Zap className="w-8 h-8 text-yellow-500" />
              <span className="text-2xl font-bold text-white">
                {dashboardData?.habits?.active || 0}
              </span>
            </div>
            <p className="text-gray-400 text-sm">Active Habits</p>
          </div>

          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <Clock className="w-8 h-8 text-purple-500" />
              <span className="text-2xl font-bold text-white">
                {dashboardData?.productivity?.avg_focus_hours || 0}h
              </span>
            </div>
            <p className="text-gray-400 text-sm">Avg Focus Time</p>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Digital DNA */}
          <div className="lg:col-span-2 card">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white">Digital DNA</h2>
              <Brain className="w-5 h-5 text-primary-600" />
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {dashboardData?.digital_dna && Object.entries(dashboardData.digital_dna).map(([key, value]) => (
                <div key={key} className="bg-dark-bg rounded-lg p-4">
                  <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">
                    {key.replace(/_/g, ' ')}
                  </p>
                  <p className="text-white text-sm font-medium truncate">
                    {Array.isArray(value) ? value.join(', ') : String(value)}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Today's Recommendation */}
          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white">Today's Focus</h2>
              <Calendar className="w-5 h-5 text-primary-600" />
            </div>
            
            <div className="space-y-4">
              <div className="bg-gradient-to-r from-primary-600/20 to-primary-600/5 rounded-lg p-4 border border-primary-600/30">
                <p className="text-primary-400 text-sm font-medium mb-2">Priority Task</p>
                <p className="text-white">Continue working on your main goal</p>
              </div>
              
              <div className="bg-dark-bg rounded-lg p-4">
                <p className="text-gray-400 text-sm font-medium mb-2">Productivity Tip</p>
                <p className="text-white text-sm">Based on your patterns, you're most focused in the morning</p>
              </div>
            </div>
          </div>
        </div>

        {/* Goals and Habits */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
          {/* Goals */}
          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white">Current Goals</h2>
              <Target className="w-5 h-5 text-primary-600" />
            </div>
            
            <div className="space-y-4">
              {dashboardData?.goals?.items?.map((goal) => (
                <div key={goal.id} className="bg-dark-bg rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-white font-medium">{goal.title}</p>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      goal.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                      goal.status === 'active' ? 'bg-primary-600/20 text-primary-400' :
                      'bg-gray-500/20 text-gray-400'
                    }`}>
                      {goal.status}
                    </span>
                  </div>
                  <div className="h-2 bg-dark-border rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary-600 transition-all"
                      style={{ width: `${goal.progress}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-gray-400 mt-1">{goal.progress}% complete</p>
                </div>
              ))}
              
              {(!dashboardData?.goals?.items || dashboardData.goals.items.length === 0) && (
                <p className="text-gray-400 text-center py-8">No goals yet. Start chatting to set goals!</p>
              )}
            </div>
          </div>

          {/* Habits */}
          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white">Habit Tracker</h2>
              <Zap className="w-5 h-5 text-primary-600" />
            </div>
            
            <div className="space-y-4">
              {dashboardData?.habits?.items?.map((habit) => (
                <div key={habit.id} className="bg-dark-bg rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-white font-medium">{habit.name}</p>
                    <div className="flex items-center gap-2">
                      <span className="text-yellow-500 text-sm">🔥 {habit.current_streak}</span>
                      <span className="text-gray-500 text-xs">best: {habit.best_streak}</span>
                    </div>
                  </div>
                  <p className="text-xs text-gray-400">Current streak</p>
                </div>
              ))}
              
              {(!dashboardData?.habits?.items || dashboardData.habits.items.length === 0) && (
                <p className="text-gray-400 text-center py-8">No habits tracked yet. Start building habits!</p>
              )}
            </div>
          </div>
        </div>

        {/* Memory Timeline */}
        <div className="card mt-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-white">Memory Timeline</h2>
            <BarChart3 className="w-5 h-5 text-primary-600" />
          </div>
          
          <div className="space-y-4">
            {dashboardData?.memories?.map((memory) => (
              <div key={memory.id} className="flex items-start gap-4 bg-dark-bg rounded-lg p-4">
                <div className="w-2 h-2 bg-primary-600 rounded-full mt-2"></div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-primary-400 uppercase">{memory.type}</span>
                    <span className="text-xs text-gray-500">
                      {new Date(memory.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <p className="text-white text-sm">{memory.content}</p>
                </div>
              </div>
            ))}
            
            {(!dashboardData?.memories || dashboardData.memories.length === 0) && (
              <p className="text-gray-400 text-center py-8">No memories yet. Start chatting to build your digital twin!</p>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
