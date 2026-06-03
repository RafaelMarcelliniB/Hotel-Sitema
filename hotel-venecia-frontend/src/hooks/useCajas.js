import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getCajas } from '../api/cajaApi'
import api from '../api/axiosConfig'

export function useCajas() {
  const queryClient = useQueryClient()

  // Lista histórica o resumen
  const query = useQuery({
    queryKey: ['cajas'],
    queryFn: getCajas
  })

  // Obtener resumen detallado de la caja activa
  const useResumen = () => useQuery({
    queryKey: ['caja-resumen'],
    queryFn: async () => {
      const { data } = await api.get('/caja/resumen/')
      return data
    },
    refetchInterval: 30000 // Actualiza cada 30 seg
  })

  const abrirCaja = useMutation({
    mutationFn: async (datos) => {
      const { data } = await api.post('/caja/apertura/', datos)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['cajas'])
      queryClient.invalidateQueries(['caja-resumen'])
    }
  })

  const cerrarCaja = useMutation({
    mutationFn: async (datos) => {
      const { data } = await api.post('/caja/cierre/', datos)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['cajas'])
      queryClient.invalidateQueries(['caja-resumen'])
    }
  })

  return {
    ...query,
    useResumen,
    abrirCaja: abrirCaja.mutateAsync,
    cerrarCaja: cerrarCaja.mutateAsync
  }
}