import api from './axiosConfig'

export async function getDisponibles() {
  const { data } = await api.get('/hotel/habitaciones/')
  // Backend devuelve habitaciones con campo `estado_ocupacion` en MAYÚSCULAS.
  // Queremos únicamente DISPONIBLE y RESERVADO, ocultando OCUPADO.
  const filtered = (data || []).filter(h => h.estado_ocupacion === 'DISPONIBLE' || h.estado_ocupacion === 'RESERVADO')
  // Ordenar: primero DISPONIBLE, luego RESERVADO
  filtered.sort((a, b) => {
    const rank = (s) => s === 'DISPONIBLE' ? 0 : s === 'RESERVADO' ? 1 : 2
    return rank(a.estado_ocupacion) - rank(b.estado_ocupacion)
  })
  return filtered
}

export async function crearReserva(payload) {
  const { data } = await api.post('/hotel/reservas/', payload)
  return data
}

export async function getReservasVencidas() {
  const { data } = await api.get('/hotel/reservas/vencidas/')
  return data
}

export async function procesarCheckinReserva(id, payload) {
  const { data } = await api.post(`/hotel/reservas/${id}/checkin/`, payload)
  return data
}

export async function getReservasPorHabitacion(habitacionId) {
  // Aceptamos que nos pasen un objeto habitación o directamente un id.
  // Guard clause estricta: evitar llamadas con `undefined` como string o valores falsy
  if (!habitacionId || habitacionId === 'undefined') return []

  const id = typeof habitacionId === 'object'
    ? (habitacionId.id ?? habitacionId.habitacion_id ?? habitacionId.numero)
    : habitacionId

  if (!id || id === 'undefined') return []
  // Usar exclusivamente el endpoint de lista de reservas con filtro por habitación
  try {
    // Nota: algunos backends aceptan `habitacion` o `habitacion_id` como parámetro.
    const { data } = await api.get('/hotel/reservas/', { params: { habitacion: id, estado: 'PENDIENTE' } })
    const arr = Array.isArray(data) ? data : (data?.data || [])
    return arr.filter(r => !r.estado || r.estado === 'PENDIENTE')
  } catch (err) {
    console.error('Error fetching reservas por habitacion:', err)
    return []
  }
}
