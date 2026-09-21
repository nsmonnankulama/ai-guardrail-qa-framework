export default function BarChart({ data }) {
  const entries = Object.entries(data || {})
  if (entries.length === 0) {
    return <p style={{ color: 'var(--text-dim)' }}>No test results yet.</p>
  }

  return (
    <div className="bar-chart">
      {entries.map(([category, counts]) => {
        const total = (counts.passed || 0) + (counts.failed || 0)
        const passPct = total ? (counts.passed / total) * 100 : 0
        const failPct = total ? (counts.failed / total) * 100 : 0
        return (
          <div className="bar-row" key={category}>
            <span>{category.replace(/_/g, ' ')}</span>
            <div className="bar-track">
              <div className="bar-fill-pass" style={{ width: `${passPct}%` }} />
              <div className="bar-fill-fail" style={{ width: `${failPct}%` }} />
            </div>
            <span>{counts.passed || 0} / {total}</span>
          </div>
        )
      })}
    </div>
  )
}
