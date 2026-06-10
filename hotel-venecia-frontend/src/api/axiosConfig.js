import axios from 'axios'

function getStoredToken() {
  const raw = localStorage.getItem('hotel_auth_store')
  if (raw) {
    try {
      const parsed = JSON.parse(raw)
      // Buscamos dentro de la estructura de estado de Zustand o el fallback directo
      return parsed?.state?.token || parsed?.token || null
    } catch (e) {
      console.error("Error al parsear el token de Zustand:", e)
      return null
    }
  }
  return localStorage.getItem('hotel_token')
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// INTERCEPTOR CORREGIDO: Fuerza la lectura fresca del token en cada request
api.interceptors.request.use(
  (config) => {
    const token = getStoredToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    } else {
      // Limpieza preventiva si no hay token activo
      delete config.headers.Authorization
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor de respuestas: si la API responde 401 avisamos y redirigimos al login
api.interceptors.response.use(
  (resp) => resp,
  (error) => {
    const status = error.response?.status
    if (status === 401) {
      try {
        // Limpieza del token local y redirección a la pantalla de login
        localStorage.removeItem('hotel_auth_store')
        localStorage.removeItem('hotel_token')
      } catch (e) {}
      // Mostrar mensaje amigable
      alert('Sesión expirada o no autorizada. Por favor vuelve a iniciar sesión.')
      // Redirigir a la ruta raíz (ajusta si tu app usa otra ruta de login)
      window.location.href = '/'
    }
    return Promise.reject(error)
  }
)

export default api