import api from './axiosConfig'

export async function getCajas() {
  const { data } = await api.get('/caja/cajas/')
  return data
}

// Nueva función para abrir la caja
export async function abrirCaja(payload) {
  const { data } = await api.post('/caja/apertura/', payload)
  return data
}