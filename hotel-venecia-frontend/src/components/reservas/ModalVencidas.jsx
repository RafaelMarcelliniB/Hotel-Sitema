import React, { useState } from 'react'

export default function ModalVencidas({ isOpen, onClose, reservas = [], loading = false, error = null }) {
  if (!isOpen) return null

  const [expandedId, setExpandedId] = useState(null)

  const formatPhone = (tel) => {
    if (!tel) return ''
    return tel.replace(/[^0-9]/g, '')
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black/40" onClick={onClose} />
      <div className="relative z-50 w-full max-w-2xl bg-white p-6 rounded-lg">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold">Devolución / Reembolsos PENDIENTES</h3>
          <button onClick={onClose} className="text-slate-500">Cerrar</button>
        </div>

        {loading && <div className="p-6 text-center">Cargando reservas...</div>}
        {error && <div className="p-4 text-red-500">Ocurrió un error al cargar las reservas.</div>}

        {!loading && reservas.length === 0 && (
          <div className="p-6 text-center text-slate-500">No hay reservas vencidas por procesar.</div>
        )}

        {!loading && reservas.length > 0 && (
          <div className="space-y-3">
            {reservas.map((r) => {
              const isOpen = expandedId === r.id
              return (
                <div key={r.id} className="border rounded">
                  <div className={`flex items-center justify-between p-3 cursor-pointer ${isOpen ? 'bg-slate-50' : ''}`} onClick={() => setExpandedId(isOpen ? null : r.id)}>
                    <div>
                      <div className="font-semibold">{r.huesped?.nombre || r.huesped || 'Huésped'}</div>
                      <div className="text-sm text-slate-600">Hab: {r.habitacion_preferida || (r.habitacion_preferida_numero) || '—'}</div>
                      <div className="text-sm text-slate-500">{r.created_at || `${r.fecha_llegada_estimada} ${r.hora_llegada_estimada || ''}`}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-slate-800">S/ {Number(r.monto_garantia || 20).toFixed(2)}</div>
                      <div className="mt-2">
                        {r.huesped?.telefono || r.telefono ? (
                          <a className="text-sm text-amber-600 hover:underline" href={`https://wa.me/51${formatPhone(r.huesped?.telefono || r.telefono)}`} target="_blank" rel="noreferrer">WhatsApp</a>
                        ) : (
                          <span className="text-sm text-slate-400">Sin teléfono</span>
                        )}
                      </div>
                    </div>
                  </div>

                  {isOpen && (
                    <div className="p-4 bg-white">
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div>
                          <div className="text-xs text-slate-500">Nombre completo</div>
                          <div className="font-medium">{[r.huesped?.nombre, r.huesped?.apellido].filter(Boolean).join(' ') || r.huesped || '—'}</div>
                        </div>
                        <div>
                          <div className="text-xs text-slate-500">DNI / Pasaporte</div>
                          <div className="font-medium">{r.huesped?.dni_pasaporte || r.huesped?.dni || r.dni_pasaporte || '—'}</div>
                        </div>
                        <div>
                          <div className="text-xs text-slate-500">Teléfono</div>
                          <div className="font-medium">{r.huesped?.telefono || r.telefono || '—'}</div>
                        </div>
                        <div>
                          <div className="text-xs text-slate-500">Fecha / Hora creación</div>
                          <div className="font-medium">{r.created_at || `${r.fecha_llegada_estimada || '—'} ${r.hora_llegada_estimada || ''}`}</div>
                        </div>
                        <div>
                          <div className="text-xs text-slate-500">Estado</div>
                          <div className="font-medium">{r.estado || r.estado_reserva || '—'}</div>
                        </div>
                        <div>
                          <div className="text-xs text-slate-500">Monto garantía</div>
                          <div className="font-medium">S/ {Number(r.monto_garantia || 0).toFixed(2)}</div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
