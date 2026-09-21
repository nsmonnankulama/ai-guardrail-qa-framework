import { NavLink } from 'react-router-dom'

const LINKS = [
  { to: '/', label: 'Dashboard', end: true },
  { to: '/connectors', label: 'Connectors' },
  { to: '/policies', label: 'Guardrail Policies' },
  { to: '/suites', label: 'Test Suites' },
  { to: '/runs', label: 'Test Runs' },
]

export default function Nav() {
  return (
    <div className="sidebar">
      <h1>AI Guardrail QA</h1>
      <nav>
        {LINKS.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
            className={({ isActive }) => (isActive ? 'active' : '')}
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
    </div>
  )
}
