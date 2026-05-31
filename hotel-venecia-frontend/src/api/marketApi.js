import api from './axiosConfig'

export async function getProductos() {
  const { data } = await api.get('/market/productos/')
  return data
}
