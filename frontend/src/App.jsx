import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import LandingPage from './LandingPage'
import EnhancementPage from './EnhancementPage'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/enhance" element={<EnhancementPage />} />
      </Routes>
    </Router>
  )
}

export default App
