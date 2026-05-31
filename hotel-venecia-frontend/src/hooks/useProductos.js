import { getProductos } from '../api/marketApi'
import { useAsyncData } from './useAsyncData'

export function useProductos() {
  return useAsyncData(getProductos)
}
