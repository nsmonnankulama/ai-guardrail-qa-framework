import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import client from '../api/client.js'

export default function Runs() {
  const [runs, setRuns] = useState([])
  const [suites, setSuites] = useState([])
  const [connectors, setConnectors] = useState([])
  const [suiteId, setSuiteId] = useState('')
  const [connectorId, setConnectorId] = useState('')
  const [error, setError] = useState('')
  const [triggering, setTriggering] = useState(false)

  const load = () => {
    client.get('/runs/').then((res) => setRuns(res.data)).catch((err) => setError(err.message))
  }

  useEffect(() => {
    load()
    client.get('/suites/').then((res) => setSuites(res.data))
    client.get('/connectors/').then((res) => setConnectors(res.data))
  }, [])

  const trigger = async (e) => {
    e.preventDefault()
    setError('')
    setTriggering(true)
    try {
      await client.post('/runs/', { suite_id: Number(suiteId), connector_id: Number(connectorId) })
      load()
    } catch (err) {
      setError(err.response?.data?.detail ? JSON.stringify(err.response.data.detail) : err.message)
    } finally {
      setTriggering(false)
    }
  }

  return (
    <div>
      <h2>Test Runs</h2>

      <div className="card">
        <h2>Trigger a Run</h2>
        <form onSubmit={trigger}>
          <div className="form-row">
            <label>Test Suite</label>
            <select value={suiteId} onChange={(e) => setSuiteId(e.target.value)} required>
              <option value="">Select a suite</option>
              {suites.map((s) => (
                <option key={s.id} value={s.id}>{s.name} ({s.test_cases.length} cases)</option>
              ))}
            </select>
          </div>
          <div className="form-row">
            <label>Connector</label>
            <select value={connectorId} onChange={(e) => setConnectorId(e.target.value)} required>
              <option value="">Select a connector</option>
              {connectors.map((c) => (
                <option key={c.id} value={c.id}>{c.name} ({c.type})</option>
              ))}
            </select>
          </div>
          {error && <p className="error-text">{error}</p>}
          <button type="submit" disabled={triggering}>{triggering ? 'Running...' : 'Run Suite'}</button>
        </form>
      </div>

      <div className="card">
        <h2>Run History</h2>
        <table>
          <thead>
            <tr><th>ID</th><th>Status</th><th>Pass</th><th>Fail</th><th>Total</th><th>Started</th><th></th></tr>
          </thead>
          <tbody>
            {runs.map((run) => (
              <tr key={run.id}>
                <td>#{run.id}</td>
                <td>{run.status}</td>
                <td>{run.pass_count}</td>
                <td>{run.fail_count}</td>
                <td>{run.total_count}</td>
                <td>{new Date(run.started_at).toLocaleString()}</td>
                <td><Link to={`/runs/${run.id}`}>View Transcript</Link></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
