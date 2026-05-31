import { NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: 'Dashboard' },
  { to: '/hotel', label: 'Hotel' },
  { to: '/market', label: 'Market' },
  { to: '/cochera', label: 'Cochera' },
  { to: '/caja', label: 'Caja' },
  { to: '/recados', label: 'Recados' },
]

export default function Sidebar() {
  return (
    <aside className="hidden w-72 flex-col bg-primary text-white lg:flex">
      <div className="border-b border-white/10 px-6 py-6">
        <p className="text-xs uppercase tracking-[0.3em] text-white/60">Hotel Venecia</p>
        <h1 className="mt-2 font-heading text-2xl font-semibold">Gestión Integral</h1>
      </div>
      <nav className="flex-1 space-y-2 px-4 py-6">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) =>
              `block rounded-2xl px-4 py-3 text-sm font-semibold transition ${isActive ? 'bg-white/15 text-white' : 'text-white/75 hover:bg-white/10 hover:text-white'}`
            }
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
      <div className="border-t border-white/10 px-6 py-5 text-xs text-white/60">React + Vite + Electron ready</div>
    </aside>
  )
}
