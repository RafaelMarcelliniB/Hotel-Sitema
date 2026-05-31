import { getDashboardMetrics } from '../api/dashboardApi'
import { useAsyncData } from './useAsyncData'

export function useDashboard() {
  return useAsyncData(getDashboardMetrics)
}
