import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import CreateTest from './pages/CreateTest'
import Dashboard from './pages/Dashboard'
import TakeTest from './pages/TakeTest'
import Results from './pages/Results'
import ExamSelector from './components/ExamSelector'
import { useExamStore } from './store/examStore'

function App() {
  const { selectedExam, setExam } = useExamStore();

  const handleSelectExam = (examId: string) => {
    // In a real app, you'd get name and color from the config
    // For now, mapping some defaults
    const names: Record<string, string> = {
      ncdpi: 'NCDPI', neet: 'NEET', jee: 'JEE', cbse: 'CBSE',
      icse: 'ICSE', tn_govt: 'TN Govt', sat: 'SAT', act: 'ACT'
    };
    const colors: Record<string, string> = {
      ncdpi: 'from-blue-500 to-blue-700',
      neet: 'from-green-500 to-green-700',
      jee: 'from-orange-500 to-orange-700',
      cbse: 'from-purple-500 to-purple-700',
      icse: 'from-teal-500 to-teal-700',
      tn_govt: 'from-red-500 to-red-700',
      sat: 'from-indigo-500 to-indigo-700',
      act: 'from-rose-500 to-rose-700'
    };

    setExam(examId, names[examId] || examId.toUpperCase(), colors[examId] || 'from-indigo-500 to-indigo-700');
  };

  return (
    <Router>
      <Layout>
        <Routes>
          <Route
            path="/"
            element={!selectedExam ? <ExamSelector onSelectExam={handleSelectExam} /> : <Navigate to="/dashboard" replace />}
          />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/create" element={<CreateTest />} />
          <Route path="/take/:testId" element={<TakeTest />} />
          <Route path="/results/:testId" element={<Results />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
