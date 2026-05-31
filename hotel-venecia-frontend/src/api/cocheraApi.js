import api from './axiosConfig'

export async function getEspacios() {
  const { data } = await api.get('/cochera/espacios/')
  return data
}
