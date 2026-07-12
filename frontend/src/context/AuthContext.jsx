import { createContext, useContext, useState, useEffect } from 'react'
import { useAuth as useClerkAuth, useUser as useClerkUser } from '@clerk/clerk-react'
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

  const clerkAuth = useClerkAuth()
  const clerkUser = useClerkUser()

  const { isSignedIn, getToken, signOut } = clerkAuth
  const { user: cUser, isLoaded } = clerkUser

  useEffect(() => {
    if (isLoaded) {
      syncWithClerk()
    }
  }, [isSignedIn, cUser, isLoaded])

  const syncWithClerk = async () => {
    if (isSignedIn && cUser) {
      try {
        const token = await getToken()
        const email = cUser.primaryEmailAddress?.emailAddress || 'demo@twinmind.ai'
        const name = cUser.fullName || cUser.username || email.split('@')[0]
        const picture = cUser.imageUrl

        console.log('Syncing authenticated Clerk session with local backend...')
        const response = await api.post('/auth/clerk', {
          token,
          email,
          name,
          picture
        })

        console.log('Clerk sync successful:', response.data)
        localStorage.setItem('token', response.data.access_token)
        setUser({
          ...response.data.user,
          show_memory_timeline: localStorage.getItem('show_memory_timeline') === 'true'
        })
      } catch (error) {
        console.error('Clerk session synchronization failed:', error)
        localStorage.removeItem('token')
        setUser(null)
      }
    } else {
      localStorage.removeItem('token')
      setUser(null)
    }
    setLoading(false)
  }

  const login = async (googleToken) => {
    // If external caller uses login directly (e.g. legacy/mock calls),
    // we bypass. For Clerk, users sign in via the overlay modal.
    console.warn('Direct login bypass, Clerk auth recommended.')
  }

  const logout = async () => {
    console.log('Logging out from Clerk...')
    await signOut()
    localStorage.removeItem('token')
    setUser(null)
  }

  const updateUser = (userData) => {
    setUser((prev) => ({ ...prev, ...userData }))
  }

  const checkAuth = async () => {
    await syncWithClerk()
  }

  return (
    <AuthContext.Provider value={{ user, loading: loading || !isLoaded, login, logout, updateUser, checkAuth }}>
      {children}
    </AuthContext.Provider>
  )
}
