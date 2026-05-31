import api from './axiosConfig'

export async function getCajas() {
  const { data } = await api.get('/caja/cajas/')
  return data
}
