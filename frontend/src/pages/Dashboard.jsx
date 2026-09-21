import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import client from '../api/client.js'
import BarChart from '../components/BarChart.jsx'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    client
      .get('/dashboard/stats')
      .then((res) => setStats(res.data))
      .catch((err) => setError(err.message))
  }, [])

  if (error) return <p className="error-text">Failed to load dashboard: {error}</p>
  if (!stats) return <p>Loading...</p>

  return (
    <div>
      <h2>Dashboard</h2>
      <div className="grid card">
        <div className="stat-tile">
          <div className="value">{stats.total_runs}</div>
          <div className="label">Total Runs</div>
        </div>
        <div className="stat-tile">
          <div className="value">{stats.total_cases_executed}</div>
          <div className="label">Cases Executed</div>
        </div>
        <div className="stat-tile">
          <div className="value">{stats.pass_rate}%</div>
          <div className="label">Overall Pass Rate</div>
        </div>
      </div>

      <div className="card">
        <h2>Category Breakdown</h2>
        <BarChart data={stats.category_breakdown} />
      </div>

      <div className="card">
        <h2>Recent Runs</h2>
        {stats.recent_runs.length === 0 ? (
          <p style={{ color: 'var(--text-dim)' }}>No test runs yet. Create a suite and trigger a run.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Status</th>
                <th>Pass</th>
                <th>Fail</th>
                <th>Total</th>
                <th>Started</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {stats.recent_runs.map((run) => (
                <tr key={run.id}>
                  <td>#{run.id}</td>
                  <td>{run.status}</td>
                  <td>{run.pass_count}</td>
                  <td>{run.fail_count}</td>
                  <td>{run.total_count}</td>
                  <td>{new Date(run.started_at).toLocaleString()}</td>
                  <td><Link to={`/runs/${run.id}`}>View</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
