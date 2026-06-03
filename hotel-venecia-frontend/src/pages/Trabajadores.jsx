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

  if (isLoading) return <div className="p-10 text-center"><Spinner /></div>

  return (
    <div className="space-y-6 p-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">Gestión de Personal</h2>
          <p className="text-sm text-slate-500">Administra los accesos y roles de los trabajadores.</p>
        </div>
        <Button onClick={() => setShowModal(true)}>+ Registrar Trabajador</Button>
      </div>

      <Card>
        <Table columns={['DNI / Usuario', 'Nombre Completo', 'Rol', 'Estado', 'Acciones']}>
          {trabajadores.map((t) => (
            <tr key={t.id} className="border-b last:border-0 hover:bg-slate-50 transition-colors">
              <td className="px-4 py-4 font-mono font-medium">{t.username}</td>
              <td className="px-4 py-4">{t.first_name} {t.last_name}</td>
              <td className="px-4 py-4">
                <Badge variant={t.rol === 'admin' ? 'danger' : 'info'}>
                  {t.rol.toUpperCase()}
                </Badge>
              </td>
              <td className="px-4 py-4">
                <div className="flex items-center gap-2">
                  <span className={`h-2 w-2 rounded-full ${t.is_active ? 'bg-green-500' : 'bg-red-500'}`}></span>
                  {t.is_active ? 'Activo' : 'Inactivo'}
                </div>
              </td>
              <td className="px-4 py-4">
                <Button variant="ghost" className="text-blue-600 h-8 px-2">Editar</Button>
              </td>
            </tr>
          ))}
        </Table>
      </Card>

      {showModal && <ModalNuevoTrabajador onClose={() => setShowModal(false)} />}
    </div>
  )
}