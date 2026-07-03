import { useQuery } from '@tanstack/react-query'
import { getDashboardMetrics, getCajaResumen } from '../api/dashboardApi'

export function useDashboard() {
  const query = useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: getDashboardMetrics,
    refetchInterval: 1000 * 10,
    staleTime: 0,
    retry: false,
  })

  return {
    data: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
    refetch: query.refetch,
  }
}

export function useCajaResumen(filters) {
  const query = useQuery({
    queryKey: ['caja-resumen', filters],
    queryFn: () => getCajaResumen(filters),
    enabled: false,
    keepPreviousData: true,
    staleTime: 1000 * 30,
    retry: false,
  })

  return {
    data: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
    refetch: query.refetch,
  }
}
