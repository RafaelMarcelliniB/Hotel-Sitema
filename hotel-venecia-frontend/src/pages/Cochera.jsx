import { useState } from 'react'
import Card from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { useEspacios } from '../hooks/useEspacios'
import Spinner from '../components/ui/Spinner'
import ModalIngresoCochera from '../components/cochera/ModalIngresoCochera'
import ModalSalidaCochera from '../components/cochera/ModalSalidaCochera' // <-- Importamos tu modal de salida

export default function Cochera() {
  const { espacios, isLoading } = useEspacios()
  const [selectedEspacio, setSelectedEspacio] = useState(null)
  const [selectedEspacioSalida, setSelectedEspacioSalida] = useState(null) // <-- Nuevo estado para controlar la salida

  if (isLoading) return <Spinner />

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
                  <p className="text-xs text-slate-600">Tipo: {espacio.vehiculo_actual?.tipo_vehiculo || espacio.tipo}</p>
                  {espacio.vehiculo_actual?.habitacion && (
                    <p className="text-xs text-slate-600">Habitación: Hab. {espacio.vehiculo_actual.habitacion}</p>
                  )}
                  <p className="text-xs text-slate-500">Ingreso: {espacio.hora_ingreso || '14:20 PM'}</p>
                  {espacio.vehiculo_actual?.hora_salida_estimada && (
                    <p className="text-xs text-slate-600">Salida estimada: {espacio.vehiculo_actual.hora_salida_estimada}</p>
                  )}
                  {espacio.vehiculo_actual?.observaciones && (
                    <p className="text-xs text-slate-600">Nota: {espacio.vehiculo_actual.observaciones}</p>
                  )}
                  {/* Mostrar tipo de cliente si existe el registro actual */}
                  {espacio.vehiculo_actual?.tipo_cliente && (
                    <p className="text-xs mt-1">
                      <span className="font-semibold">Cliente:</span>{' '}
                      {espacio.vehiculo_actual.tipo_cliente === 'HUESPED' ? 'Huésped' : 'Público'}
                    </p>
                  )}
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
                /* CORREGIDO: Ya no ejecuta handleLiberar. Ahora setea el estado para abrir tu modal */
                <Button 
                  variant="outline" 
                  className="w-full text-red-600 border-red-200 hover:bg-red-50" 
                  onClick={() => setSelectedEspacioSalida(espacio)}
                >
                  Procesar Salida
                </Button>
              )}
            </div>
          </Card>
        ))}
      </div>

      {/* MODAL INGRESO */}
      {selectedEspacio && (
        <ModalIngresoCochera 
          espacio={selectedEspacio} 
          onClose={() => setSelectedEspacio(null)} 
        />
      )}

      {/* MODAL SALIDA (Agregado para que pinte en pantalla) */}
      {selectedEspacioSalida && (
        <ModalSalidaCochera 
          espacio={selectedEspacioSalida} 
          onClose={() => setSelectedEspacioSalida(null)} 
        />
      )}
    </div>
  )
}