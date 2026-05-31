import api from './axiosConfig'

export async function getDashboardMetrics() {
  const { data } = await api.get('/dashboard/')
  return data
}
