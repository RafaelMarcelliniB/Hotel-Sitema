import api from './axiosConfig'

export async function getRecados() {
  const { data } = await api.get('/recados/')
  return data
}
