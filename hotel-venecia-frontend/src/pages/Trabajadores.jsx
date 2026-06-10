import { useState } from 'react'
import { useTrabajadores } from '../hooks/useTrabajadores'
import Card from '../components/ui/Card'
import Table from '../components/ui/Table'
import { Button } from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import Spinner from '../components/ui/Spinner'
import ModalNuevoTrabajador from '../components/trabajadores/ModalNuevoTrabajador'

export default function Trabajadores() {
  const { trabajadores, isLoading } = useTrabajadores()
  const [showModal, setShowModal] = useState(false)
  const [selected, setSelected] = useState(null)

  if (isLoading) return <div className="p-10 text-center"><Spinner /></div>

  return (
    <div className="space-y-6 p-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">Usuarios</h2>
          <p className="text-sm text-slate-500">Listado de usuarios y roles del sistema.</p>
        </div>
        <Button onClick={() => { setSelected(null); setShowModal(true) }}>+ Registrar Usuario</Button>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {trabajadores.filter(t => t.username !== 'admin').map((t) => (
          <Card key={t.id} className="flex flex-col justify-between">
            <div>
              <h3 className="text-lg font-semibold text-slate-800">{t.nombre} {t.apellido}</h3>
              <p className="text-sm text-slate-500">@{t.username}</p>
            </div>
            <div className="mt-4 flex items-center justify-between">
              <div className="space-y-1">
                <div className="text-xs text-slate-500">Rol</div>
                <div className="text-sm font-medium">{t.rol}</div>
              </div>
              <div className="space-y-1 text-right">
                <div className="text-xs text-slate-500">Turno</div>
                <div className="text-sm font-medium">{t.turno || '—'}</div>
              </div>
            </div>
              <div className="mt-4 flex items-center justify-between">
              <div className={`inline-flex items-center gap-2 text-sm ${t.activo ? 'text-green-600' : 'text-red-600'}`}>
                <span className={`h-2 w-2 rounded-full ${t.activo ? 'bg-green-500' : 'bg-red-500'}`}></span>
                {t.activo ? 'Activo' : 'Inactivo'}
              </div>
              <Button variant="ghost" className="text-blue-600 h-8 px-2" onClick={() => { setSelected(t); setShowModal(true) }}>Editar</Button>
            </div>
          </Card>
        ))}
      </div>

      {showModal && <ModalNuevoTrabajador id={selected?.id} initialData={selected} onClose={() => setShowModal(false)} />}
    </div>
  )
}