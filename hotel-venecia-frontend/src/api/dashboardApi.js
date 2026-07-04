import api from './axiosConfig'

export async function getDashboardMetrics() {
  const { data } = await api.get('/caja/dashboard/')
  return data
}

export async function getCajaResumen(params = {}) {
  const { data } = await api.get('/caja/resumen/', { params })
  return data
}
