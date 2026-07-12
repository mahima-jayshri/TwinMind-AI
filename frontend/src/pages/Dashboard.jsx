import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import { 
  Brain, Target, TrendingUp, Clock, MessageSquare, 
  Settings, LogOut, BarChart3, Zap, Calendar, Plus, Trash, X, Save, AlertCircle, RefreshCw, Sparkles
} from 'lucide-react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Bar, Legend, ComposedChart, Line } from 'recharts'


export default function Dashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)

  // Goals Modal State
  const [isGoalsModalOpen, setIsGoalsModalOpen] = useState(false)
  const [goalsList, setGoalsList] = useState([])
  const [newGoalTitle, setNewGoalTitle] = useState('')
  const [newGoalType, setNewGoalType] = useState('short_term')
  const [newGoalPriority, setNewGoalPriority] = useState('medium')

  // Habits Modal State
  const [isHabitsModalOpen, setIsHabitsModalOpen] = useState(false)
  const [habitsList, setHabitsList] = useState([])
  const [newHabitName, setNewHabitName] = useState('')
  const [newHabitFrequency, setNewHabitFrequency] = useState('daily')
  const [newHabitTarget, setNewHabitTarget] = useState(1)

  // Success Predictor State
  const [predictTask, setPredictTask] = useState('')
  const [predictLoading, setPredictLoading] = useState(false)
  const [predictionResult, setPredictionResult] = useState(null)

  // Productivity Modal State
  const [isProductivityModalOpen, setIsProductivityModalOpen] = useState(false)
  const [prodTasksCompleted, setProdTasksCompleted] = useState('')
  const [prodTasksPlanned, setProdTasksPlanned] = useState('')
  const [prodFocusHours, setProdFocusHours] = useState('')
  const [prodDistractions, setProdDistractions] = useState('')
  const [prodMood, setProdMood] = useState('focused')
  const [prodEnergyLevel, setProdEnergyLevel] = useState(7)
  const [prodLogging, setProdLogging] = useState(false)

  const fetchGoals = async () => {
    try {
      const response = await api.get('/goals')
      setGoalsList(response.data)
    } catch (error) {
      console.error('Failed to fetch goals:', error)
    }
  }

  const handlePredictSuccess = async (e) => {
    e.preventDefault()
    if (!predictTask.trim()) return
    setPredictLoading(true)
    setPredictionResult(null)
    try {
      const response = await api.post('/predictions/predict', {
        prediction_type: 'task_completion',
        task_description: predictTask
      })
      setPredictionResult(response.data)
    } catch (error) {
      console.error('Failed to get prediction:', error)
      setPredictionResult({
        error: 'Prediction currently unavailable. Please make sure the backend is active.'
      })
    } finally {
      setPredictLoading(false)
    }
  }

  const fetchHabits = async () => {
    try {
      const response = await api.get('/habits')
      setHabitsList(response.data)
    } catch (error) {
      console.error('Failed to fetch habits:', error)
    }
  }

  const handleAddGoal = async () => {
    if (!newGoalTitle.trim()) return
    try {
      await api.post('/goals', {
        title: newGoalTitle,
        goal_type: newGoalType,
        priority: newGoalPriority,
      })
      setNewGoalTitle('')
      fetchGoals()
    } catch (error) {
      console.error('Failed to create goal:', error)
    }
  }

  const handleGoalListChange = (id, field, value) => {
    setGoalsList(prev => prev.map(g => {
      if (g.id === id) {
        let updated = { ...g, [field]: value }
        if (field === 'status' && value === 'completed') {
          updated.progress = 100
        }
        return updated
      }
      return g
    }))
  }

  const handleUpdateGoal = async (goal) => {
    try {
      await api.put(`/goals/${goal.id}`, {
        title: goal.title,
        progress: parseFloat(goal.progress),
        status: goal.status,
        priority: goal.priority
      })
      fetchGoals()
    } catch (error) {
      console.error('Failed to update goal:', error)
    }
  }

  const handleDeleteGoal = async (id) => {
    try {
      await api.delete(`/goals/${id}`)
      fetchGoals()
    } catch (error) {
      console.error('Failed to delete goal:', error)
    }
  }

  const handleAddHabit = async () => {
    if (!newHabitName.trim()) return
    try {
      await api.post('/habits', {
        name: newHabitName,
        frequency: newHabitFrequency,
        target_count: newHabitTarget,
      })
      setNewHabitName('')
      fetchHabits()
    } catch (error) {
      console.error('Failed to create habit:', error)
    }
  }

  const handleLogHabit = async (id) => {
    try {
      await api.post(`/habits/${id}/log`, {})
      fetchHabits()
    } catch (error) {
      console.error('Failed to log habit:', error)
    }
  }

  const handleDeleteHabit = async (id) => {
    try {
      await api.delete(`/habits/${id}`)
      fetchHabits()
    } catch (error) {
      console.error('Failed to delete habit:', error)
    }
  }

  const handleLogProductivity = async (e) => {
    e.preventDefault()
    setProdLogging(true)
    try {
      await api.post('/predictions/productivity', {
        tasks_completed: parseInt(prodTasksCompleted) || 0,
        tasks_planned: parseInt(prodTasksPlanned) || 0,
        focus_hours: parseFloat(prodFocusHours) || 0.0,
        distraction_count: parseInt(prodDistractions) || 0,
        mood: prodMood,
        energy_level: parseInt(prodEnergyLevel) || 7
      })
      setIsProductivityModalOpen(false)
      setProdTasksCompleted('')
      setProdTasksPlanned('')
      setProdFocusHours('')
      setProdDistractions('')
      setProdMood('focused')
      setProdEnergyLevel(7)
      loadDashboard()
    } catch (error) {
      console.error('Failed to log productivity:', error)
    } finally {
      setProdLogging(false)
    }
  }


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

          <div className="card flex flex-col justify-between">
            <div className="flex items-center justify-between mb-4">
              <Clock className="w-8 h-8 text-purple-500" />
              <span className="text-2xl font-bold text-white">
                {dashboardData?.productivity?.avg_focus_hours || 0}h
              </span>
            </div>
            <div className="flex items-center justify-between">
              <p className="text-gray-400 text-sm">Avg Focus Time</p>
              <button
                onClick={() => setIsProductivityModalOpen(true)}
                className="text-xs text-primary-400 hover:text-primary-300 font-medium transition-colors cursor-pointer"
              >
                Log Stats
              </button>
            </div>
          </div>
        </div>

        {/* Confidence Scores & Future Predictor Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Confidence Score Panel */}
          <div className="card flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-white">AI Confidence Scores</h2>
                <Brain className="w-5 h-5 text-primary-600" />
              </div>
              <p className="text-gray-400 text-xs mb-6">
                Predictive insights calculated from your habits, focus logs, and Digital DNA context.
              </p>
              
              <div className="space-y-6">
                {/* Procrastination Risk */}
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-300 font-medium">Procrastination Risk</span>
                    <span className={`font-semibold ${
                      (dashboardData?.predictions?.procrastination?.confidence_score || 0) > 60 ? 'text-red-400' :
                      (dashboardData?.predictions?.procrastination?.confidence_score || 0) > 35 ? 'text-yellow-400' : 'text-green-400'
                    }`}>
                      {dashboardData?.predictions?.procrastination?.confidence_score || 0}%
                    </span>
                  </div>
                  <div className="w-full bg-dark-border h-2 rounded-full overflow-hidden">
                    <div 
                      className={`h-full rounded-full transition-all ${
                        (dashboardData?.predictions?.procrastination?.confidence_score || 0) > 60 ? 'bg-red-500' :
                        (dashboardData?.predictions?.procrastination?.confidence_score || 0) > 35 ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${dashboardData?.predictions?.procrastination?.confidence_score || 0}%` }}
                    />
                  </div>
                </div>

                {/* Productivity momentum */}
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-300 font-medium">Productivity Momentum</span>
                    <span className="text-primary-400 font-semibold">
                      {dashboardData?.predictions?.productivity?.confidence_score || 0}%
                    </span>
                  </div>
                  <div className="w-full bg-dark-border h-2 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-primary-600 rounded-full transition-all"
                      style={{ width: `${dashboardData?.predictions?.productivity?.confidence_score || 0}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
            
            <div className="mt-6 pt-4 border-t border-dark-border/40 text-xs text-gray-500">
              Updated based on {dashboardData?.productivity?.weekly_tasks_completed || 0} tasks logged this week.
            </div>
          </div>

          {/* Interactive Future Success Predictor */}
          <div className="lg:col-span-2 card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-white">Predict Success of Today's Task</h2>
              <Sparkles className="w-5 h-5 text-primary-600" />
            </div>
            
            <form onSubmit={handlePredictSuccess} className="space-y-4">
              <div>
                <label className="block text-gray-400 text-sm mb-2">What task do you plan to work on today?</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={predictTask}
                    onChange={(e) => setPredictTask(e.target.value)}
                    placeholder="e.g. Write backend API unit tests, Finish React dashboard widgets"
                    className="input-field flex-1 py-2 px-3 bg-dark-bg text-white border-dark-border rounded-lg"
                    required
                  />
                  <button
                    type="submit"
                    disabled={predictLoading}
                    className="btn-primary py-2 px-4 flex items-center gap-1.5 whitespace-nowrap"
                  >
                    {predictLoading ? (
                      <RefreshCw className="w-4 h-4 animate-spin" />
                    ) : (
                      'Predict success'
                    )}
                  </button>
                </div>
              </div>
            </form>

            {predictionResult && (
              <div className="mt-4 p-4 rounded-xl bg-dark-bg/60 border border-dark-border/80 animate-fade-in space-y-3">
                {predictionResult.error ? (
                  <div className="flex items-center gap-2 text-red-400 text-sm">
                    <AlertCircle className="w-4 h-4" />
                    <p>{predictionResult.error}</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="flex flex-col items-center justify-center border-r border-dark-border/40 pr-2">
                      <span className="text-xs text-gray-400 uppercase font-medium">Likelihood</span>
                      <span className={`text-3xl font-extrabold mt-1 ${
                        predictionResult.confidence_score >= 75 ? 'text-green-400' :
                        predictionResult.confidence_score >= 50 ? 'text-yellow-400' : 'text-red-400'
                      }`}>
                        {predictionResult.confidence_score}%
                      </span>
                    </div>
                    <div className="md:col-span-3 text-sm space-y-2">
                      <p className="text-gray-300 italic">"{predictionResult.analysis}"</p>
                      {predictionResult.factors && predictionResult.factors.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 mt-2">
                          {predictionResult.factors.map((factor, idx) => (
                            <span key={idx} className="text-xs px-2 py-0.5 bg-primary-600/10 text-primary-400 border border-primary-600/25 rounded-full">
                              • {factor}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
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
              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    fetchGoals()
                    setIsGoalsModalOpen(true)
                  }}
                  className="btn-secondary py-1 px-3 text-xs flex items-center gap-1 border-primary-600/30 hover:border-primary-600/50"
                >
                  Manage
                </button>
                <Target className="w-5 h-5 text-primary-600" />
              </div>
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
              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    fetchHabits()
                    setIsHabitsModalOpen(true)
                  }}
                  className="btn-secondary py-1 px-3 text-xs flex items-center gap-1 border-primary-600/30 hover:border-primary-600/50"
                >
                  Manage
                </button>
                <Zap className="w-5 h-5 text-primary-600" />
              </div>
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
        {user?.show_memory_timeline && (
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
        )}
      </main>

      {/* Goals Modal */}
      {isGoalsModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fade-in">
          <div className="bg-dark-card border border-dark-border rounded-2xl w-full max-w-2xl max-h-[85vh] overflow-hidden flex flex-col shadow-2xl">
            {/* Modal Header */}
            <div className="p-6 border-b border-dark-border flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Target className="w-5 h-5 text-primary-600" />
                <h3 className="text-lg font-semibold text-white">Manage Goals</h3>
              </div>
              <button
                onClick={() => {
                  setIsGoalsModalOpen(false)
                  loadDashboard()
                }}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto flex-1 space-y-6">
              {/* Add New Goal Form */}
              <div className="bg-dark-bg/50 border border-dark-border/60 rounded-xl p-4 space-y-4">
                <h4 className="text-sm font-semibold text-primary-400">Add New Goal</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <input
                    type="text"
                    placeholder="Goal Title"
                    value={newGoalTitle}
                    onChange={(e) => setNewGoalTitle(e.target.value)}
                    className="input-field py-2 text-sm bg-dark-bg border-dark-border/80"
                  />
                  <select
                    value={newGoalType}
                    onChange={(e) => setNewGoalType(e.target.value)}
                    className="input-field py-2 text-sm bg-dark-bg border-dark-border/80"
                  >
                    <option value="short_term">Short Term (3 mo)</option>
                    <option value="long_term">Long Term (5 yr)</option>
                  </select>
                </div>
                <div className="flex items-center gap-3">
                  <select
                    value={newGoalPriority}
                    onChange={(e) => setNewGoalPriority(e.target.value)}
                    className="input-field py-2 text-sm bg-dark-bg border-dark-border/80 max-w-[180px]"
                  >
                    <option value="low">Low Priority</option>
                    <option value="medium">Medium Priority</option>
                    <option value="high">High Priority</option>
                  </select>
                  <button
                    onClick={handleAddGoal}
                    className="btn-primary py-2 px-4 text-sm flex items-center gap-1 ml-auto"
                  >
                    <Plus className="w-4 h-4" />
                    Add Goal
                  </button>
                </div>
              </div>

              {/* Goal List */}
              <div className="space-y-4">
                <h4 className="text-sm font-semibold text-gray-400">Your Goals ({goalsList.length})</h4>
                {goalsList.map((g) => (
                  <div key={g.id} className="bg-dark-bg/40 border border-dark-border rounded-xl p-4 space-y-3">
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <input
                          type="text"
                          value={g.title}
                          onChange={(e) => handleGoalListChange(g.id, 'title', e.target.value)}
                          className="bg-transparent border-b border-transparent focus:border-primary-600/50 text-white font-medium focus:outline-none text-sm w-full py-0.5"
                        />
                        <div className="flex flex-wrap gap-2 text-xs">
                          <span className="text-gray-400 capitalize">{g.goal_type.replace('_', ' ')}</span>
                          <span className="text-gray-500">•</span>
                          <span className={`capitalize ${
                            g.priority === 'high' ? 'text-red-400' :
                            g.priority === 'medium' ? 'text-yellow-400' : 'text-blue-400'
                          }`}>{g.priority} Priority</span>
                        </div>
                      </div>
                      <button
                        onClick={() => handleDeleteGoal(g.id)}
                        className="text-gray-500 hover:text-red-400 p-1.5 rounded-lg hover:bg-dark-border transition-all"
                      >
                        <Trash className="w-4 h-4" />
                      </button>
                    </div>

                    <div className="flex items-center gap-4">
                      {/* Progress slider */}
                      <div className="flex-1 flex items-center gap-2">
                        <input
                          type="range"
                          min="0"
                          max="100"
                          value={g.progress}
                          onChange={(e) => handleGoalListChange(g.id, 'progress', parseInt(e.target.value))}
                          className="flex-1 accent-primary-600 bg-dark-border h-1.5 rounded-lg appearance-none cursor-pointer"
                        />
                        <span className="text-xs text-gray-300 min-w-[32px] text-right">{g.progress}%</span>
                      </div>

                      {/* Status select */}
                      <select
                        value={g.status}
                        onChange={(e) => handleGoalListChange(g.id, 'status', e.target.value)}
                        className="input-field py-1 px-2 text-xs bg-dark-bg border-dark-border/80 max-w-[120px]"
                      >
                        <option value="active">Active</option>
                        <option value="completed">Completed</option>
                        <option value="paused">Paused</option>
                      </select>

                      <button
                        onClick={() => handleUpdateGoal(g)}
                        className="btn-secondary py-1 px-3 text-xs flex items-center gap-1"
                      >
                        <Save className="w-3.5 h-3.5" />
                        Save
                      </button>
                    </div>
                  </div>
                ))}
                {goalsList.length === 0 && (
                  <p className="text-gray-500 text-center py-6 text-sm">No goals found. Create one above!</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Habits Modal */}
      {isHabitsModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fade-in">
          <div className="bg-dark-card border border-dark-border rounded-2xl w-full max-w-2xl max-h-[85vh] overflow-hidden flex flex-col shadow-2xl">
            {/* Modal Header */}
            <div className="p-6 border-b border-dark-border flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Zap className="w-5 h-5 text-primary-600" />
                <h3 className="text-lg font-semibold text-white">Manage Habits</h3>
              </div>
              <button
                onClick={() => {
                  setIsHabitsModalOpen(false)
                  loadDashboard()
                }}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto flex-1 space-y-6">
              {/* Add New Habit Form */}
              <div className="bg-dark-bg/50 border border-dark-border/60 rounded-xl p-4 space-y-4">
                <h4 className="text-sm font-semibold text-primary-400">Add New Habit</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <input
                    type="text"
                    placeholder="Habit Name"
                    value={newHabitName}
                    onChange={(e) => setNewHabitName(e.target.value)}
                    className="input-field py-2 text-sm bg-dark-bg border-dark-border/80 col-span-1 md:col-span-2"
                  />
                  <select
                    value={newHabitFrequency}
                    onChange={(e) => setNewHabitFrequency(e.target.value)}
                    className="input-field py-2 text-sm bg-dark-bg border-dark-border/80"
                  >
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                  </select>
                </div>
                <div className="flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2 text-sm text-gray-300">
                    <span>Target:</span>
                    <input
                      type="number"
                      min="1"
                      value={newHabitTarget}
                      onChange={(e) => setNewHabitTarget(parseInt(e.target.value) || 1)}
                      className="input-field py-1 px-2 text-sm bg-dark-bg border-dark-border/80 w-16 text-center"
                    />
                    <span>times</span>
                  </div>
                  <button
                    onClick={handleAddHabit}
                    className="btn-primary py-2 px-4 text-sm flex items-center gap-1"
                  >
                    <Plus className="w-4 h-4" />
                    Add Habit
                  </button>
                </div>
              </div>

              {/* Habit List */}
              <div className="space-y-4">
                <h4 className="text-sm font-semibold text-gray-400">Your Habits ({habitsList.length})</h4>
                {habitsList.map((h) => (
                  <div key={h.id} className="bg-dark-bg/40 border border-dark-border rounded-xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="space-y-1">
                      <p className="text-white font-medium text-sm">{h.name}</p>
                      <div className="flex items-center gap-3 text-xs text-gray-400">
                        <span className="capitalize">{h.frequency}</span>
                        <span>•</span>
                        <span className="text-yellow-500">🔥 Current Streak: {h.current_streak}</span>
                        <span>•</span>
                        <span className="text-gray-500">🏆 Best Streak: {h.best_streak}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 ml-auto md:ml-0">
                      <button
                        onClick={() => handleLogHabit(h.id)}
                        className="btn-primary py-1.5 px-3 text-xs flex items-center gap-1 bg-green-600 hover:bg-green-700"
                      >
                        ⚡ Log
                      </button>
                      <button
                        onClick={() => handleDeleteHabit(h.id)}
                        className="text-gray-500 hover:text-red-400 p-1.5 rounded-lg hover:bg-dark-border transition-all"
                      >
                        <Trash className="w-4.5 h-4.5" />
                      </button>
                    </div>
                  </div>
                ))}
                {habitsList.length === 0 && (
                  <p className="text-gray-500 text-center py-6 text-sm">No habits found. Create one above!</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Productivity Modal */}
      {isProductivityModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fade-in">
          <div className="bg-dark-card border border-dark-border rounded-2xl w-full max-w-lg max-h-[85vh] overflow-hidden flex flex-col shadow-2xl">
            {/* Modal Header */}
            <div className="p-6 border-b border-dark-border flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Clock className="w-5 h-5 text-primary-600" />
                <h3 className="text-lg font-semibold text-white">Log Today's Productivity</h3>
              </div>
              <button
                onClick={() => setIsProductivityModalOpen(false)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body */}
            <form onSubmit={handleLogProductivity} className="p-6 overflow-y-auto flex-1 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-gray-400 text-xs mb-1 font-medium">Tasks Completed</label>
                  <input
                    type="number"
                    min="0"
                    placeholder="e.g. 4"
                    value={prodTasksCompleted}
                    onChange={(e) => setProdTasksCompleted(e.target.value)}
                    className="input-field py-2 text-sm bg-dark-bg border-dark-border/80 w-full text-white"
                    required
                  />
                </div>
                <div>
                  <label className="block text-gray-400 text-xs mb-1 font-medium">Tasks Planned</label>
                  <input
                    type="number"
                    min="0"
                    placeholder="e.g. 6"
                    value={prodTasksPlanned}
                    onChange={(e) => setProdTasksPlanned(e.target.value)}
                    className="input-field py-2 text-sm bg-dark-bg border-dark-border/80 w-full text-white"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-gray-400 text-xs mb-1 font-medium">Focus Hours</label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    placeholder="e.g. 5.5"
                    value={prodFocusHours}
                    onChange={(e) => setProdFocusHours(e.target.value)}
                    className="input-field py-2 text-sm bg-dark-bg border-dark-border/80 w-full text-white"
                    required
                  />
                </div>
                <div>
                  <label className="block text-gray-400 text-xs mb-1 font-medium">Distractions Count</label>
                  <input
                    type="number"
                    min="0"
                    placeholder="e.g. 2"
                    value={prodDistractions}
                    onChange={(e) => setProdDistractions(e.target.value)}
                    className="input-field py-2 text-sm bg-dark-bg border-dark-border/80 w-full text-white"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-gray-400 text-xs mb-1 font-medium">Mood</label>
                <select
                  value={prodMood}
                  onChange={(e) => setProdMood(e.target.value)}
                  className="input-field py-2 text-sm bg-dark-bg border-dark-border/80 w-full text-white"
                >
                  <option value="focused">Focused 🎯</option>
                  <option value="energetic">Energetic ⚡</option>
                  <option value="calm">Calm 🌊</option>
                  <option value="tired">Tired 🥱</option>
                  <option value="stressed">Stressed 😰</option>
                </select>
              </div>

              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="block text-gray-400 text-xs font-medium">Energy Level</label>
                  <span className="text-xs font-semibold text-primary-400">{prodEnergyLevel}/10</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={prodEnergyLevel}
                  onChange={(e) => setProdEnergyLevel(parseInt(e.target.value))}
                  className="w-full accent-primary-600 bg-dark-border h-1.5 rounded-lg appearance-none cursor-pointer"
                />
              </div>

              <div className="pt-4 border-t border-dark-border/40 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setIsProductivityModalOpen(false)}
                  className="btn-secondary py-2 px-4 text-sm text-gray-300 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={prodLogging}
                  className="btn-primary py-2 px-4 text-sm flex items-center gap-1.5 text-white"
                >
                  {prodLogging && <RefreshCw className="w-4 h-4 animate-spin" />}
                  Save Metrics
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

