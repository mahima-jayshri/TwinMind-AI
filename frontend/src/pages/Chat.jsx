import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import { 
  Send, Brain, User, Bot, ArrowLeft, 
  Sparkles, Target, BookOpen, Briefcase
} from 'lucide-react'
import { marked } from 'marked'

const modes = [
  { id: 'mentor', name: 'Mentor', icon: Briefcase, description: 'Professional guidance' },
  { id: 'best_friend', name: 'Best Friend', icon: User, description: 'Casual & supportive' },
  { id: 'roast', name: 'Roast', icon: Sparkles, description: 'Funny but respectful' },
  { id: 'future_me', name: 'Future Me', icon: Target, description: 'Your future self' },
  { id: 'interviewer', name: 'Interviewer', icon: BookOpen, description: 'Practice interviews' }
]

const actions = [
  { id: 'create_study_plan', name: 'Study Plan', icon: BookOpen },
  { id: 'create_weekly_goals', name: 'Weekly Goals', icon: Target },
  { id: 'track_habits', name: 'Track Habits', icon: Brain },
  { id: 'review_resume', name: 'Review Resume', icon: Briefcase },
  { id: 'mock_interview', name: 'Mock Interview', icon: User }
]

export default function Chat() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [selectedMode, setSelectedMode] = useState('mentor')
  const [showModeSelector, setShowModeSelector] = useState(false)
  const [showActions, setShowActions] = useState(false)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    if (user && !user.is_onboarded) {
      navigate('/onboarding')
      return
    }
  }, [user, navigate])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await api.post('/agent/chat', {
        message: input,
        mode: selectedMode,
        conversation_history: messages
      })

      const agentMessage = { role: 'assistant', content: response.data.response }
      setMessages(prev => [...prev, agentMessage])

      if (response.data.needs_evolution) {
        setTimeout(() => {
          setMessages(prev => [...prev, {
            role: 'system',
            content: '🧬 Your Digital DNA is evolving. Let me ask you a few questions to update your profile.'
          }])
        }, 1000)
      }
    } catch (error) {
      console.error('Failed to send message:', error)
      setMessages(prev => [...prev, {
        role: 'system',
        content: 'Sorry, something went wrong. Please try again.'
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleAction = async (actionId) => {
    setShowActions(false)
    setLoading(true)

    try {
      const response = await api.post('/agent/action', {
        action: actionId,
        params: { context: messages }
      })

      const agentMessage = { role: 'assistant', content: response.data.result }
      setMessages(prev => [...prev, agentMessage])
    } catch (error) {
      console.error('Failed to perform action:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const currentMode = modes.find(m => m.id === selectedMode)

  return (
    <div className="min-h-screen bg-dark-bg flex flex-col">
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
              <div className="flex items-center gap-2">
                <Brain className="w-6 h-6 text-primary-600" />
                <div>
                  <h1 className="text-lg font-semibold text-white">TwinMind AI</h1>
                  <p className="text-xs text-gray-400">{currentMode?.name} Mode</p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowActions(!showActions)}
                className="btn-secondary text-sm"
              >
                Actions
              </button>
              <button
                onClick={() => setShowModeSelector(!showModeSelector)}
                className="btn-primary text-sm"
              >
                {currentMode?.name}
              </button>
            </div>
          </div>

          {/* Mode Selector */}
          {showModeSelector && (
            <div className="mt-4 grid grid-cols-2 md:grid-cols-5 gap-2 animate-fade-in">
              {modes.map((mode) => (
                <button
                  key={mode.id}
                  onClick={() => {
                    setSelectedMode(mode.id)
                    setShowModeSelector(false)
                  }}
                  className={`p-3 rounded-lg border-2 text-left transition-all ${
                    selectedMode === mode.id
                      ? 'border-primary-600 bg-primary-600/10'
                      : 'border-dark-border hover:border-primary-600/50'
                  }`}
                >
                  <mode.icon className="w-5 h-5 mb-1 text-primary-400" />
                  <p className="text-white text-sm font-medium">{mode.name}</p>
                  <p className="text-gray-400 text-xs">{mode.description}</p>
                </button>
              ))}
            </div>
          )}

          {/* Actions */}
          {showActions && (
            <div className="mt-4 flex flex-wrap gap-2 animate-fade-in">
              {actions.map((action) => (
                <button
                  key={action.id}
                  onClick={() => handleAction(action.id)}
                  className="flex items-center gap-2 px-3 py-2 bg-dark-card border border-dark-border rounded-lg hover:border-primary-600/50 transition-colors"
                >
                  <action.icon className="w-4 h-4 text-primary-400" />
                  <span className="text-white text-sm">{action.name}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 py-6">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-primary-600/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <Brain className="w-8 h-8 text-primary-600" />
              </div>
              <h2 className="text-2xl font-semibold text-white mb-2">
                Start Your Conversation
              </h2>
              <p className="text-gray-400 mb-6">
                I'm your {currentMode?.name.toLowerCase()}. Ask me anything!
              </p>
              <div className="flex flex-wrap justify-center gap-2">
                <button
                  onClick={() => setInput('What should I focus on today?')}
                  className="px-4 py-2 bg-dark-card border border-dark-border rounded-lg text-gray-300 hover:border-primary-600/50 transition-colors text-sm"
                >
                  What should I focus on today?
                </button>
                <button
                  onClick={() => setInput('Help me create a study plan')}
                  className="px-4 py-2 bg-dark-card border border-dark-border rounded-lg text-gray-300 hover:border-primary-600/50 transition-colors text-sm"
                >
                  Help me create a study plan
                </button>
                <button
                  onClick={() => setInput('Review my progress this week')}
                  className="px-4 py-2 bg-dark-card border border-dark-border rounded-lg text-gray-300 hover:border-primary-600/50 transition-colors text-sm"
                >
                  Review my progress this week
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex gap-3 ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {message.role === 'assistant' && (
                    <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Bot className="w-5 h-5 text-white" />
                    </div>
                  )}
                  
                  <div
                    className={`max-w-2xl rounded-2xl px-4 py-3 ${
                      message.role === 'user'
                        ? 'bg-primary-600 text-white'
                        : message.role === 'system'
                        ? 'bg-yellow-600/20 text-yellow-400 border border-yellow-600/30'
                        : 'bg-dark-card text-gray-100 border border-dark-border'
                    }`}
                  >
                    {message.role === 'user' || message.role === 'system' ? (
                      <p className="whitespace-pre-wrap">{message.content}</p>
                    ) : (
                      <div 
                        className="markdown-content"
                        dangerouslySetInnerHTML={{ __html: marked.parse(message.content) }}
                      />
                    )}
                  </div>

                  {message.role === 'user' && (
                    <div className="w-8 h-8 bg-gray-600 rounded-lg flex items-center justify-center flex-shrink-0">
                      <User className="w-5 h-5 text-white" />
                    </div>
                  )}
                </div>
              ))}
              
              {loading && (
                <div className="flex gap-3 justify-start">
                  <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                  <div className="bg-dark-card border border-dark-border rounded-2xl px-4 py-3">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      {/* Input */}
      <div className="border-t border-dark-border bg-dark-card/50 backdrop-blur-sm">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              className="flex-1 input-field"
              disabled={loading}
            />
            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="btn-primary flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
