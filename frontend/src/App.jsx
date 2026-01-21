import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './AuthContext'
import ProtectedRoute from './pages/ProtectedRoute'
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import VerifyEmailPage from './pages/VerifyEmailPage'
import CreateJDPage from './pages/CreateJDPage'
import EnhanceJDPage from './pages/EnhanceJDPage'
import OrgContextInputPage from './pages/OrgContextInputPage'
import InterviewPlanDisplayPage from './pages/InterviewPlanDisplayPage'

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/verify-email" element={<VerifyEmailPage />} />
          <Route
            path="/create"
            element={
              <ProtectedRoute>
                <CreateJDPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/enhance"
            element={
              <ProtectedRoute>
                <EnhanceJDPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/interview-context"
            element={
              <ProtectedRoute>
                <OrgContextInputPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/interview-plan"
            element={
              <ProtectedRoute>
                <InterviewPlanDisplayPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App

