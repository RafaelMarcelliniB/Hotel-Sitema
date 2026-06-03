import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getEspacios } from '../api/cocheraApi'
import api from '../api/axiosConfig'

export function useEspacios() {
  const queryClient = useQueryClient()

  const query = useQuery({
    queryKey: ['espacios'],
    queryFn: getEspacios,
    refetchInterval: 30000 // Refresco automático cada 30 segundos
  })

  const registrarIngreso = useMutation({
    mutationFn: async (datos) => {
      const { data } = await api.post('/cochera/ingresos/', datos)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['espacios'])
      queryClient.invalidateQueries(['dashboard-metrics']) // Sincroniza el Dashboard
    }
  })

  const registrarSalida = useMutation({
    mutationFn: async (idEspacio) => {
      const { data } = await api.post(`/cochera/espacios/${idEspacio}/salida/`)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['espacios'])
      queryClient.invalidateQueries(['dashboard-metrics']) // Sincroniza el Dashboard
    }
  })

  return {
    ...query,
    espacios: query.data || [],
    registrarIngreso: registrarIngreso.mutateAsync,
    registrarSalida: registrarSalida.mutateAsync,
    isMutating: registrarIngreso.isLoading || registrarSalida.isLoading // Agrega estado de carga
  }
}