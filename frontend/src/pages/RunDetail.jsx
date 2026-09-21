import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import client from '../api/client.js'

function highlight(text, evidence) {
  if (!evidence || evidence.length === 0) return text
  const snippets = evidence
    .map((e) => (e.includes(':') ? e.split(':').slice(1).join(':') : e))
    .filter((s) => s && s.length > 1)

  let parts = [text]
  snippets.forEach((snippet, idx) => {
    const next = []
    parts.forEach((part) => {
      if (typeof part !== 'string') {
        next.push(part)
        return
      }
      const pieces = part.split(snippet)
      pieces.forEach((piece, i) => {
        next.push(piece)
        if (i < pieces.length - 1) {
          next.push(<mark key={`${idx}-${i}-${piece.length}`} style={{ background: 'rgba(239,90,90,0.4)', color: 'inherit' }}>{snippet}</mark>)
        }
      })
    })
    parts = next
  })
  return parts
}

export default function RunDetail() {
  const { runId } = useParams()
  const [run, setRun] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    client.get(`/runs/${runId}`).then((res) => setRun(res.data)).catch((err) => setError(err.message))
  }, [runId])

  if (error) return <p className="error-text">{error}</p>
  if (!run) return <p>Loading...</p>

  return (
    <div>
      <p><Link to="/runs">&larr; Back to runs</Link></p>
      <h2>Run #{run.id}</h2>
      <div className="grid card">
        <div className="stat-tile"><div className="value">{run.status}</div><div className="label">Status</div></div>
        <div className="stat-tile"><div className="value">{run.pass_count}</div><div className="label">Passed</div></div>
        <div className="stat-tile"><div className="value">{run.fail_count}</div><div className="label">Failed</div></div>
        <div className="stat-tile"><div className="value">{run.total_count}</div><div className="label">Total</div></div>
      </div>

      <div className="card">
        <h2>Transcript</h2>
        {run.results.map((r) => (
          <div className="transcript" key={r.id}>
            <div className="toolbar" style={{ marginBottom: 8 }}>
              <span className={`badge ${r.passed ? 'pass' : 'fail'}`}>{r.passed ? 'PASS' : 'FAIL'}</span>
              <span className={`badge severity-${r.severity}`}>{r.severity}</span>
              <span className="pill">{r.category.replace(/_/g, ' ')}</span>
              <span className="pill">{Math.round(r.latency_ms)}ms</span>
            </div>
            <div className="prompt"><strong>Prompt:</strong> {r.prompt}</div>
            <div className="response">
              <strong>Response:</strong> {highlight(r.response_text, r.evidence)}
            </div>
            {r.evidence && r.evidence.length > 0 && (
              <div style={{ marginTop: 8 }}>
                {r.evidence.map((e, i) => <span className="evidence-chip" key={i}>{e}</span>)}
              </div>
            )}
            <div style={{ marginTop: 8, fontSize: 12, color: 'var(--text-dim)' }}>{r.message}</div>
            {r.error && <div className="error-text">{r.error}</div>}
          </div>
        ))}
      </div>
    </div>
  )
}
