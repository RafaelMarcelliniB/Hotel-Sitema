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
      queryClient.invalidateQueries(['habitaciones'])
      queryClient.invalidateQueries(['dashboard-metrics']) // Actualiza contadores del Dashboard
    }
  })

  return {
    ...query,
    habitaciones: query.data || [],
    cambiarEstado: mutation.mutateAsync, // Cambiado a mutateAsync para mayor control
    isUpdating: mutation.isLoading
  }
}