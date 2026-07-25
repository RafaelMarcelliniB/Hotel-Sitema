import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getDisponibles, crearReserva, getReservasVencidas, getReservasPorHabitacion } from '../api/reservaApi'

export function useDisponibles() {
  return useQuery({
    queryKey: ['habitaciones-disponibles'],
    queryFn: getDisponibles,
    refetchInterval: 15000,
  })
}

export function useCrearReserva() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: crearReserva,
    onSuccess: () => {
      qc.invalidateQueries(['habitaciones-disponibles'])
      qc.invalidateQueries(['dashboard-metrics'])
    }
  })
}

export function useVencidas() {
  return useQuery({
    queryKey: ['reservas-vencidas'],
    queryFn: getReservasVencidas,
    enabled: false,
  })
}

export function useReservasPorHabitacion(habitacionId) {
  return useQuery({
    queryKey: ['reservas-habitacion', habitacionId],
    queryFn: () => getReservasPorHabitacion(habitacionId),
    enabled: !!habitacionId && habitacionId !== 'undefined',
  })
}
