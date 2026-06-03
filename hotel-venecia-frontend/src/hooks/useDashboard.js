import { useQuery } from '@tanstack/react-query'
import { getDashboardMetrics } from '../api/dashboardApi'

export function useDashboard() {
  const query = useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: getDashboardMetrics,
    refetchInterval: 1000 * 60 * 5, // Se actualiza cada 5 min
  })

  return {
    data: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
    refetch: query.refetch
  }
}