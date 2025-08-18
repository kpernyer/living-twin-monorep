import { useAuth } from '../features/auth/AuthProvider'
import SignIn from '../features/auth/SignIn'
import { Dashboard } from './dashboard/Dashboard'

export default function App() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    )
  }

  if (!user) {
    return <SignIn />
  }

  return <Dashboard />
}
