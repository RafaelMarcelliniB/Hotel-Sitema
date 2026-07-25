import { useState } from 'react'
import { useCrearReserva } from '../../hooks/useReservas'

export default function ModalReserva({ habitacion, onClose, onSuccess }) {
  const [nombre, setNombre] = useState('')
  const [dni, setDni] = useState('')
  const [telefono, setTelefono] = useState('')
  const crear = useCrearReserva()

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await crear.mutateAsync({
        huesped: { nombre: nombre, apellido: '', dni_pasaporte: dni, telefono },
        habitacion_preferida: habitacion.id,
        fecha_llegada_estimada: new Date().toISOString().slice(0,10),
        hora_llegada_estimada: new Date().toLocaleTimeString('en-GB').slice(0,5),
        tipo_pago_adelanto: 'EFECTIVO',
        monto_garantia: 20.00,
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
          <div className="flex items-center justify-between">
            <div>S/ 20.00 (Garantía)</div>
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
