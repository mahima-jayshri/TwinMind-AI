import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import { 
  User, Settings, Brain, ArrowLeft, Save, 
  Bell, Lock, Palette, Globe
} from 'lucide-react'

export default function Profile() {
  const { user, logout, updateUser } = useAuth()
  const navigate = useNavigate()
  const [settings, setSettings] = useState({
    preferred_mode: user?.preferred_mode || 'mentor',
    preferred_tone: user?.preferred_tone || 'professional',
    preferred_language: user?.preferred_language || 'english',
    show_memory_timeline: localStorage.getItem('show_memory_timeline') === 'true'
  })
  const [memories, setMemories] = useState([])
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    loadMemories()
  }, [])

  useEffect(() => {
    if (user) {
      setSettings((prev) => ({
        ...prev,
        preferred_mode: user.preferred_mode || 'mentor',
        preferred_tone: user.preferred_tone || 'professional',
        preferred_language: user.preferred_language || 'english',
        show_memory_timeline: localStorage.getItem('show_memory_timeline') === 'true'
      }))
    }
  }, [user])

  const loadMemories = async () => {
    try {
      const response = await api.get('/memory/')
      setMemories(response.data)
    } catch (error) {
      console.error('Failed to load memories:', error)
    }
  }

  const handleSaveSettings = async () => {
    setSaving(true)
    try {
      localStorage.setItem('show_memory_timeline', String(settings.show_memory_timeline))
      
      const response = await api.put('/auth/settings', {
        preferred_mode: settings.preferred_mode,
        preferred_tone: settings.preferred_tone,
        preferred_language: settings.preferred_language
      })
      
      updateUser({
        ...response.data,
        show_memory_timeline: settings.show_memory_timeline
      })
      setTimeout(() => setSaving(false), 500)
    } catch (error) {
      console.error('Failed to save settings:', error)
      setSaving(false)
    }
  }

  const handleDeleteMemory = async (memoryId) => {
    try {
      await api.delete(`/memory/${memoryId}`)
      setMemories(memories.filter(m => m.id !== memoryId))
    } catch (error) {
      console.error('Failed to delete memory:', error)
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-dark-bg">
      {/* Header */}
      <header className="border-b border-dark-border bg-dark-card/50 backdrop-blur-sm">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button
                onClick={() => navigate('/dashboard')}
                className="p-2 rounded-lg hover:bg-dark-border transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-gray-400" />
              </button>
              <h1 className="text-xl font-semibold text-white">Profile & Settings</h1>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Profile Card */}
        <div className="card mb-6">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-20 h-20 bg-primary-600 rounded-2xl flex items-center justify-center">
              <User className="w-10 h-10 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">{user?.name}</h2>
              <p className="text-gray-400">{user?.email}</p>
              <div className="flex items-center gap-2 mt-2">
                <span className="px-2 py-1 bg-primary-600/20 text-primary-400 text-xs rounded-full">
                  {user?.is_onboarded ? 'Onboarded' : 'Not Onboarded'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Settings */}
        <div className="card mb-6">
          <div className="flex items-center gap-3 mb-6">
            <Settings className="w-6 h-6 text-primary-600" />
            <h2 className="text-xl font-semibold text-white">Agent Settings</h2>
          </div>

          <div className="space-y-6">
            <div>
              <label className="block text-gray-400 text-sm mb-2">Preferred Mode</label>
              <select
                value={settings.preferred_mode}
                onChange={(e) => setSettings({ ...settings, preferred_mode: e.target.value })}
                className="input-field w-full"
              >
                <option value="mentor">Mentor</option>
                <option value="best_friend">Best Friend</option>
                <option value="roast">Roast</option>
                <option value="future_me">Future Me</option>
                <option value="interviewer">Interviewer</option>
              </select>
            </div>

            <div>
              <label className="block text-gray-400 text-sm mb-2">Preferred Tone</label>
              <select
                value={settings.preferred_tone}
                onChange={(e) => setSettings({ ...settings, preferred_tone: e.target.value })}
                className="input-field w-full"
              >
                <option value="professional">Professional</option>
                <option value="casual">Casual</option>
                <option value="direct">Direct</option>
                <option value="empathetic">Empathetic</option>
              </select>
            </div>

            <div>
              <label className="block text-gray-400 text-sm mb-2">Preferred Language</label>
              <select
                value={settings.preferred_language}
                onChange={(e) => setSettings({ ...settings, preferred_language: e.target.value })}
                className="input-field w-full"
              >
                <option value="english">English</option>
                <option value="spanish">Spanish</option>
                <option value="french">French</option>
                <option value="german">German</option>
              </select>
            </div>

            <div className="flex items-center gap-3 py-2">
              <input
                type="checkbox"
                id="show_memory_timeline"
                checked={settings.show_memory_timeline}
                onChange={(e) => setSettings({ ...settings, show_memory_timeline: e.target.checked })}
                className="w-4 h-4 rounded border-dark-border bg-dark-bg text-primary-600 focus:ring-primary-500 focus:ring-offset-dark-bg cursor-pointer"
              />
              <label htmlFor="show_memory_timeline" className="text-gray-300 text-sm font-medium cursor-pointer select-none">
                Show Memory Timeline on Dashboard
              </label>
            </div>

            <button
              onClick={handleSaveSettings}
              disabled={saving}
              className="btn-primary flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              {saving ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </div>

        {/* Memory Management */}
        <div className="card mb-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <Brain className="w-6 h-6 text-primary-600" />
              <h2 className="text-xl font-semibold text-white">Memory Timeline</h2>
            </div>
            <span className="text-gray-400 text-sm">{memories.length} memories</span>
          </div>

          <div className="space-y-3 max-h-96 overflow-y-auto">
            {memories.map((memory) => (
              <div key={memory.id} className="bg-dark-bg rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-1 bg-primary-600/20 text-primary-400 text-xs rounded-full uppercase">
                      {memory.type}
                    </span>
                    <span className="text-gray-500 text-xs">
                      {new Date(memory.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <button
                    onClick={() => handleDeleteMemory(memory.id)}
                    className="text-red-400 hover:text-red-300 text-sm"
                  >
                    Delete
                  </button>
                </div>
                <p className="text-white text-sm">{memory.content}</p>
                <div className="mt-2 flex items-center gap-2">
                  <span className="text-xs text-gray-500">Importance:</span>
                  <div className="flex gap-1">
                    {[...Array(10)].map((_, i) => (
                      <div
                        key={i}
                        className={`w-2 h-2 rounded-full ${
                          i < memory.importance ? 'bg-primary-600' : 'bg-dark-border'
                        }`}
                      />
                    ))}
                  </div>
                </div>
              </div>
            ))}
            
            {memories.length === 0 && (
              <p className="text-gray-400 text-center py-8">No memories stored yet</p>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="card">
          <div className="flex items-center gap-3 mb-6">
            <Settings className="w-6 h-6 text-primary-600" />
            <h2 className="text-xl font-semibold text-white">Quick Actions</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button className="flex items-center gap-3 p-4 bg-dark-bg rounded-lg hover:bg-dark-border transition-colors">
              <Bell className="w-5 h-5 text-primary-600" />
              <div className="text-left">
                <p className="text-white font-medium">Notifications</p>
                <p className="text-gray-400 text-sm">Manage your alerts</p>
              </div>
            </button>

            <button className="flex items-center gap-3 p-4 bg-dark-bg rounded-lg hover:bg-dark-border transition-colors">
              <Lock className="w-5 h-5 text-primary-600" />
              <div className="text-left">
                <p className="text-white font-medium">Privacy</p>
                <p className="text-gray-400 text-sm">Control your data</p>
              </div>
            </button>

            <button className="flex items-center gap-3 p-4 bg-dark-bg rounded-lg hover:bg-dark-border transition-colors">
              <Palette className="w-5 h-5 text-primary-600" />
              <div className="text-left">
                <p className="text-white font-medium">Appearance</p>
                <p className="text-gray-400 text-sm">Customize the look</p>
              </div>
            </button>

            <button className="flex items-center gap-3 p-4 bg-dark-bg rounded-lg hover:bg-dark-border transition-colors">
              <Globe className="w-5 h-5 text-primary-600" />
              <div className="text-left">
                <p className="text-white font-medium">Language</p>
                <p className="text-gray-400 text-sm">Change language</p>
              </div>
            </button>
          </div>

          <button
            onClick={handleLogout}
            className="w-full mt-6 py-3 bg-red-600/20 text-red-400 rounded-lg hover:bg-red-600/30 transition-colors font-medium"
          >
            Sign Out
          </button>
        </div>
      </main>
    </div>
  )
}
