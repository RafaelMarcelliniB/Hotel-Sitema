import { useState } from 'react'
import { useHabitaciones } from '../hooks/useHabitaciones'
import HabitacionCard from '../components/hotel/HabitacionCard'
import ModalCheckIn from '../components/hotel/ModalCheckIn'
import ModalCheckOut from '../components/hotel/ModalCheckOut' 
import ModalProcesarReserva from '../components/reservas/ModalProcesarReserva'
import Spinner from '../components/ui/Spinner'
import api from '../api/axiosConfig' 

export default function Hotel() {
  const { habitaciones, isLoading, refetch } = useHabitaciones()
  const [selectedHab, setSelectedHab] = useState(null)
  const [showCheckIn, setShowCheckIn] = useState(false)
  const [showCheckOut, setShowCheckOut] = useState(false) 
  const [showProcesarReserva, setShowProcesarReserva] = useState(false)
  const [checkInInitialData, setCheckInInitialData] = useState(null)

  // Nueva función para consumir el endpoint de limpieza que tienes en Django
  const handleTerminarLimpieza = async (habitacionId, numeroHabitacion) => {
    const confirmar = window.confirm(
      `¿Confirmas que la Habitación #${numeroHabitacion} ya está limpia y lista para volver a estar disponible?`
    );
    
    if (confirmar) {
      try {
        // Ejecuta un POST a la ruta que configuraste en tu urls.py
        await api.post(`/hotel/habitaciones/${habitacionId}/limpiar/`);
        alert(`¡Habitación #${numeroHabitacion} marcada como LIMPIA con éxito!`);
        refetch(); // Refresca automáticamente el mapa para que vuelva a salir verde
      } catch (error) {
        console.error("Error al limpiar la habitación:", error);
        alert("Ocurrió un error al intentar actualizar el estado de limpieza.");
      }
    }
  };

  const handleRoomClick = (hab) => {
    console.log("Datos de habitación seleccionada:", hab);

    // 1. PRIMERA VALIDACIÓN: Si está OCUPADA, se abre el Check-Out obligatoriamente
    if (hab.estado_ocupacion === 'OCUPADO' || hab.estado === 'OCUPADO') {
      setSelectedHab(hab);
      setShowCheckOut(true);
      setShowCheckIn(false);
      setShowProcesarReserva(false);
    } 
    // 2. SEGUNDA VALIDACIÓN: Si NO está ocupada pero está SUCIA, se dispara la limpieza
    else if (hab.estado_limpieza === 'SUCIO') {
      handleTerminarLimpieza(hab.id, hab.numero);
    } 
    // 2.5 Si está RESERVADO, abrimos modal para procesar check-in desde la reserva
    else if (hab.estado_ocupacion === 'RESERVADO') {
      setSelectedHab(hab);
      setShowProcesarReserva(true);
      setShowCheckIn(false);
      setShowCheckOut(false);
    }
    // 3. TERCERA OPCIÓN: Si está limpia y libre, se abre el Check-In para alquilarla
    else {
      setSelectedHab(hab);
      setShowCheckIn(true);
      setShowCheckOut(false);
    }
  };

  const handleCloseModals = () => {
    setShowCheckIn(false);
    setShowCheckOut(false);
    setSelectedHab(null);
    setCheckInInitialData(null)
  };

  const handleSuccess = () => {
    handleCloseModals();
    refetch(); // Refresca el mapa para ver los cambios de colores
  };

  const handleProcesarSuccess = () => {
    setShowProcesarReserva(false)
    setSelectedHab(null)
    refetch()
  }

  const handleOpenCheckInFromReserva = (payload) => {
    // payload expected: { habitacion, cliente_nombre, cliente_apellido, cliente_dni, cliente_telefono, monto_adelanto, garantia, habitacion_id }
    setSelectedHab(payload.habitacion || selectedHab)
    setCheckInInitialData({
      huesped: {
        nombre: payload.cliente_nombre || '',
        apellido: payload.cliente_apellido || '',
        dni_pasaporte: payload.cliente_dni || '',
        telefono: payload.cliente_telefono || ''
      },
      monto_pagado: payload.monto_adelanto ?? payload.garantia ?? 0,
      garantia: payload.garantia ?? 0
    })
    setShowProcesarReserva(false)
    setShowCheckIn(true)
  }

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
          initialData={checkInInitialData}
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

      {showProcesarReserva && selectedHab && (
        <ModalProcesarReserva
          habitacion={selectedHab}
          isOpen={showProcesarReserva}
          onClose={() => setShowProcesarReserva(false)}
          onSuccess={handleProcesarSuccess}
          onOpenCheckIn={handleOpenCheckInFromReserva}
        />
      )}
    </div>
  )
}