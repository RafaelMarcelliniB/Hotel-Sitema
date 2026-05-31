import { getEspacios } from '../api/cocheraApi'
import { useAsyncData } from './useAsyncData'

export function useEspacios() {
  return useAsyncData(getEspacios)
}
