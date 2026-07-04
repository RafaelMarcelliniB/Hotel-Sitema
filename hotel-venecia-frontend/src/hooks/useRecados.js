import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getRecados } from '../api/recadosApi'
import api from '../api/axiosConfig'

export function useRecados() {
  const queryClient = useQueryClient()

  const query = useQuery({
    queryKey: ['recados'],
    queryFn: getRecados,
    refetchInterval: 60000,
  })

  const crearRecado = useMutation({
    mutationFn: async (nuevoRecado) => {
      const { data } = await api.post('/recados/', nuevoRecado)
      return data
    },
    onSuccess: () => queryClient.invalidateQueries(['recados']),
  })

  const actualizarEstado = useMutation({
    mutationFn: async ({ id, estado }) => {
      const { data } = await api.patch(`/recados/${id}/`, { estado })
      return data
    },
    onSuccess: () => queryClient.invalidateQueries(['recados']),
  })

  const marcarLeido = useMutation({
    mutationFn: async (id) => {
      const { data } = await api.patch(`/recados/${id}/leer/`)
      return data
    },
    onSuccess: (data) => {
      queryClient.setQueryData(['recados'], (oldData = []) => {
        if (!Array.isArray(oldData)) return oldData
        return oldData.map((item) => (item.id === data.id ? data : item))
      })
    },
  })

  return {
    ...query,
    recados: query.data || [],
    crearRecado: crearRecado.mutateAsync,
    actualizarEstado: actualizarEstado.mutateAsync,
    marcarLeido: marcarLeido.mutateAsync,
  }
}