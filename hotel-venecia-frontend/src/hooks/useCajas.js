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
          
          // MODIFICACIÓN: Si el backend nos avisa que no hay caja activa, devolvemos null
          if (data && data.caja_activa === false) {
            return null
          }
          
          return data
        } catch (err) {
          // Esto solo se ejecutará si de verdad se cae el servidor (500, etc)
          throw err
        }
      },
      refetchInterval: 10000, 
      staleTime: 0,            
      retry: false            
    })

  const abrirCaja = useMutation({
    mutationFn: async (datos) => {
      const { data } = await api.post('/caja/apertura/', datos)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['cajas'])
      queryClient.invalidateQueries(['caja-resumen'])
      queryClient.invalidateQueries(['dashboard-metrics']) // <-- CORRECCIÓN: Actualiza el Dashboard al abrir
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
      queryClient.invalidateQueries(['dashboard-metrics']) // <-- CORRECCIÓN: Actualiza el Dashboard al cerrar
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