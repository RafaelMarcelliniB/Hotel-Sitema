import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getCajas } from '../api/cajaApi'
import api from '../api/axiosConfig'

export function useCajas() {
  const queryClient = useQueryClient()

  // Lista histórica de cajas
  const query = useQuery({
    queryKey: ['cajas'],
    queryFn: getCajas
  })

  // Obtener resumen detallado de la caja activa
  const useResumen = () => useQuery({
    queryKey: ['caja-resumen'],
    queryFn: async () => {
      try {
        const { data } = await api.get('/caja/resumen/')
        return data
      } catch (err) {
        // Si el backend devuelve 400 o 404, asumimos que no hay caja activa
        if (err.response?.status === 400 || err.response?.status === 404) {
          return null
        }
        throw err
      }
    },
    refetchInterval: 10000, // Actualiza cada 10 segundos para mayor fluidez
    staleTime: 0,           // Considera los datos viejos de inmediato
    retry: false            
  })

  const abrirCaja = useMutation({
    mutationFn: async (datos) => {
      const { data } = await api.post('/caja/apertura/', datos)
      return data
    },
    onSuccess: () => {
      // Forzar actualización de todas las queries relacionadas a caja
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
    cerrarCaja: cerrarCaja.mutateAsync,
    isOpening: abrirCaja.isLoading,
    isClosing: cerrarCaja.isLoading
  }
}