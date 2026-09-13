import api from './axiosConfig'

export async function login({ username, password }) {
  try {
    const { data } = await api.post('/users/auth/login/', { username, password })
    return data
  } catch (error) {
    if (!error.response) {
      throw new Error('No se pudo conectar con el servidor. Inicia el backend Django en el puerto 8000.')
    }
    const detail = error?.response?.data?.detail || 'Credenciales inválidas'
    throw new Error(detail)
  }
}

// Nuevas funciones para el CRUD de trabajadores
export async function getTrabajadores() {
  const { data } = await api.get('/users/trabajadores/')
  return data
}

export async function registrarTrabajador(userData) {
  const { data } = await api.post('/users/trabajadores/', userData)
  return data
}

export async function actualizarTrabajador(id, userData) {
  const { data } = await api.patch(`/users/trabajadores/${id}/`, userData)
  return data
}