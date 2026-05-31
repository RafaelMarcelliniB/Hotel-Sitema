import Badge from '../ui/Badge'
import Button from '../ui/Button'
import { useAuthStore } from '../../store/authStore'
import { useCajaStore } from '../../store/cajaStore'

export default function TopBar() {
  const user = useAuthStore((state) => state.user)
  const clearSession = useAuthStore((state) => state.clearSession)
  const cajaActiva = useCajaStore((state) => state.cajaActiva)

  return (
    <header className="flex items-center justify-between gap-4 border-b border-slate-200 bg-white px-6 py-4">
      <div>
        <p className="text-sm text-slate-500">Bienvenido</p>
        <h2 className="font-heading text-2xl font-semibold text-slate-900">
          {user ? `${user.nombre} ${user.apellido}` : 'Usuario'}
        </h2>
      </div>
      <div className="flex items-center gap-3">
        {cajaActiva ? <Badge variant="success">Caja activa: {cajaActiva.turno}</Badge> : <Badge variant="warning">Sin caja activa</Badge>}
        <Badge variant="neutral">{user?.rol ?? 'sin rol'}</Badge>
        <Button variant="ghost" onClick={clearSession}>Salir</Button>
      </div>
    </header>
  )
}
