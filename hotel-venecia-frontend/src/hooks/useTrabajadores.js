import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getTrabajadores, registrarTrabajador, actualizarTrabajador } from '../api/authApi'

export function useTrabajadores() {
  const queryClient = useQueryClient()

  const query = useQuery({
    queryKey: ['trabajadores'],
    queryFn: getTrabajadores
  })

  const crearMutation = useMutation({
    mutationFn: registrarTrabajador,
    onSuccess: () => queryClient.invalidateQueries(['trabajadores'])
  })

  const editarMutation = useMutation({
    mutationFn: ({ id, data }) => actualizarTrabajador(id, data),
    onSuccess: () => queryClient.invalidateQueries(['trabajadores'])
  })

  return {
    ...query,
    trabajadores: query.data || [],
    crearTrabajador: crearMutation.mutateAsync,
    editarTrabajador: editarMutation.mutateAsync,
    isLoadingMutation: crearMutation.isLoading || editarMutation.isLoading
  }
}