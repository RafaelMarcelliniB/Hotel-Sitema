import { useState } from 'react'
import { useHabitaciones } from '../hooks/useHabitaciones'
import HabitacionCard from '../components/hotel/HabitacionCard'
import ModalCheckIn from '../components/hotel/ModalCheckIn'
import Spinner from '../components/ui/Spinner'

export default function Hotel() {
  const { habitaciones, isLoading, refetch } = useHabitaciones()
  const [selectedHab, setSelectedHab] = useState(null)
  const [showCheckIn, setShowCheckIn] = useState(false)

  if (isLoading) return <Spinner />

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">Mapa de Habitaciones</h2>
      
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        {habitaciones.map(hab => (
          <HabitacionCard 
            key={hab.id} 
            habitacion={hab} 
            onClick={(h) => {
              setSelectedHab(h)
              if(h.estado_ocupacion === 'disponible') setShowCheckIn(true)
            }} 
          />
        ))}
      </div>

      {showCheckIn && selectedHab && (
        <ModalCheckIn 
          habitacion={selectedHab} 
          onClose={() => setShowCheckIn(false)}
          onSuccess={refetch}
        />
      )}
    </div>
  )
}