import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import CreateTest from './pages/CreateTest'
import Dashboard from './pages/Dashboard'
import TakeTest from './pages/TakeTest'
import Results from './pages/Results'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/create" element={<CreateTest />} />
          <Route path="/take/:testId" element={<TakeTest />} />
          <Route path="/results/:testId" element={<Results />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
