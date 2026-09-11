import api from './axiosConfig'

export async function getEspacios() {
  const { data } = await api.get('/cochera/espacios/')
  return data
}

export async function crearEspacio(espacioData) {
  const { data } = await api.post('/cochera/espacios/', espacioData)
  return data
}
