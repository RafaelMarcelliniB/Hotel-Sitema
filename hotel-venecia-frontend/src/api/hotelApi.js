import api from './axiosConfig'

export async function getHabitaciones() {
  const { data } = await api.get('/hotel/habitaciones/')
  return data
}

export async function getHuespedes() {
  const { data } = await api.get('/hotel/huespedes/')
  return data
}
