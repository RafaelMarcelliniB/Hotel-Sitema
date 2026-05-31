import { getCajas } from '../api/cajaApi'
import { useAsyncData } from './useAsyncData'

export function useCajas() {
  return useAsyncData(getCajas)
}
