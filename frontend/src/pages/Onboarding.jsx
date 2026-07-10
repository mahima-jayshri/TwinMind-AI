import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import { Brain, ArrowRight, ArrowLeft } from 'lucide-react'

export default function Onboarding() {
  const { user, updateUser } = useAuth()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [answer, setAnswer] = useState('')
  const [questionData, setQuestionData] = useState(null)
  const [currentStep, setCurrentStep] = useState(0)

  useEffect(() => {
    if (user && user.is_onboarded) {
      navigate('/dashboard')
      return
    }
    loadQuestion()
  }, [user, navigate])

  const loadQuestion = async () => {
    try {
      setLoading(true)
      const response = await api.post('/agent/onboarding', { answer: null })
      setQuestionData(response.data)
      setCurrentStep(response.data.step || 1)
      setAnswer('')
    } catch (error) {
      console.error('Failed to load question:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!answer.trim()) return

    try {
      setLoading(true)
      const response = await api.post('/agent/onboarding', { answer })
      
      if (response.data.completed) {
        updateUser({ is_onboarded: true, digital_dna: response.data.digital_dna })
        navigate('/dashboard')
      } else {
        setQuestionData(response.data)
        setCurrentStep(response.data.step)
        setAnswer('')
      }
    } catch (error) {
      console.error('Failed to submit answer:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSkip = async () => {
    try {
      setLoading(true)
      const response = await api.post('/agent/onboarding', { answer: 'Skipped' })
      
      if (response.data.completed) {
        updateUser({ is_onboarded: true })
        navigate('/dashboard')
      } else {
        setQuestionData(response.data)
        setCurrentStep(response.data.step)
        setAnswer('')
      }
    } catch (error) {
      console.error('Failed to skip:', error)
    } finally {
      setLoading(false)
    }
  }

  if (!questionData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-dark-bg via-slate-900 to-dark-bg p-4">
      <div className="max-w-2xl w-full">
        {/* Progress bar */}
        <div className="mb-8">
          <div className=" flex items-center justify-between text-sm text-gray-400 mb-2">
            <span>Step {currentStep} of {questionData.total_steps}</span>
            <span>{Math.round(questionData.progress)}% complete</span>
          </div>
          <div className="h-2 bg-dark-card rounded-full overflow-hidden">
            <div
              className="h-full bg-primary-600 transition-all duration-500"
              style={{ width: `${questionData.progress}%` }}
            ></div>
          </div>
        </div>

        {/* Question card */}
        <div className="card animate-slide-up">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 bg-primary-600 rounded-xl flex items-center justify-center">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-white">Building Your Digital DNA</h2>
              <p className="text-gray-400 text-sm">Help me understand you better</p>
            </div>
          </div>

          <div className="mb-8">
            <h3 className="text-2xl font-medium text-white mb-4">
              {questionData.question}
            </h3>
          </div>

          <form onSubmit={handleSubmit}>
            {questionData.question_type === 'select' ? (
              <div className="grid grid-cols-1 gap-3 mb-6">
                {questionData.options?.map((option) => (
                  <button
                    key={option}
                    type="button"
                    onClick={() => { setAnswer(option); handleSubmit({ preventDefault: () => {} }) }}
                    className={`p-4 rounded-lg border-2 text-left transition-all ${
                      answer === option
                        ? 'border-primary-600 bg-primary-600/10 text-white'
                        : 'border-dark-border hover:border-primary-600/50 text-gray-300'
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            ) : (
              <div className="mb-6">
                <input
                  type={questionData.question_type === 'number' ? 'number' : 
                        questionData.question_type === 'time' ? 'time' : 'text'}
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  placeholder="Type your answer..."
                  className="input-field w-full text-lg"
                  autoFocus
                />
              </div>
            )}

            <div className="flex gap-3">
              <button
                type="submit"
                disabled={loading || !answer.trim()}
                className="flex-1 btn-primary flex items-center justify-center gap-2"
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                ) : (
                  <>
                    Continue
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
              
              <button
                type="button"
                onClick={handleSkip}
                disabled={loading}
                className="btn-secondary"
              >
                Skip
              </button>
            </div>
          </form>
        </div>

        <p className="text-center text-gray-500 text-sm mt-6">
          Your answers help create a personalized AI that understands you
        </p>
      </div>
    </div>
  )
}
