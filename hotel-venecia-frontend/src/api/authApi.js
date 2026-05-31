import api from './axiosConfig'

export async function login({ username, password }) {
  try {
    const { data } = await api.post('/users/auth/login/', { username, password })
    return data
  } catch (error) {
    const detail = error?.response?.data?.detail || 'Credenciales inválidas'
    throw new Error(detail)
  }
}
