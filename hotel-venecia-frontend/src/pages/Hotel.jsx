import { useState } from 'react'
import { useHabitaciones } from '../hooks/useHabitaciones'
import HabitacionCard from '../components/hotel/HabitacionCard'
import ModalCheckIn from '../components/hotel/ModalCheckIn'
import Spinner from '../components/ui/Spinner'

export default function Hotel() {
  const { habitaciones, isLoading, refetch } = useHabitaciones()
  const [selectedHab, setSelectedHab] = useState(null)
  const [showCheckIn, setShowCheckIn] = useState(false)

  // Función para manejar el clic de forma segura
  const handleRoomClick = (hab) => {
    console.log("Datos de habitación seleccionada:", hab); // Para depurar en F12
    setSelectedHab(hab);
    setShowCheckIn(true); // Abrimos siempre; la lógica de si puede o no hacer check-in la manejará el Modal/Drawer
  };

  if (isLoading) return (
    <div className="flex h-screen items-center justify-center">
      <Spinner />
    </div>
  )

  return (
    <div className="p-6 bg-slate-50 min-h-screen">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-slate-800">Mapa de Habitaciones</h2>
        <p className="text-sm text-slate-500">Selecciona una habitación para ver detalles o registrar ingreso</p>
      </div>
      
      {/* Grid responsivo: 2 columnas en móvil, hasta 6 en pantallas grandes */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
        {habitaciones && habitaciones.length > 0 ? (
          habitaciones.map(hab => (
            <HabitacionCard 
              key={hab.id} 
              habitacion={hab} 
              onClick={handleRoomClick} 
            />
          ))
        ) : (
          <div className="col-span-full p-10 text-center bg-white rounded-xl border-2 border-dashed border-slate-200 text-slate-400">
            No se encontraron habitaciones configuradas.
          </div>
        )}
      </div>

      {/* Renderizado condicional del Panel/Modal */}
      {showCheckIn && selectedHab && (
        <ModalCheckIn 
          habitacion={selectedHab} 
          onClose={() => {
            console.log("Cerrando panel");
            setShowCheckIn(false);
            setSelectedHab(null);
          }}
          onSuccess={() => {
            console.log("Check-in exitoso, refrescando mapa...");
            setShowCheckIn(false);
            setSelectedHab(null);
            refetch();
          }}
        />
      )}
    </div>
  )
}