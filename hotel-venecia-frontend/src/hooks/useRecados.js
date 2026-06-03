import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getRecados } from '../api/recadosApi'
import api from '../api/axiosConfig'

export function useRecados() {
  const queryClient = useQueryClient()

  const query = useQuery({
    queryKey: ['recados'],
    queryFn: getRecados,
    refetchInterval: 60000 // Se actualiza cada minuto para ver recados nuevos
  })

  const crearRecado = useMutation({
    mutationFn: async (nuevoRecado) => {
      const { data } = await api.post('/recados/', nuevoRecado)
      return data
    },
    onSuccess: () => queryClient.invalidateQueries(['recados'])
  })

  const marcarLeido = useMutation({
    mutationFn: async (id) => {
      const { data } = await api.patch(`/recados/${id}/leer/`)
      return data
    },
    onSuccess: () => queryClient.invalidateQueries(['recados'])
  })

  return {
    ...query,
    recados: query.data || [],
    crearRecado: crearRecado.mutateAsync,
    marcarLeido: marcarLeido.mutateAsync
  }
}