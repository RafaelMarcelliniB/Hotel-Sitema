import { NavLink } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'

function buildLinksForRole(role) {
    const all = [
    { to: '/', label: 'Dashboard' },
    { to: '/hotel', label: 'Hotel' },
    { to: '/reservas', label: 'Reservas' },
    { to: '/market', label: 'Market' },
    { to: '/cochera', label: 'Cochera' },
    { to: '/caja', label: 'Caja' },
    { to: '/recados', label: 'Recados' },
    { to: '/trabajadores', label: 'Usuarios' },
  ]

  if (!role) return [{ to: '/', label: 'Dashboard' }]

  const r = role.toLowerCase()
  if (r === 'admin') return all
  if (r === 'recepcionista') return all.filter(l => ['/', '/reservas', '/hotel','/cochera','/caja','/recados'].includes(l.to))
  if (r === 'cajero') return [{ to: '/', label: 'Dashboard' }, { to: '/market', label: 'Market' }, { to: '/caja?module=market', label: 'Caja (Market)' }, { to: '/recados', label: 'Recados' }]
  return [{ to: '/', label: 'Dashboard' }]
}

export default function Sidebar({ open = false, onClose = () => {} }) {
  const user = useAuthStore(state => state.user)
  const links = buildLinksForRole(user?.rol)
  return (
    <>
      {/* Desktop sidebar */}
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

      {/* Mobile sidebar overlay */}
      <div className={`${open ? 'fixed inset-0 z-40 flex' : 'hidden' } lg:hidden`}> 
        <div className="fixed inset-0 bg-black/40" onClick={onClose} />
        <aside className="relative z-50 w-72 flex flex-col bg-primary text-white">
          <div className="border-b border-white/10 px-6 py-6 flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-white/60">Hotel Venecia</p>
              <h1 className="mt-2 font-heading text-2xl font-semibold">Gestión Integral</h1>
            </div>
            <button className="text-white/80" onClick={onClose} aria-label="Cerrar menu">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <nav className="flex-1 space-y-2 px-4 py-6">
            {links.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                onClick={onClose}
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
      </div>
    </>
  )
}
