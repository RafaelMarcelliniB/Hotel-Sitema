import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useCajaStore = create(
  persist(
    (set) => ({
      cajaActiva: null,
      turnoActivo: null,
      setCajaActiva: (cajaActiva) => set({ cajaActiva }),
      setTurnoActivo: (turnoActivo) => set({ turnoActivo }),
      clearCaja: () => set({ cajaActiva: null, turnoActivo: null }),
    }),
    { name: 'hotel_caja_store' },
  ),
)
