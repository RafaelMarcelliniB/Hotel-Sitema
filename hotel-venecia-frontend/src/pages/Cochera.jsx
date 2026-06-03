import { useState } from 'react'
import Card from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { useEspacios } from '../hooks/useEspacios'
import Spinner from '../components/ui/Spinner'
import ModalIngresoCochera from '../components/cochera/ModalIngresoCochera' // Lo crearemos abajo

export default function Cochera() {
  const { espacios, isLoading, registrarSalida } = useEspacios()
  const [selectedEspacio, setSelectedEspacio] = useState(null)

  if (isLoading) return <Spinner />

  const handleLiberar = async (id) => {
    if (confirm("¿Desea procesar la salida y realizar el cobro?")) {
      try {
        await registrarSalida(id)
        alert("Salida registrada correctamente")
      } catch (err) {
        alert("Error al procesar salida")
      }
    }
  }

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6 text-slate-800">Control de Cochera</h2>
      
      <div className="grid gap-4 md:grid-cols-3 xl:grid-cols-4">
        {espacios.map((espacio) => (
          <Card key={espacio.id} className={espacio.estado === 'OCUPADO' ? 'border-red-200 bg-red-50/30' : 'border-green-200'}>
            <div className="flex items-center justify-between">
              <span className="text-2xl font-black text-slate-400">#{espacio.numero}</span>
              <Badge variant={espacio.estado === 'LIBRE' ? 'success' : 'danger'}>
                {espacio.estado}
              </Badge>
            </div>

            <div className="mt-4 min-h-[60px]">
              {espacio.estado === 'OCUPADO' ? (
                <div>
                  <p className="text-lg font-bold text-red-700 tracking-widest">{espacio.placa || 'PLACA-123'}</p>
                  <p className="text-xs text-slate-500">Ingreso: {espacio.hora_ingreso || '14:20 PM'}</p>
                </div>
              ) : (
                <p className="text-sm text-slate-500">Disponible para {espacio.tipo}</p>
              )}
            </div>

            <div className="mt-4 pt-4 border-t border-slate-100">
              {espacio.estado === 'LIBRE' ? (
                <Button className="w-full" onClick={() => setSelectedEspacio(espacio)}>
                  Registrar Ingreso
                </Button>
              ) : (
                <Button variant="outline" className="w-full text-red-600 border-red-200" onClick={() => handleLiberar(espacio.id)}>
                  Procesar Salida
                </Button>
              )}
            </div>
          </Card>
        ))}
      </div>

      {selectedEspacio && (
        <ModalIngresoCochera 
          espacio={selectedEspacio} 
          onClose={() => setSelectedEspacio(null)} 
        />
      )}
    </div>
  )
}