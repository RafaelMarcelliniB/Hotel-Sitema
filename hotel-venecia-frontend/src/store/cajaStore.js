import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api from '../api/axiosConfig'

export const useCajaStore = create(
  persist(
    (set) => ({
      cajaActiva: null,
      turnoActivo: null,
      loading: false,
      
      // Acción para obtener la caja abierta desde la API
      fetchCajaActiva: async () => {
        set({ loading: true })
        try {
          const { data } = await api.get('/caja/resumen/')
          set({ cajaActiva: data, turnoActivo: data.turno, loading: false })
        } catch (error) {
          set({ cajaActiva: null, loading: false })
        }
      },

      setCajaActiva: (cajaActiva) => set({ cajaActiva }),
      setTurnoActivo: (turnoActivo) => set({ turnoActivo }),
      clearCaja: () => set({ cajaActiva: null, turnoActivo: null }),
    }),
    { name: 'hotel_caja_store' },
  ),
)