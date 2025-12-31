import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './AuthContext'
import ProtectedRoute from './ProtectedRoute'
import LandingPage from './LandingPage'
import LoginPage from './LoginPage'
import RegisterPage from './RegisterPage'
import EnhancementPage from './EnhancementPage'

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route
            path="/enhance"
            element={
              <ProtectedRoute>
                <EnhancementPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App
