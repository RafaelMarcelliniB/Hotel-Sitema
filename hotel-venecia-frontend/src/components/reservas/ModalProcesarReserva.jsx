import React, { useState } from 'react'
import { useReservasPorHabitacion } from '../../hooks/useReservas'

export default function ModalProcesarReserva({ habitacion, isOpen, onClose, onSuccess, onOpenCheckIn }) {
  // Extraer el id de la habitación de forma defensiva: puede venir como objeto o como campos distintos
  const habitacionId = habitacion ? (habitacion.id ?? habitacion.habitacion_id ?? habitacion.numero) : null
  const { data: reservas = [], isLoading, isError, refetch } = useReservasPorHabitacion(habitacionId)
  const [processingId, setProcessingId] = useState(null)

  if (!isOpen) return null

  const handleProcesar = (reserva) => {
    if (!window.confirm(`Abrir formulario de Check-in para ${reserva.huesped?.nombre || 'Huésped'} en Hab ${habitacion.numero}?`)) return
    // Preparar datos para abrir el modal principal de Check-in (no ejecutar la API aquí)
    const initialPayload = {
      // incluir el id de la reserva para que el modal de CheckIn pueda enviar `reserva_id`
      id: reserva.id,
      habitacion: habitacion,
      cliente_nombre: reserva.huesped?.nombre || reserva.huesped || '',
      cliente_apellido: reserva.huesped?.apellido || '',
      cliente_dni: reserva.huesped?.dni_pasaporte || reserva.dni || reserva.documento || '',
      // Mapear el teléfono siguiendo la estructura flexible solicitada
      cliente_telefono: reserva.cliente_telefono || reserva.telefono || reserva.celular || (reserva.cliente && reserva.cliente.celular) || (reserva.cliente && reserva.cliente.telefono) || '',
      monto_adelanto: reserva.monto_pagado ?? reserva.precio_pagado ?? 20.00,
      garantia: 20.00,
      habitacion_id: habitacion?.id ?? habitacion?.habitacion_id
    }

    // Llamar al handler proporcionado por la página principal para abrir el modal de Check-in
    if (typeof onOpenCheckIn === 'function') {
      onOpenCheckIn(initialPayload)
    }

    // Cerrar este modal
    onClose && onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black/40" onClick={onClose} />
      <div className="relative z-50 w-full max-w-xl bg-white p-6 rounded-lg">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold">Procesar Check-in (Reserva)</h3>
          <button onClick={onClose} className="text-slate-500">Cerrar</button>
        </div>

        {isLoading && <div className="p-6 text-center">Cargando reservas vinculadas...</div>}
        {isError && <div className="p-4 text-red-500">No se pudo cargar las reservas para esta habitación.</div>}

        {!isLoading && reservas.length === 0 && (
          <div className="p-6 text-center text-slate-500">No hay reservas asociadas a esta habitación.</div>
        )}

        {!isLoading && reservas.length > 0 && (
          <div className="space-y-3">
            {reservas.map(r => (
              <div key={r.id} className="flex items-center justify-between p-3 border rounded">
                <div>
                  <div className="font-semibold">{r.huesped?.nombre || r.huesped || 'Huésped'}</div>
                  <div className="text-sm text-slate-600">Fecha: {r.fecha_llegada_estimada} {r.hora_llegada_estimada || ''}</div>
                </div>
                <div className="flex items-center gap-2">
                  <button disabled={processingId === r.id} onClick={() => handleProcesar(r)} className="px-3 py-1 rounded bg-green-600 text-white">Procesar Check-in</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      {/* No renderizamos el modal de CheckIn localmente aquí: delegamos su apertura al padre vía onOpenCheckIn */}
    </div>
  )
}
