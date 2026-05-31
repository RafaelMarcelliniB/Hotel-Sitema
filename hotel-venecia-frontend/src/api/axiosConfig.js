import axios from 'axios'

function getStoredToken() {
  const raw = localStorage.getItem('hotel_auth_store')
  if (raw) {
    try {
      const parsed = JSON.parse(raw)
      return parsed?.state?.token || null
    } catch {
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

api.interceptors.request.use((config) => {
  const token = getStoredToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
