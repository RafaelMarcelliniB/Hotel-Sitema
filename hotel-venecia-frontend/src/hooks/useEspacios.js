import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getEspacios } from '../api/cocheraApi'
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

  return {
    ...query,
    espacios: query.data || [],
    registrarIngreso: registrarIngreso.mutateAsync, // Retorna la función directa
    registrarSalida: registrarSalida.mutateAsync,   // Retorna la función directa
    isMutating: registrarIngreso.isLoading || registrarSalida.isLoading
  }
}