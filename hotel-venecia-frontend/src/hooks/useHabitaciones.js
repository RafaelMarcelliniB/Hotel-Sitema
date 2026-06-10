import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getHabitaciones } from '../api/hotelApi'
import api from '../api/axiosConfig'

export function useHabitaciones() {
  const queryClient = useQueryClient()

  const query = useQuery({
    queryKey: ['habitaciones'],
    queryFn: getHabitaciones,
    refetchInterval: 15000 // Refresco automático cada 15 segundos
  })

  const mutation = useMutation({
    mutationFn: async ({ id, estado_ocupacion, estado_limpieza }) => {
      const { data } = await api.patch(`/hotel/habitaciones/${id}/estado/`, {
        estado_ocupacion,
        estado_limpieza
      })
      return data
    },
    onSuccess: () => {
      // Forzamos el refresco de los datos financieros del dashboard y de la caja abierta
      queryClient.invalidateQueries(['habitaciones'])
      queryClient.invalidateQueries(['dashboard-metrics'])
      queryClient.invalidateQueries(['caja-resumen'])
      queryClient.invalidateQueries(['cajas'])
    }
  })

  return {
    ...query,
    habitaciones: query.data || [],
    cambiarEstado: mutation.mutateAsync,
    isUpdating: mutation.isLoading
  }
}