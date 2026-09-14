import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import api from '../services/api'

const AuthContext = createContext(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const checkLocalAuth = useCallback(async () => {
    const token = localStorage.getItem('token')
    if (!token) {
      setUser(null)
      setLoading(false)
      return
    }

    try {
      const response = await api.get('/auth/me')
      setUser({
        ...response.data,
        show_memory_timeline: localStorage.getItem('show_memory_timeline') === 'true'
      })
    } catch (error) {
      console.warn('Session expired or invalid token:', error)
      localStorage.removeItem('token')
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    checkLocalAuth()
  }, [checkLocalAuth])

  const loginDemo = async (email = 'demo@twinmind.ai') => {
    try {
      setLoading(true)
      const mockToken = `mock_google_token:${email}`
      const response = await api.post('/auth/google', {
        token: mockToken
      })

      localStorage.setItem('token', response.data.access_token)
      const userData = {
        ...response.data.user,
        show_memory_timeline: localStorage.getItem('show_memory_timeline') === 'true'
      }
      setUser(userData)
      return userData
    } catch (error) {
      console.error('Demo login failed:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const loginWithGoogle = async (googleToken) => {
    try {
      setLoading(true)
      const response = await api.post('/auth/google', {
        token: googleToken
      })

      localStorage.setItem('token', response.data.access_token)
      const userData = {
        ...response.data.user,
        show_memory_timeline: localStorage.getItem('show_memory_timeline') === 'true'
      }
      setUser(userData)
      return userData
    } catch (error) {
      console.error('Google token login failed:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const syncClerkSession = async (clerkToken, clerkUser) => {
    if (!clerkToken || !clerkUser) return
    try {
      const email = clerkUser.primaryEmailAddress?.emailAddress || 'demo@twinmind.ai'
      const name = clerkUser.fullName || clerkUser.username || email.split('@')[0]
      const picture = clerkUser.imageUrl

      const response = await api.post('/auth/clerk', {
        token: clerkToken,
        email,
        name,
        picture
      })

      localStorage.setItem('token', response.data.access_token)
      setUser({
        ...response.data.user,
        show_memory_timeline: localStorage.getItem('show_memory_timeline') === 'true'
      })
    } catch (error) {
      console.error('Clerk session synchronization failed:', error)
    }
  }

  const logout = async () => {
    localStorage.removeItem('token')
    setUser(null)
  }

  const updateUser = (userData) => {
    setUser((prev) => ({ ...prev, ...userData }))
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        loginDemo,
        loginWithGoogle,
        syncClerkSession,
        logout,
        updateUser,
        checkAuth: checkLocalAuth
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

