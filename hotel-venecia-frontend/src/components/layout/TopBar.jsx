import { useState } from 'react'
import Badge from '../ui/Badge'
import Button from '../ui/Button'
import { useAuthStore } from '../../store/authStore'
import { useCajas } from '../../hooks/useCajas'
import { useRecados } from '../../hooks/useRecados'

export default function TopBar() {
  const user = useAuthStore((state) => state.user)
  const clearSession = useAuthStore((state) => state.clearSession)
  
  const { useResumen } = useCajas()
  const { data: resumen } = useResumen()
  
  // Consumimos los recados en tiempo real
  const { recados, marcarLeido } = useRecados()
  const [showNotifications, setShowNotifications] = useState(false)

  // Filtramos recados pendientes o en proceso; los resueltos ya no deben mostrarse
  const notificaciones = recados.filter(r => r.estado !== 'RESUELTO')

  // Verificamos si existe una caja activa en la respuesta del servidor
  const cajaActivaReal = resumen && resumen.caja

  return (
    <header className="flex items-center justify-between gap-4 border-b border-slate-200 bg-white px-6 py-4 sticky top-0 z-40">
      <div className="flex items-center gap-4">
        {/* Hamburger for mobile */}
        <button className="lg:hidden p-2 rounded-md text-slate-600 hover:bg-slate-100" onClick={() => { window.dispatchEvent(new CustomEvent('toggle-sidebar')) }} aria-label="Toggle sidebar">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>

        <div>
          <p className="text-sm text-slate-500">Bienvenido</p>
          <h2 className="font-heading text-2xl font-semibold text-slate-900">
            {user ? `${user.nombre} ${user.apellido}` : 'Usuario'}
          </h2>
        </div>
      </div>
      
      <div className="flex items-center gap-4">
        {/* Centro de Notificaciones Dropdown */}
        <div className="relative">
          <button 
            onClick={() => setShowNotifications(!showNotifications)}
            className="p-2 text-slate-500 hover:bg-slate-100 rounded-full transition-colors relative"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            
            {notificaciones.length > 0 && (
              <span className="absolute top-1 right-1 flex h-4 w-4">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-4 w-4 bg-red-500 text-[10px] text-white items-center justify-center font-bold">
                  {notificaciones.length}
                </span>
              </span>
            )}
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-white border border-slate-200 rounded-xl shadow-xl overflow-hidden z-50">
              <div className="p-3 border-b bg-slate-50 font-semibold text-sm text-slate-700">
                Notificaciones de Turno
              </div>
              <div className="max-h-64 overflow-y-auto">
                {notificaciones.length > 0 ? (
                  notificaciones.map(n => (
                    <div key={n.id} className="p-3 border-b hover:bg-slate-50 transition-colors flex flex-col gap-1 relative group">
                      <div className="flex justify-between items-center">
                        <Badge variant={n.estado === 'PENDIENTE' ? 'danger' : 'warning'} className="text-[9px] px-1 py-0">
                          {n.estado}
                        </Badge>
                        <button 
                          onClick={() => marcarLeido(n.id)}
                          className="text-[10px] text-blue-600 font-medium opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          Marcar leído
                        </button>
                      </div>
                      <p className="text-xs text-slate-700 pr-2 italic">"{n.descripcion || n.titulo}"</p>
                    </div>
                  ))
                ) : (
                  <div className="p-6 text-center text-slate-400 text-xs">
                    Sin recados urgentes pendientes
                  </div>
                )}
              </div>
              <a 
                href="/recados" 
                className="block p-2 text-center text-xs font-semibold bg-slate-50 hover:bg-slate-100 border-t text-slate-700"
                onClick={() => setShowNotifications(false)}
              >
                Ver todos los recados
              </a>
            </div>
          )}
        </div>

        <div className="h-6 w-[1px] bg-slate-200"></div>

        {/* Bloque de Estados ACTUALIZADO */}
        <div className="flex items-center gap-3">
          {cajaActivaReal ? (
            <Badge variant="success" className="animate-fade-in flex items-center gap-1">
              <span className="h-1.5 w-1.5 rounded-full bg-white animate-pulse"></span>
              Caja activa: {cajaActivaReal.turno}
            </Badge>
          ) : (
            <Badge variant="warning">Sin caja activa</Badge>
          )}
          
          <Badge variant="neutral" className="uppercase tracking-wider">
            {user?.rol ?? 'sin rol'}
          </Badge>
          
          <Button 
            variant="ghost" 
            size="sm"
            onClick={() => {
              if (confirm("¿Estás seguro de que deseas salir del sistema?")) {
                clearSession()
              }
            }}
          >
            Salir
          </Button>
        </div>
      </div>
    </header>
  )
}