import { useEffect, useState } from 'react'
import client from '../api/client.js'

const EMPTY_HTTP_CONFIG = {
  url: '',
  method: 'POST',
  headers: '{"Content-Type": "application/json"}',
  request_template: '{"message": "{{prompt}}"}',
  response_path: 'reply',
}

const EMPTY_LLM_CONFIG = {
  model: '',
  api_key: '',
  api_base: '',
  system_prompt: '',
}

export default function Connectors() {
  const [connectors, setConnectors] = useState([])
  const [name, setName] = useState('')
  const [type, setType] = useState('http')
  const [httpConfig, setHttpConfig] = useState(EMPTY_HTTP_CONFIG)
  const [llmConfig, setLlmConfig] = useState(EMPTY_LLM_CONFIG)
  const [error, setError] = useState('')
  const [testResults, setTestResults] = useState({})

  const load = () => {
    client.get('/connectors/').then((res) => setConnectors(res.data)).catch((err) => setError(err.message))
  }

  useEffect(load, [])

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      let config
      if (type === 'http') {
        config = { ...httpConfig, headers: JSON.parse(httpConfig.headers || '{}') }
      } else {
        config = { ...llmConfig }
      }
      await client.post('/connectors/', { name, type, config })
      setName('')
      setHttpConfig(EMPTY_HTTP_CONFIG)
      setLlmConfig(EMPTY_LLM_CONFIG)
      load()
    } catch (err) {
      setError(err.response?.data?.detail ? JSON.stringify(err.response.data.detail) : err.message)
    }
  }

  const remove = async (id) => {
    await client.delete(`/connectors/${id}`)
    load()
  }

  const test = async (id) => {
    setTestResults((prev) => ({ ...prev, [id]: { loading: true } }))
    try {
      const res = await client.post(`/connectors/${id}/test`)
      setTestResults((prev) => ({ ...prev, [id]: { loading: false, ...res.data } }))
    } catch (err) {
      setTestResults((prev) => ({ ...prev, [id]: { loading: false, error: err.message } }))
    }
  }

  return (
    <div>
      <h2>Connectors</h2>

      <div className="card">
        <h2>Add Connector</h2>
        <form onSubmit={submit}>
          <div className="form-row">
            <label>Name</label>
            <input value={name} onChange={(e) => setName(e.target.value)} required />
          </div>
          <div className="form-row">
            <label>Type</label>
            <select value={type} onChange={(e) => setType(e.target.value)}>
              <option value="http">Generic HTTP / REST endpoint</option>
              <option value="llm">Direct LLM (via LiteLLM)</option>
            </select>
          </div>

          {type === 'http' ? (
            <>
              <div className="form-row">
                <label>URL</label>
                <input
                  value={httpConfig.url}
                  onChange={(e) => setHttpConfig({ ...httpConfig, url: e.target.value })}
                  placeholder="https://your-chatbot-api.example.com/chat"
                  required
                />
              </div>
              <div className="form-row">
                <label>Headers (JSON)</label>
                <textarea
                  rows={2}
                  value={httpConfig.headers}
                  onChange={(e) => setHttpConfig({ ...httpConfig, headers: e.target.value })}
                />
              </div>
              <div className="form-row">
                <label>Request Template (use {'{{prompt}}'} placeholder)</label>
                <textarea
                  rows={2}
                  value={httpConfig.request_template}
                  onChange={(e) => setHttpConfig({ ...httpConfig, request_template: e.target.value })}
                />
              </div>
              <div className="form-row">
                <label>Response Path (dot path to reply text, e.g. choices.0.message.content)</label>
                <input
                  value={httpConfig.response_path}
                  onChange={(e) => setHttpConfig({ ...httpConfig, response_path: e.target.value })}
                />
              </div>
            </>
          ) : (
            <>
              <div className="form-row">
                <label>Model (blank = use server AI_MODEL env default)</label>
                <input
                  value={llmConfig.model}
                  onChange={(e) => setLlmConfig({ ...llmConfig, model: e.target.value })}
                  placeholder="gpt-4o-mini / claude-3-5-sonnet-20240620 / ollama/llama3"
                />
              </div>
              <div className="form-row">
                <label>API Key (blank = use server AI_API_KEY env default)</label>
                <input
                  type="password"
                  value={llmConfig.api_key}
                  onChange={(e) => setLlmConfig({ ...llmConfig, api_key: e.target.value })}
                />
              </div>
              <div className="form-row">
                <label>API Base (optional, e.g. Ollama URL)</label>
                <input
                  value={llmConfig.api_base}
                  onChange={(e) => setLlmConfig({ ...llmConfig, api_base: e.target.value })}
                />
              </div>
              <div className="form-row">
                <label>System Prompt (the bot's guardrail instructions under test)</label>
                <textarea
                  rows={3}
                  value={llmConfig.system_prompt}
                  onChange={(e) => setLlmConfig({ ...llmConfig, system_prompt: e.target.value })}
                />
              </div>
            </>
          )}

          {error && <p className="error-text">{error}</p>}
          <button type="submit">Create Connector</button>
        </form>
      </div>

      <div className="card">
        <h2>Existing Connectors</h2>
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Config</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {connectors.map((c) => (
              <tr key={c.id}>
                <td>{c.name}</td>
                <td>{c.type}</td>
                <td style={{ maxWidth: 320, overflowWrap: 'break-word' }}>
                  <code style={{ fontSize: 11 }}>{JSON.stringify(c.config)}</code>
                  {testResults[c.id] && (
                    <div style={{ marginTop: 6, fontSize: 11, color: 'var(--text-dim)' }}>
                      {testResults[c.id].loading
                        ? 'Testing...'
                        : testResults[c.id].error
                          ? <span className="error-text">{testResults[c.id].error}</span>
                          : `"${(testResults[c.id].response_text || '').slice(0, 120)}" (${Math.round(testResults[c.id].latency_ms)}ms)`}
                    </div>
                  )}
                </td>
                <td>
                  <button className="secondary" onClick={() => test(c.id)}>Test</button>{' '}
                  <button className="secondary" onClick={() => remove(c.id)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
