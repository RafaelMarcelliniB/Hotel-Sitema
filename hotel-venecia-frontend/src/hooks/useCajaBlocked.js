/**
 * Hook: useCajaBlocked
 * 
 * Detecta si el usuario actual tiene una caja abierta.
 * 
 * Uso:
 * const { cajaActiva, cargando, validarCaja } = useCajaBlocked()
 * 
 * Returns:
 *  - cajaActiva: objeto con estado de caja o null si no hay
 *  - cargando: true mientras se verifica
 *  - validarCaja: función para validar manualmente
 *  - mostrarBloqueo: boolean si debe bloquearse la acción
 */

import { useQuery } from '@tanstack/react-query'
import api from '../api/axiosConfig'

export function useCajaBlocked() {
  // Usar la misma fuente de verdad que TopBar: /caja/resumen/
  const { data: resumenCaja, isLoading: cargando } = useQuery({
    queryKey: ['caja-resumen'],
    queryFn: async () => {
      const { data } = await api.get('/caja/resumen/')
      return data
    },
    refetchInterval: 10000,
    staleTime: 0,
    retry: false,
  })

  const cajaActiva = Boolean(resumenCaja?.caja_activa && resumenCaja?.caja)

  /**
   * Verifica si debe bloquearse la operación
   * Retorna true si NO hay caja abierta (debe bloquearse)
   */
  const mostrarBloqueo = !cargando && !cajaActiva

  /**
   * Función manual para validar caja
   * Retorna true si hay caja abierta, false si no
   */
  const validarCaja = () => {
    return cajaActiva
  }

  return {
    cajaActiva,
    cargando,
    validarCaja,
    mostrarBloqueo,
    totalCajasAbiertas: cajaActiva ? 1 : 0,
  }
}
