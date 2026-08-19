import { useState } from 'react'
import { useHabitaciones } from '../hooks/useHabitaciones'
import HabitacionCard from '../components/hotel/HabitacionCard'
import ModalCheckIn from '../components/hotel/ModalCheckIn'
import ModalCheckOut from '../components/hotel/ModalCheckOut' 
import ModalProcesarReserva from '../components/reservas/ModalProcesarReserva'
import Spinner from '../components/ui/Spinner'
import api from '../api/axiosConfig' 

export default function Hotel() {
  const { habitaciones, isLoading, refetch, cambiarEstado } = useHabitaciones()
  const [selectedHab, setSelectedHab] = useState(null)
  const [pisoSeleccionado, setPisoSeleccionado] = useState('TODOS')
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

  const handleRequestMaintenance = async (hab) => {
    const enMantenimiento = hab.estado_ocupacion === 'MANTENIMIENTO';
    const accion = enMantenimiento ? 'habilitar' : 'enviar a mantenimiento';
    if (!window.confirm(`¿Confirmas ${accion} la Habitación #${hab.numero}?`)) return;

    try {
      await cambiarEstado({
        id: hab.id,
        estado_ocupacion: enMantenimiento ? 'DISPONIBLE' : 'MANTENIMIENTO',
        estado_limpieza: hab.estado_limpieza
      });
      refetch();
    } catch (error) {
      console.error('Error al actualizar el mantenimiento:', error);
      alert('No se pudo actualizar el estado de mantenimiento.');
    }
  };

  const handleRoomClick = (hab) => {
    console.log("Datos de habitación seleccionada:", hab);

    if (hab.estado_ocupacion === 'MANTENIMIENTO') return;

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

  const pisos = [...new Set((habitaciones || []).map((habitacion) => habitacion.piso))]
    .sort((a, b) => a - b)
  const habitacionesVisibles = (habitaciones || []).filter(
    (habitacion) => pisoSeleccionado === 'TODOS' || String(habitacion.piso) === String(pisoSeleccionado)
  )

  return (
    <div className="p-6 bg-slate-50 min-h-screen">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-slate-800">Mapa de Habitaciones</h2>
        <p className="text-sm text-slate-500">Selecciona una habitación disponible para ingreso o una ocupada para salida</p>
      </div>
      
      <div className="mb-6 flex flex-wrap gap-2" role="tablist" aria-label="Filtrar habitaciones por piso">
        {['TODOS', ...pisos].map((piso) => (
          <button
            key={piso}
            type="button"
            role="tab"
            aria-selected={pisoSeleccionado === piso}
            onClick={() => setPisoSeleccionado(piso)}
            className={`rounded-lg border px-4 py-2 text-sm font-bold transition-colors ${
              pisoSeleccionado === piso
                ? 'border-slate-800 bg-slate-800 text-white'
                : 'border-slate-200 bg-white text-slate-600 hover:border-slate-400'
            }`}
          >
            {piso === 'TODOS' ? 'Todos' : `Piso ${piso}`}
          </button>
        ))}
      </div>

      {pisos.length > 0 && (pisoSeleccionado === 'TODOS' ? pisos : [pisoSeleccionado]).map((piso) => (
        <section key={piso} className="mb-8" aria-labelledby={`piso-${piso}`}>
          <h3 id={`piso-${piso}`} className="mb-3 text-sm font-black uppercase tracking-wider text-slate-500">
            Piso {piso}
          </h3>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6">
            {habitacionesVisibles.filter((habitacion) => habitacion.piso === piso).map((hab) => (
              <HabitacionCard
                key={hab.id}
                habitacion={hab}
                onClick={handleRoomClick}
                onRequestMaintenance={handleRequestMaintenance}
              />
            ))}
          </div>
        </section>
      ))}

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