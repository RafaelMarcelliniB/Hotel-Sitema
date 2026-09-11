import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getEspacios, crearEspacio } from '../api/cocheraApi'
import api from '../api/axiosConfig'

export function useEspacios() {
  const queryClient = useQueryClient()

  const query = useQuery({
    queryKey: ['espacios'],
    queryFn: getEspacios,
    refetchInterval: 15000 // Refresco cada 15 segundos
  })

  const registrarIngreso = useMutation({
    mutationFn: async (datos) => {
      const { data } = await api.post('/cochera/vehiculos/ingreso/', datos) 
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['espacios'])
      queryClient.invalidateQueries(['dashboard-metrics'])
    }
  })

  const registrarSalida = useMutation({
    mutationFn: async ({ registroId, metodo_pago }) => {
      const payload = metodo_pago ? { metodo_pago } : {}
      const { data } = await api.patch(`/cochera/vehiculos/${registroId}/salida/`, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['espacios'])
      queryClient.invalidateQueries(['dashboard-metrics'])
      queryClient.invalidateQueries(['caja-resumen']) // Actualiza tus finanzas en tiempo real
    }
  })

  const crearEspacioMutation = useMutation({
    mutationFn: crearEspacio,
    onSuccess: () => {
      queryClient.invalidateQueries(['espacios'])
      queryClient.invalidateQueries(['dashboard-metrics'])
    }
  })

  return {
    ...query,
    espacios: query.data || [],
    registrarIngreso: registrarIngreso.mutateAsync,
    registrarSalida: registrarSalida.mutateAsync,
    crearEspacio: crearEspacioMutation.mutateAsync,
    isCreatingEspacio: crearEspacioMutation.isLoading,
    isMutating: registrarIngreso.isLoading || registrarSalida.isLoading
  }
}