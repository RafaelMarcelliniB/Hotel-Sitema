import { useState } from 'react'
import Card from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { useRecados } from '../hooks/useRecados'
import Spinner from '../components/ui/Spinner'
import ModalNuevoRecado from '../components/recados/ModalNuevoRecado'

const PRIORIDAD_COLORS = {
  ALTA: 'border-l-4 border-l-red-500 bg-red-50',
  MEDIA: 'border-l-4 border-l-yellow-500 bg-yellow-50',
  BAJA: 'border-l-4 border-l-blue-500 bg-blue-50'
}

export default function Recados() {
  const { recados, isLoading, marcarLeido } = useRecados()
  const [showModal, setShowModal] = useState(false)

  if (isLoading) return <Spinner />

  // Filtramos para mostrar primero los no leídos
  const recadosPendientes = recados.filter(r => !r.leido)

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-slate-800">Tablero de Recados</h2>
        <Button onClick={() => setShowModal(true)}>+ Nuevo Recado</Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {recadosPendientes.map((recado) => (
          <Card key={recado.id} className={`${PRIORIDAD_COLORS[recado.prioridad]} flex flex-col justify-between h-full shadow-sm`}>
            <div>
              <div className="flex justify-between items-start mb-3">
                <span className="text-xs font-bold text-slate-400 uppercase">
                  De: {recado.usuario_origen || 'Turno Anterior'}
                </span>
                <Badge variant={recado.prioridad === 'ALTA' ? 'danger' : 'warning'}>
                  {recado.prioridad}
                </Badge>
              </div>
              <h3 className="text-lg font-medium text-slate-800 mb-4 italic">
                "{recado.contenido}"
              </h3>
            </div>

            <div className="flex justify-between items-center mt-4 pt-3 border-t border-slate-200">
              <span className="text-xs text-slate-500">{recado.fecha_creacion}</span>
              <Button 
                variant="ghost" 
                className="text-blue-600 hover:bg-blue-100 text-xs"
                onClick={() => marcarLeido(recado.id)}
              >
                Marcar como leído
              </Button>
            </div>
          </Card>
        ))}
        
        {recadosPendientes.length === 0 && (
          <div className="col-span-full py-20 text-center text-slate-400">
            <p className="text-xl">No hay recados pendientes</p>
            <p className="text-sm">Todo está al día en el hotel.</p>
          </div>
        )}
      </div>

      {showModal && <ModalNuevoRecado onClose={() => setShowModal(false)} />}
    </div>
  )
}