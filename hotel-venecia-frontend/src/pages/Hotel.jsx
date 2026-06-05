import { useState } from 'react'
import { useHabitaciones } from '../hooks/useHabitaciones'
import HabitacionCard from '../components/hotel/HabitacionCard'
import ModalCheckIn from '../components/hotel/ModalCheckIn'
import ModalCheckOut from '../components/hotel/ModalCheckOut' 
import Spinner from '../components/ui/Spinner'

export default function Hotel() {
  const { habitaciones, isLoading, refetch } = useHabitaciones()
  const [selectedHab, setSelectedHab] = useState(null)
  const [showCheckIn, setShowCheckIn] = useState(false)
  const [showCheckOut, setShowCheckOut] = useState(false) 

  const handleRoomClick = (hab) => {
    console.log("Datos de habitación seleccionada:", hab);
    setSelectedHab(hab);

    // Comparamos con el estado que viene de tu base de datos
    // En tu imagen se ve "OCUPADO", así que validamos esa cadena
    if (hab.estado_ocupacion === 'OCUPADO' || hab.estado === 'OCUPADO') {
      setShowCheckOut(true);
      setShowCheckIn(false);
    } else {
      setShowCheckIn(true);
      setShowCheckOut(false);
    }
  };

  const handleCloseModals = () => {
    setShowCheckIn(false);
    setShowCheckOut(false);
    setSelectedHab(null);
  };

  const handleSuccess = () => {
    handleCloseModals();
    refetch(); // Refresca el mapa para ver los cambios de colores
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
        <p className="text-sm text-slate-500">Selecciona una habitación disponible para ingreso o una ocupada para salida</p>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
        {habitaciones?.map(hab => (
          <HabitacionCard 
            key={hab.id} 
            habitacion={hab} 
            onClick={handleRoomClick} 
          />
        ))}
      </div>

      {/* Modal para Registro (Entrada) */}
      {showCheckIn && selectedHab && (
        <ModalCheckIn 
          habitacion={selectedHab} 
          onClose={handleCloseModals}
          onSuccess={handleSuccess}
        />
      )}

      {/* Modal para Check-Out (Salida) */}
      {showCheckOut && selectedHab && (
        <ModalCheckOut 
          habitacion={selectedHab} 
          onClose={handleCloseModals}
          onSuccess={handleSuccess}
        />
      )}
    </div>
  )
}