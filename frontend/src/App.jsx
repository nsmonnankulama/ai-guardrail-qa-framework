import { Routes, Route } from 'react-router-dom'
import Nav from './components/Nav.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Connectors from './pages/Connectors.jsx'
import Policies from './pages/Policies.jsx'
import Suites from './pages/Suites.jsx'
import Runs from './pages/Runs.jsx'
import RunDetail from './pages/RunDetail.jsx'

export default function App() {
  return (
    <div className="app-shell">
      <Nav />
      <div className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/connectors" element={<Connectors />} />
          <Route path="/policies" element={<Policies />} />
          <Route path="/suites" element={<Suites />} />
          <Route path="/runs" element={<Runs />} />
          <Route path="/runs/:runId" element={<RunDetail />} />
        </Routes>
      </div>
    </div>
  )
}
