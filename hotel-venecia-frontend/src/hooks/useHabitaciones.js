import { getHabitaciones } from '../api/hotelApi'
import { useAsyncData } from './useAsyncData'

export function useHabitaciones() {
  return useAsyncData(getHabitaciones)
}
