import { useEffect, useState } from 'react'
import client from '../api/client.js'

const EMPTY = {
  name: '',
  company_name: '',
  product_name: '',
  allowed_topics: '',
  competitor_names: '',
  banned_words: '',
  required_disclaimers: '',
}

function toList(str) {
  return str.split(',').map((s) => s.trim()).filter(Boolean)
}

export default function Policies() {
  const [policies, setPolicies] = useState([])
  const [form, setForm] = useState(EMPTY)
  const [error, setError] = useState('')

  const load = () => {
    client.get('/policies/').then((res) => setPolicies(res.data)).catch((err) => setError(err.message))
  }

  useEffect(load, [])

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await client.post('/policies/', {
        name: form.name,
        company_name: form.company_name,
        product_name: form.product_name,
        allowed_topics: toList(form.allowed_topics),
        competitor_names: toList(form.competitor_names),
        banned_words: toList(form.banned_words),
        required_disclaimers: toList(form.required_disclaimers),
      })
      setForm(EMPTY)
      load()
    } catch (err) {
      setError(err.message)
    }
  }

  const remove = async (id) => {
    await client.delete(`/policies/${id}`)
    load()
  }

  return (
    <div>
      <h2>Guardrail Policies</h2>

      <div className="card">
        <h2>New Policy</h2>
        <form onSubmit={submit}>
          <div className="form-row">
            <label>Policy Name</label>
            <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          </div>
          <div className="form-row">
            <label>Company Name</label>
            <input value={form.company_name} onChange={(e) => setForm({ ...form, company_name: e.target.value })} />
          </div>
          <div className="form-row">
            <label>Product Name</label>
            <input value={form.product_name} onChange={(e) => setForm({ ...form, product_name: e.target.value })} />
          </div>
          <div className="form-row">
            <label>Allowed Topics (comma-separated)</label>
            <input value={form.allowed_topics} onChange={(e) => setForm({ ...form, allowed_topics: e.target.value })} placeholder="billing, shipping, returns, account settings" />
          </div>
          <div className="form-row">
            <label>Competitor Names (comma-separated)</label>
            <input value={form.competitor_names} onChange={(e) => setForm({ ...form, competitor_names: e.target.value })} />
          </div>
          <div className="form-row">
            <label>Banned Words (comma-separated)</label>
            <input value={form.banned_words} onChange={(e) => setForm({ ...form, banned_words: e.target.value })} />
          </div>
          <div className="form-row">
            <label>Required Disclaimers (comma-separated)</label>
            <input value={form.required_disclaimers} onChange={(e) => setForm({ ...form, required_disclaimers: e.target.value })} />
          </div>
          {error && <p className="error-text">{error}</p>}
          <button type="submit">Create Policy</button>
        </form>
      </div>

      <div className="card">
        <h2>Existing Policies</h2>
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Company</th>
              <th>Allowed Topics</th>
              <th>Competitors</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {policies.map((p) => (
              <tr key={p.id}>
                <td>{p.name}</td>
                <td>{p.company_name}</td>
                <td>{p.allowed_topics.join(', ')}</td>
                <td>{p.competitor_names.join(', ')}</td>
                <td><button className="secondary" onClick={() => remove(p.id)}>Delete</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
