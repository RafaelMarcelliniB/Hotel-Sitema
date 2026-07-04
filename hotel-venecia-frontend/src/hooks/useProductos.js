import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getProductos } from '../api/marketApi'
import api from '../api/axiosConfig'

export function useProductos() {
  const queryClient = useQueryClient()

  const query = useQuery({
    queryKey: ['productos'],
    queryFn: getProductos
  })

  const registrarVenta = useMutation({
    mutationFn: async (ventaData) => {
      const { data } = await api.post('/market/ventas/', ventaData)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['productos'])
      queryClient.invalidateQueries(['dashboard-metrics']) // Actualiza ingresos de venta en Dashboard
    }
  })

  return {
    ...query,
    productos: query.data || [],
    procesarVenta: registrarVenta.mutateAsync,
    isSelling: registrarVenta.isLoading
  }
}