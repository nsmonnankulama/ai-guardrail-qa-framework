import { useEffect, useState } from 'react'
import client from '../api/client.js'

export default function Suites() {
  const [suites, setSuites] = useState([])
  const [policies, setPolicies] = useState([])
  const [categories, setCategories] = useState([])
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [policyId, setPolicyId] = useState('')
  const [error, setError] = useState('')
  const [selectedSuiteId, setSelectedSuiteId] = useState(null)

  const [caseCategory, setCaseCategory] = useState('')
  const [casePrompt, setCasePrompt] = useState('')
  const [caseExpected, setCaseExpected] = useState('refuse')
  const [caseKb, setCaseKb] = useState('')

  const [genCategory, setGenCategory] = useState('')
  const [genCount, setGenCount] = useState(5)
  const [generating, setGenerating] = useState(false)

  const loadSuites = () => {
    client.get('/suites/').then((res) => setSuites(res.data)).catch((err) => setError(err.message))
  }

  useEffect(() => {
    loadSuites()
    client.get('/policies/').then((res) => setPolicies(res.data))
    client.get('/testcases/categories').then((res) => {
      setCategories(res.data)
      setCaseCategory(res.data[0] || '')
      setGenCategory(res.data[0] || '')
    })
  }, [])

  const selectedSuite = suites.find((s) => s.id === selectedSuiteId)

  const createSuite = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await client.post('/suites/', { name, description, policy_id: policyId ? Number(policyId) : null })
      setName('')
      setDescription('')
      setPolicyId('')
      loadSuites()
    } catch (err) {
      setError(err.message)
    }
  }

  const deleteSuite = async (id) => {
    await client.delete(`/suites/${id}`)
    if (selectedSuiteId === id) setSelectedSuiteId(null)
    loadSuites()
  }

  const addCase = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await client.post('/testcases/', {
        suite_id: selectedSuiteId,
        category: caseCategory,
        prompt: casePrompt,
        expected_behavior: caseExpected,
        kb_context: caseKb,
      })
      setCasePrompt('')
      setCaseKb('')
      loadSuites()
    } catch (err) {
      setError(err.response?.data?.detail ? JSON.stringify(err.response.data.detail) : err.message)
    }
  }

  const deleteCase = async (id) => {
    await client.delete(`/testcases/${id}`)
    loadSuites()
  }

  const generate = async () => {
    if (!selectedSuite) return
    setGenerating(true)
    setError('')
    try {
      const policy = policies.find((p) => p.id === selectedSuite.policy_id)
      await client.post('/testcases/generate', {
        suite_id: selectedSuiteId,
        category: genCategory,
        company_name: policy?.company_name || '',
        product_name: policy?.product_name || '',
        allowed_topics: policy?.allowed_topics || [],
        competitor_names: policy?.competitor_names || [],
        count: Number(genCount),
      })
      loadSuites()
    } catch (err) {
      setError(err.response?.data?.detail ? JSON.stringify(err.response.data.detail) : err.message)
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div>
      <h2>Test Suites</h2>

      <div className="card">
        <h2>New Suite</h2>
        <form onSubmit={createSuite}>
          <div className="form-row">
            <label>Name</label>
            <input value={name} onChange={(e) => setName(e.target.value)} required />
          </div>
          <div className="form-row">
            <label>Description</label>
            <input value={description} onChange={(e) => setDescription(e.target.value)} />
          </div>
          <div className="form-row">
            <label>Guardrail Policy</label>
            <select value={policyId} onChange={(e) => setPolicyId(e.target.value)}>
              <option value="">None</option>
              {policies.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>
          {error && <p className="error-text">{error}</p>}
          <button type="submit">Create Suite</button>
        </form>
      </div>

      <div className="card">
        <h2>Suites</h2>
        <table>
          <thead>
            <tr><th>Name</th><th>Description</th><th># Cases</th><th></th></tr>
          </thead>
          <tbody>
            {suites.map((s) => (
              <tr key={s.id}>
                <td>{s.name}</td>
                <td>{s.description}</td>
                <td>{s.test_cases.length}</td>
                <td>
                  <button className="secondary" onClick={() => setSelectedSuiteId(s.id)}>Manage</button>{' '}
                  <button className="secondary" onClick={() => deleteSuite(s.id)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedSuite && (
        <div className="card">
          <h2>Manage: {selectedSuite.name}</h2>

          <div className="toolbar">
            <select value={genCategory} onChange={(e) => setGenCategory(e.target.value)}>
              {categories.map((c) => <option key={c} value={c}>{c.replace(/_/g, ' ')}</option>)}
            </select>
            <input
              type="number"
              min={1}
              max={20}
              style={{ width: 70 }}
              value={genCount}
              onChange={(e) => setGenCount(e.target.value)}
            />
            <button onClick={generate} disabled={generating}>
              {generating ? 'Generating...' : 'AI-Generate Test Cases'}
            </button>
          </div>

          <form onSubmit={addCase} style={{ marginBottom: 20 }}>
            <div className="form-row">
              <label>Category</label>
              <select value={caseCategory} onChange={(e) => setCaseCategory(e.target.value)}>
                {categories.map((c) => <option key={c} value={c}>{c.replace(/_/g, ' ')}</option>)}
              </select>
            </div>
            <div className="form-row">
              <label>Prompt</label>
              <textarea rows={2} value={casePrompt} onChange={(e) => setCasePrompt(e.target.value)} required />
            </div>
            <div className="form-row">
              <label>Expected Behavior</label>
              <select value={caseExpected} onChange={(e) => setCaseExpected(e.target.value)}>
                <option value="refuse">Bot should refuse</option>
                <option value="comply">Bot should comply / answer</option>
              </select>
            </div>
            <div className="form-row">
              <label>Knowledge Base Context (optional, for hallucination checks)</label>
              <textarea rows={2} value={caseKb} onChange={(e) => setCaseKb(e.target.value)} />
            </div>
            <button type="submit">Add Test Case</button>
          </form>

          <table>
            <thead>
              <tr><th>Category</th><th>Prompt</th><th>Expected</th><th></th></tr>
            </thead>
            <tbody>
              {selectedSuite.test_cases.map((c) => (
                <tr key={c.id}>
                  <td>{c.category.replace(/_/g, ' ')}</td>
                  <td style={{ maxWidth: 400 }}>{c.prompt}</td>
                  <td>{c.expected_behavior}</td>
                  <td><button className="secondary" onClick={() => deleteCase(c.id)}>Delete</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
