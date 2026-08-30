import React, { useState } from 'react'
import { useEffect } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { useEspacios } from '../../hooks/useEspacios'
import api from '../../api/axiosConfig'

export default function ModalSalidaCochera({ espacio, onClose }) {
  const { registrarSalida } = useEspacios()
  const [loading, setLoading] = useState(false)
  const [monto, setMonto] = useState(null)
  const [fetching, setFetching] = useState(false)
  const [metodoPago, setMetodoPago] = useState('EFECTIVO')

  const esHuesped = String(espacio?.vehiculo_actual?.tipo_cliente || '').toUpperCase() === 'HUESPED'

  useEffect(() => {
    const registroId = espacio?.vehiculo_actual?.id
    if (!registroId) return
    setFetching(true)
    api.get(`/cochera/vehiculos/${registroId}/salida/`)
      .then(res => {
        const valor = esHuesped ? 0 : (res.data.monto_calculado ?? null)
        setMonto(valor)
      })
      .catch(err => {
        console.error('Error al obtener monto calculado:', err)
      })
      .finally(() => setFetching(false))
  }, [espacio, esHuesped])

  const handleConfirmarSalida = async () => {
    // CORREGIDO: Buscamos el ID del registro de forma inteligente
    const registroId = espacio?.vehiculo_actual?.id || espacio?.id 

    if (!registroId) {
      alert("Error: No se pudo determinar el ID del registro para procesar la salida.")
      return
    }

    // Si el vehículo está registrado como HUESPED no permitimos procesar la salida
    const tipoCliente = espacio?.vehiculo_actual?.tipo_cliente
    if (tipoCliente === 'HUESPED') {
      alert('Este vehículo está registrado como HUÉSPED. La salida solo puede procesarse cuando se realice el Check-out del huésped.')
      return
    }

    try {
      setLoading(true)
        // Ejecutamos la mutación directa enviando el método de pago seleccionado
        await registrarSalida({ registroId, metodo_pago: metodoPago })
        // Cerramos el modal inmediatamente sin esperar interacción del usuario
        onClose()
        // Notificación no bloqueante: usamos alert como fallback
        try { alert("Salida de cochera procesada correctamente. Espacio liberado.") } catch (e) {}
    } catch (err) {
      console.error("Error al procesar salida:", err)
      const errorMsg = err.response?.data?.error || "Error al procesar la salida del vehículo."
      alert(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal open={true} onClose={onClose} title={`Procesar Salida - Espacio #${espacio?.numero}`}>
      <div className="space-y-4 p-1">
        
        <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 space-y-2">
          <span className="text-[10px] font-black text-slate-400 uppercase block">Información de Cochera</span>
          <div className="grid grid-cols-2 gap-3 text-slate-700">
            <div>
              <p className="text-[11px] text-slate-400">Espacio Nro:</p>
              <p className="text-sm font-bold text-slate-900 bg-amber-100 px-2 py-0.5 rounded inline-block">
                #{espacio?.numero || 'N/A'}
              </p>
            </div>
            <div>
              <p className="text-[11px] text-slate-400">Tipo permitido:</p>
              <p className="text-sm font-semibold text-slate-800 uppercase">{espacio?.tipo || 'General'}</p>
            </div>
            {/* Mostrar resumen del vehículo (si existe) */}
            <div>
              <p className="text-[11px] text-slate-400">Cliente:</p>
              <p className="text-sm font-semibold text-slate-800 uppercase">{espacio?.vehiculo_actual?.tipo_cliente === 'HUESPED' ? 'Huésped' : (espacio?.vehiculo_actual?.tipo_cliente || 'N/A')}</p>
            </div>
          </div>
        </div>

        <p className="text-xs text-slate-500 text-center px-2">
          ¿Está seguro de liquidar este espacio? El sistema detendrá el contador de tiempo, calculará el monto acumulado, generará el movimiento en caja y liberará el casillero.
        </p>

        <div className="bg-white p-3 rounded border">
          <p className="text-sm text-slate-600">{esHuesped ? 'Cobro por cortesía:' : 'Monto estimado a cobrar:'}</p>
          <p className="text-2xl font-bold text-slate-900">{esHuesped ? 'S/ 0.00 (Cortesia)' : `S/ ${fetching ? 'Calculando...' : (monto !== null ? Number(monto).toFixed(2) : '0.00')}`}</p>
        </div>

        {!esHuesped && (
          <div>
            <label className="block text-xs font-bold text-slate-600 uppercase mb-1">Método de Pago</label>
            <select value={metodoPago} onChange={(e) => setMetodoPago(e.target.value)} className="w-full rounded-xl border border-slate-200 px-3 py-2">
              <option value="EFECTIVO">Efectivo</option>
              <option value="YAPE">Yape / Plin</option>
              <option value="TARJETA">Tarjeta</option>
            </select>
          </div>
        )}
        <div className="flex gap-2 justify-end pt-4 border-t border-slate-100">
          <Button type="button" variant="ghost" onClick={onClose} disabled={loading}>
            Cancelar
          </Button>
          <Button 
            type="button" 
            onClick={handleConfirmarSalida} 
            disabled={loading}
            className="bg-rose-600 hover:bg-rose-700 text-white font-bold"
          >
            {loading ? 'Procesando...' : 'Confirmar Salida'}
          </Button>
        </div>

      </div>
    </Modal>
  )
}