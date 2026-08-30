import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getProductos } from '../api/marketApi'
import api from '../api/axiosConfig'

function normalizarProducto(producto) {
  const toNumber = (value) => {
    const parsed = Number(value)
    return Number.isFinite(parsed) ? parsed : 0
  }

  const stockAlmacen = toNumber(producto.stock_almacen)
  const stockRecepcion = toNumber(producto.stock_recepcion)
  const stockRefrigeradora = toNumber(producto.stock_refrigeradora)
  const stockTotal = stockAlmacen + stockRecepcion + stockRefrigeradora

  return {
    ...producto,
    stock_almacen: stockAlmacen,
    stock_recepcion: stockRecepcion,
    stock_refrigeradora: stockRefrigeradora,
    stock_total: stockTotal,
    precio_unitario: toNumber(producto.precio_unitario),
  }
}

export function useProductos() {
  const queryClient = useQueryClient()

  const query = useQuery({
    queryKey: ['productos'],
    queryFn: async () => {
      const data = await getProductos()
      return Array.isArray(data) ? data.map(normalizarProducto) : []
    }
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

  const importarProductos = useMutation({
    mutationFn: async (file) => {
      const fd = new FormData()
      fd.append('file', file)
      const { data } = await api.post('/market/productos/importar-excel/', fd, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['productos'])
    }
  })

  const previewProductos = useMutation({
    mutationFn: async (file) => {
      const fd = new FormData()
      fd.append('file', file)
      const { data } = await api.post('/market/productos/preview-excel/', fd, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      return data
    }
  })

  const transferirStock = useMutation({
    mutationFn: async ({ productoId, origen, destino, cantidad, motivo = '' }) => {
      const { data } = await api.post(`/market/productos/${productoId}/transferir/`, {
        origen,
        destino,
        cantidad,
        motivo,
      })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['productos'])
    }
  })

  return {
    ...query,
    productos: query.data || [],
    refetchProductos: query.refetch,
    procesarVenta: registrarVenta.mutateAsync,
    isSelling: registrarVenta.isLoading,
    importarProductos: importarProductos.mutateAsync,
    previewProductos: previewProductos.mutateAsync,
    transferirStock: transferirStock.mutateAsync,
    isTransferring: transferirStock.isLoading,
  }
}