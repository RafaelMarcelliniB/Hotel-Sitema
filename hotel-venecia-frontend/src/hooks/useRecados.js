import { getRecados } from '../api/recadosApi'
import { useAsyncData } from './useAsyncData'

export function useRecados() {
  return useAsyncData(getRecados)
}
