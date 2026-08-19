import { useState } from 'react'
import { useCrearReserva } from '../../hooks/useReservas'

export default function ModalReserva({ habitacion, onClose, onSuccess }) {
  const [nombre, setNombre] = useState('')
  const [dni, setDni] = useState('')
  const [telefono, setTelefono] = useState('')
  const [fechaLlegada, setFechaLlegada] = useState(() => new Date().toISOString().slice(0, 10))
  const [horaLlegada, setHoraLlegada] = useState(() => new Date().toTimeString().slice(0, 5))
  const [montoGarantia, setMontoGarantia] = useState('20.00')
  const [metodoPago, setMetodoPago] = useState('EFECTIVO')
  const crear = useCrearReserva()

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await crear.mutateAsync({
        huesped: { nombre: nombre, apellido: '', dni_pasaporte: dni, telefono },
        habitacion_preferida: habitacion.id,
        fecha_llegada_estimada: fechaLlegada,
        hora_llegada_estimada: horaLlegada,
        tipo_pago_adelanto: metodoPago,
        monto_garantia: Number(montoGarantia),
        monto_adelanto: Number(montoGarantia),
      })
      onSuccess()
    } catch (err) {
      // Mostrar errores detallados del backend si existen
      const backend = err?.response?.data
      let message = ''
      if (backend) {
        if (backend.detail) message = backend.detail
        else if (typeof backend === 'string') message = backend
        else if (typeof backend === 'object') {
          // Convertir errores por campo a texto
          message = Object.entries(backend).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`).join('\n')
        }
      }
      alert('Error al crear la reserva:\n' + (message || err.message))
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black/40" onClick={onClose} />
      <div className="relative z-50 w-full max-w-md bg-white p-6 rounded-lg">
        <h3 className="text-lg font-bold mb-4">Reservar Habitación #{habitacion.numero}</h3>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="block text-sm">Nombre completo</label>
            <input value={nombre} onChange={e => setNombre(e.target.value)} required className="w-full border px-3 py-2 rounded" />
          </div>
          <div>
            <label className="block text-sm">DNI / Documento</label>
            <input value={dni} onChange={e => setDni(e.target.value)} required className="w-full border px-3 py-2 rounded" />
          </div>
          <div>
            <label className="block text-sm">Teléfono</label>
            <input value={telefono} onChange={e => setTelefono(e.target.value)} required className="w-full border px-3 py-2 rounded" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm">Llegada / Check-in *</label>
              <input type="date" value={fechaLlegada} onChange={e => setFechaLlegada(e.target.value)} required className="w-full border px-3 py-2 rounded" />
            </div>
            <div>
              <label className="block text-sm">Hora estimada *</label>
              <input type="time" value={horaLlegada} onChange={e => setHoraLlegada(e.target.value)} required className="w-full border px-3 py-2 rounded" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm">Garantía / Adelanto (S/) *</label>
              <input type="number" min="0" step="0.01" value={montoGarantia} onChange={e => setMontoGarantia(e.target.value)} required className="w-full border px-3 py-2 rounded" />
            </div>
            <div>
              <label className="block text-sm">Método de pago *</label>
              <select value={metodoPago} onChange={e => setMetodoPago(e.target.value)} required className="w-full border px-3 py-2 rounded">
                <option value="EFECTIVO">Efectivo</option>
                <option value="YAPE">Yape</option>
                <option value="PLIN">Plin</option>
                <option value="TRANSFERENCIA">Transferencia</option>
              </select>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <div>S/ {Number(montoGarantia || 0).toFixed(2)} (Garantía)</div>
            <div>
              <button type="button" className="mr-2 px-4 py-2 rounded bg-gray-200" onClick={onClose}>Cancelar</button>
              <button type="submit" className="px-4 py-2 rounded bg-primary text-white">Reservar</button>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}
