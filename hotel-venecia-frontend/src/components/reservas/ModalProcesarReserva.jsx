import { useState } from 'react'
import { useReservasPorHabitacion } from '../../hooks/useReservas'

const splitNombreCompleto = (valor) => {
  const raw = String(valor || '').trim()
  if (!raw) return { nombre: '', apellido: '' }
  const partes = raw.split(/\s+/)
  if (partes.length === 1) return { nombre: partes[0], apellido: '' }
  return {
    nombre: partes[0],
    apellido: partes.slice(1).join(' '),
  }
}

export default function ModalProcesarReserva({ habitacion, isOpen, onClose, onOpenCheckIn }) {
  // Extraer el id de la habitación de forma defensiva: puede venir como objeto o como campos distintos
  const habitacionId = habitacion ? (habitacion.id ?? habitacion.habitacion_id ?? habitacion.numero) : null
  const { data: reservas = [], isLoading, isError } = useReservasPorHabitacion(habitacionId)
  const [processingId, setProcessingId] = useState(null)

  if (!isOpen) return null

  const handleProcesar = (reserva) => {
    if (!window.confirm(`Abrir formulario de Check-in para ${reserva.huesped?.nombre || 'Huésped'} en Hab ${habitacion.numero}?`)) return
    setProcessingId(reserva.id)
    const nombreBase = reserva.huesped?.nombre || reserva.huesped || ''
    const { nombre, apellido } = splitNombreCompleto(nombreBase)
    const initialPayload = {
      // incluir el id de la reserva para que el modal de CheckIn pueda enviar `reserva_id`
      id: reserva.id,
      habitacion: habitacion,
      cliente_nombre: nombreBase,
      cliente_apellido: reserva.huesped?.apellido || apellido || '',
      cliente_dni: reserva.huesped?.dni_pasaporte || reserva.dni || reserva.documento || '',
      // Mapear el teléfono siguiendo la estructura flexible solicitada
      cliente_telefono: reserva.cliente_telefono || reserva.telefono || reserva.celular || (reserva.cliente && reserva.cliente.celular) || (reserva.cliente && reserva.cliente.telefono) || '',
      monto_adelanto: reserva.monto_adelanto ?? reserva.monto_garantia ?? reserva.monto_pagado ?? 20.00,
      garantia: reserva.monto_garantia ?? 20.00,
      tipo_pago: reserva.tipo_pago_adelanto || 'EFECTIVO',
      habitacion_id: habitacion?.id ?? habitacion?.habitacion_id,
      huesped: {
        nombre,
        apellido: reserva.huesped?.apellido || apellido || '',
      }
    }

    // Llamar al handler proporcionado por la página principal para abrir el modal de Check-in
    if (typeof onOpenCheckIn === 'function') {
      onOpenCheckIn(initialPayload)
    }

    // Cerrar este modal
    onClose && onClose()
    setProcessingId(null)
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
          <div className="space-y-4 p-6 text-center">
            <div className="text-slate-500">No hay reservas asociadas a esta habitación.</div>
            <button
              type="button"
              onClick={() => {
                if (typeof onOpenCheckIn === 'function') {
                  onOpenCheckIn({
                    habitacion,
                    cliente_nombre: '',
                    cliente_apellido: '',
                    cliente_dni: '',
                    cliente_telefono: '',
                    monto_adelanto: 0,
                    garantia: 0,
                    tipo_pago: 'EFECTIVO',
                    habitacion_id: habitacion?.id ?? habitacion?.habitacion_id,
                  })
                }
                onClose && onClose()
              }}
              className="px-4 py-2 rounded bg-emerald-600 text-white font-medium"
            >
              Completar Check-in directo
            </button>
          </div>
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
