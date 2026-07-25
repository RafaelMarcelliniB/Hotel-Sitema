import { useEffect, useMemo, useState } from 'react'
import Card from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import Spinner from '../components/ui/Spinner'
import Input from '../components/ui/Input'
import Select from '../components/ui/Select'
import Table from '../components/ui/Table'
import { useDashboard, useCajaResumen } from '../hooks/useDashboard'
import { useTrabajadores } from '../hooks/useTrabajadores'
import { Button } from '../components/ui/Button'
import { useAuthStore } from '../store/authStore'

const TURNOS = [
  { value: 'mañana', label: 'Mañana' },
  { value: 'tarde', label: 'Tarde' },
  { value: 'noche', label: 'Noche' },
  { value: 'madrugada', label: 'Madrugada' },
]

const PERIODOS = [
  { value: 'hoy', label: 'Hoy' },
  { value: 'ayer', label: 'Ayer' },
  { value: 'semana', label: 'Esta semana' },
  { value: 'quincena', label: 'Últimos 15 días' },
  { value: 'mes', label: 'Este mes' },
  { value: 'personalizado', label: 'Rango personalizado' },
]

export default function Dashboard() {
  const user = useAuthStore((state) => state.user)
  const isCajero = user?.rol === 'cajero'
  const isRecepcionista = user?.rol === 'recepcionista'
  const isAdmin = user?.rol === 'admin'
  const { data, isLoading, isError, refetch } = useDashboard()
  const { trabajadores, isLoading: loadingTrabajadores } = useTrabajadores()

  const [periodo, setPeriodo] = useState('hoy')
  const [fechaInicio, setFechaInicio] = useState('')
  const [fechaFin, setFechaFin] = useState('')
  const [trabajadorId, setTrabajadorId] = useState('')
  const [turno, setTurno] = useState('')

  const filterParams = useMemo(() => {
    const params = {}
    if (periodo) params.periodo = periodo
    if (fechaInicio) params.fecha_inicio = fechaInicio
    if (fechaFin) params.fecha_fin = fechaFin
    if (trabajadorId) params.trabajador_id = trabajadorId
    if (turno) params.turno = turno
    return params
  }, [periodo, fechaInicio, fechaFin, trabajadorId, turno])

  const { data: resumenData, isLoading: isLoadingResumen, refetch: refetchResumen } = useCajaResumen(filterParams)

  useEffect(() => {
    refetchResumen()
  }, [filterParams, refetchResumen])

  const handleResetFilters = () => {
    setPeriodo('hoy')
    setFechaInicio('')
    setFechaFin('')
    setTrabajadorId('')
    setTurno('')
  }

  const isCustomDateRange = periodo === 'personalizado'

  const detalleMovimientos = resumenData?.detalle || []
  const consolidado = resumenData?.consolidado || {}
  const desglosePago = resumenData?.desglose_pago || {}

  if (isLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <Spinner />
      </div>
    )
  }

  if (isError || !data) {
    return (
      <div className="text-center p-10">
        <p className="text-red-500">Error al cargar las métricas.</p>
        <Button onClick={() => refetch()} className="mt-4">Reintentar</Button>
      </div>
    )
  }

  const topProduct = data.productosMasVendidos?.[0] || { nombre: 'Sin ventas aún', cantidad: 0 }
  const totalProductosVendidosHoy = data.productosMasVendidos?.reduce((sum, item) => sum + item.cantidad, 0) ?? 0

  const AuditTable = () => (
    <Card className="mt-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between mb-4">
        <div>
          <h3 className="text-lg font-bold text-slate-800">Bitácora de Caja</h3>
          <p className="text-sm text-slate-500">Movimientos registrados según los filtros aplicados.</p>
        </div>
        <div className="inline-flex items-center gap-2 flex-wrap">
          <Badge variant="secondary">{resumenData?.total_movimientos ?? 0} movimientos</Badge>
          <Badge variant="ghost">{resumenData?.filtros?.periodo ? `Periodo: ${resumenData.filtros.periodo}` : 'Filtro personalizado'}</Badge>
        </div>
      </div>

      {isLoadingResumen ? (
        <div className="p-6 text-center text-slate-500">Cargando movimientos...</div>
      ) : detalleMovimientos.length === 0 ? (
        <div className="p-6 text-center text-slate-500">Aplica el filtro para ver el detalle de arqueo y movimientos.</div>
      ) : (
        <div className="overflow-x-auto">
          <Table columns={['Fecha / Hora', 'Trabajador', 'Turno', 'Módulo', 'Tipo', 'Pago', 'Monto', 'Referencia', 'Descripción', 'Bloqueado']}>
            {detalleMovimientos.map((mov) => (
              <tr key={mov.id} className="hover:bg-slate-50">
                <td className="px-4 py-3 text-sm text-slate-600">{new Date(mov.fecha_hora).toLocaleString()}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{mov.trabajador ?? '—'}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{mov.turno}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{mov.modulo}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{mov.tipo}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{mov.tipo_caja}</td>
                <td className="px-4 py-3 text-sm font-semibold text-slate-900">S/ {Number(mov.monto).toFixed(2)}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{mov.referencia || '—'}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{mov.descripcion || '—'}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{mov.bloqueado ? 'Sí' : 'No'}</td>
              </tr>
            ))}
          </Table>
        </div>
      )}
    </Card>
  )

  if (isCajero) {
    return (
      <div className="space-y-6 p-2 md:p-6">
        <header className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-black text-slate-800">Panel de Control</h2>
            <p className="text-sm text-slate-500 font-medium">Cajero Market</p>
          </div>
          <p className="text-sm text-slate-500 font-medium">Hotel Venecia S.R.L.</p>
        </header>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <Card className="border-l-4 border-l-green-500">
            <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Ingresos del Día</p>
            <h3 className="mt-2 text-4xl font-black text-green-600">
              S/ {typeof (data.sumaCajasActivas ?? data.ingresosDia) === 'number' ? (data.sumaCajasActivas ?? data.ingresosDia).toFixed(2) : '0.00'}
            </h3>
            <p className="mt-2 text-xs text-slate-500">Total de ventas registradas hoy</p>
          </Card>

          <Card className="border-l-4 border-l-blue-500">
            <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Producto más vendido</p>
            <h3 className="mt-2 text-4xl font-black text-slate-900">{topProduct.nombre}</h3>
            <p className="mt-2 text-xs text-slate-500">Unidades vendidas: {topProduct.cantidad}</p>
          </Card>

          <Card className="border-l-4 border-l-purple-500">
            <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Caja activa</p>
            <h3 className="mt-2 text-4xl font-black text-purple-600">{data.cajaActiva ? 'Sí' : 'No'}</h3>
            <p className="mt-2 text-xs text-slate-500">Estado de la caja actual</p>
          </Card>

          <Card className="border-l-4 border-l-orange-500">
            <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Unidades vendidas</p>
            <h3 className="mt-2 text-4xl font-black text-slate-900">{totalProductosVendidosHoy}</h3>
            <p className="mt-2 text-xs text-slate-500">Total de productos vendidos hoy</p>
          </Card>
        </section>

        <section className="grid gap-4 md:grid-cols-2">
          <Card className="bg-slate-50 border border-slate-200">
            <h3 className="text-lg font-bold text-slate-800 mb-3">Accesos Rápidos</h3>
            <div className="grid gap-3">
              <Button onClick={() => window.location.href = '/market'} className="w-full">Ir a Market</Button>
              <Button onClick={() => window.location.href = '/caja?module=market'} className="w-full">Ir a Caja Market</Button>
            </div>
          </Card>
          <Card className="bg-slate-50 border border-slate-200">
            <h3 className="text-lg font-bold text-slate-800 mb-3">Notas</h3>
            <p className="text-sm text-slate-600">Este tablero está pensado para cajeros: muestra solo métricas de ventas y caja de market.</p>
          </Card>
        </section>
      </div>
    )
  }

  if (isRecepcionista) {
    const habitaciones = data.habitaciones || {}
    return (
      <div className="space-y-6 p-2 md:p-6">
        <header className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <h2 className="text-2xl font-black text-slate-800">Panel de Recepción</h2>
            <p className="text-sm text-slate-500">Resumen rápido de habitaciones y checkouts.</p>
          </div>
          <div className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-4 py-2 text-sm text-slate-600">
            Rol: <span className="font-semibold uppercase">Recepcionista</span>
          </div>
        </header>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <Card className="border-l-4 border-l-blue-500">
            <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Total Habitaciones</p>
            <p className="mt-3 text-4xl font-black text-blue-600">{habitaciones.total || 0}</p>
          </Card>

          <Card className="border-l-4 border-l-rose-500">
            <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Ocupadas</p>
            <p className="mt-3 text-4xl font-black text-rose-600">{habitaciones.ocupadas || 0}</p>
          </Card>

          <Card className="border-l-4 border-l-emerald-500">
            <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Disponibles</p>
            <p className="mt-3 text-4xl font-black text-emerald-600">{habitaciones.disponibles || 0}</p>
          </Card>

          <Card className="border-l-4 border-l-amber-500">
            <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">RESERVADAS</p>
            <p className="mt-3 text-4xl font-black text-amber-600">{habitaciones.reservadas || 0}</p>
          </Card>
        </section>

        <section className="grid gap-4 xl:grid-cols-3">
          <Card className="xl:col-span-2">
            <h3 className="text-lg font-bold text-slate-800 mb-4">Estado Detallado</h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {Object.entries(habitaciones).map(([label, value]) => (
                <div key={label} className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-center">
                  <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
                  <p className="mt-2 text-2xl font-bold text-slate-900">{value}</p>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <h3 className="text-lg font-bold text-slate-800 mb-4">Próximas Acciones</h3>
            <div className="space-y-4">
              <div className="rounded-2xl border border-amber-100 bg-amber-50 p-4">
                <p className="text-xs uppercase tracking-wide text-amber-600">RESERVAS ACTIVAS</p>
                  <p className="mt-2 text-2xl font-bold text-amber-900">{data.reservas_activas ?? 0}</p>
                  <p className="mt-1 text-sm text-amber-700">En custodia: S/ {Number(data.monto_custodia || 0).toFixed(2)}</p>
                <Button className="mt-3 w-full" variant="secondary" onClick={() => window.location.href = '/reservas'}>Ir a Reservas</Button>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-white p-4">
                <p className="text-xs uppercase tracking-wide text-slate-500">Producto más vendido</p>
                <p className="mt-3 text-sm font-semibold text-slate-800">{topProduct.nombre}</p>
              </div>
              <Button className="w-full" variant="outline" onClick={() => window.location.href = '/hotel'}>
                Ir al Mapa de Habitaciones
              </Button>
            </div>
          </Card>
        </section>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-2 md:p-6">
      <header className="flex justify-between items-center">
        <h2 className="text-2xl font-black text-slate-800">Panel de Control</h2>
        <p className="text-sm text-slate-500 font-medium">Hotel Venecia S.R.L.</p>
      </header>

      {/* Barra de Filtros Compacta en Una Línea */}
      <section className="rounded-2xl border border-slate-200 bg-white p-3 shadow-sm mb-4">
        <div className="flex flex-col gap-3">
          {/* Fila 1: Filtros Principales */}
          <div className="flex flex-col lg:flex-row gap-3 items-end">
            <div className="flex-1 min-w-[140px]">
              <label className="block text-xs font-semibold text-slate-500 mb-1">Periodo</label>
              <Select value={periodo} onChange={(e) => { setPeriodo(e.target.value); setFechaInicio(''); setFechaFin('') }} className="text-sm">
                {PERIODOS.map((option) => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </Select>
            </div>
            <div className="flex-1 min-w-[140px]">
              <label className="block text-xs font-semibold text-slate-500 mb-1">Turno</label>
              <Select value={turno} onChange={(e) => setTurno(e.target.value)} className="text-sm">
                <option value="">Todos</option>
                {TURNOS.map((option) => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </Select>
            </div>
            <div className="flex-1 min-w-[160px]">
              <label className="block text-xs font-semibold text-slate-500 mb-1">Trabajador</label>
              <Select value={trabajadorId} onChange={(e) => setTrabajadorId(e.target.value)} disabled={loadingTrabajadores} className="text-sm">
                <option value="">Todos</option>
                {trabajadores.map((trabajador) => (
                  <option key={trabajador.id} value={trabajador.id}>{trabajador.nombre} {trabajador.apellido}</option>
                ))}
              </Select>
            </div>
            <Button variant="secondary" size="sm" onClick={handleResetFilters} className="min-w-[130px]">
              Limpiar filtros
            </Button>
          </div>

          {/* Fila 2: Rango de fechas personalizado - Solo visible cuando se selecciona 'personalizado' */}
          {isCustomDateRange && (
            <div className="flex flex-col lg:flex-row gap-3 items-end">
              <div className="flex-1 min-w-[140px]">
                <label className="block text-xs font-semibold text-slate-500 mb-1">Desde</label>
                <Input type="date" value={fechaInicio} onChange={(e) => setFechaInicio(e.target.value)} className="text-sm" />
              </div>
              <div className="flex-1 min-w-[140px]">
                <label className="block text-xs font-semibold text-slate-500 mb-1">Hasta</label>
                <Input type="date" value={fechaFin} onChange={(e) => setFechaFin(e.target.value)} className="text-sm" />
              </div>
              <span className="text-xs text-slate-500 font-medium px-3 py-2">Rango personalizado activado</span>
            </div>
          )}
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
      {/* Tarjeta Principal: Ingresos con Desglose Integrado */}
        <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200 p-6 xl:col-span-1">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-xs font-bold text-green-700 uppercase tracking-wide">Ingresos Totales</p>
              <p className="mt-4 text-5xl font-black text-green-600">S/ {Number(consolidado.total_ingresos || 0).toFixed(2)}</p>
            </div>
            <div className="text-4xl">💰</div>
          </div>
          
          {/* Desglose por método de pago integrado */}
          <div className="mt-6 pt-4 border-t border-green-200">
            <p className="text-xs font-semibold text-green-700 uppercase mb-3">Desglose por Método</p>
            <div className="space-y-2">
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-700">💵 Efectivo</span>
                <span className="font-bold text-slate-900">S/ {Number(desglosePago.efectivo || 0).toFixed(2)}</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-700">📱 Yape</span>
                <span className="font-bold text-slate-900">S/ {Number(desglosePago.yape || 0).toFixed(2)}</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-700">💳 Tarjeta</span>
                <span className="font-bold text-slate-900">S/ {Number(desglosePago.tarjeta || 0).toFixed(2)}</span>
              </div>
            </div>
          </div>
        </Card>

        <Card className="border-l-4 border-l-yellow-500">
          <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Reservas Activas</p>
          <p className="mt-3 text-2xl font-black text-amber-700">{data.reservas_activas ?? 0} reservas</p>
          <p className="mt-2 text-sm text-slate-600">En custodia: S/ {Number(data.monto_custodia || 0).toFixed(2)}</p>
          <p className="mt-1 text-xs text-slate-500">Vencidas: {data.reservas?.vencidas ?? 0}</p>
        </Card>

      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        <Card className="border-l-4 border-l-blue-500">
          <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Hab. Ocupadas</p>
          <h3 className="mt-2 text-4xl font-black text-slate-900">{data.habitaciones?.ocupadas || 0}</h3>
          <div className="mt-2 text-xs text-blue-600 font-semibold">
            {Math.round((data.habitaciones?.ocupadas / (data.habitaciones?.total || 1)) * 100) || 0}% Ocupación
          </div>
        </Card>

        <Card className="border-l-4 border-l-orange-500">
          <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Disponibles</p>
          <h3 className="mt-2 text-4xl font-black text-slate-900">{data.habitaciones?.disponibles || 0}</h3>
          <p className="mt-2 text-xs text-orange-600 font-medium">Listas para check-in</p>
        </Card>
      </section>

      <section className="grid gap-6 xl:grid-cols-3">
        <Card className="xl:col-span-2">
          <h3 className="mb-6 text-lg font-bold text-slate-800">Estado Detallado</h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {data.habitaciones && Object.entries(data.habitaciones).map(([label, value]) => (
              <div key={label} className="p-4 rounded-lg bg-slate-50 text-center border">
                <p className="text-xs text-slate-500 uppercase mb-1">{label}</p>
                <span className="text-xl font-bold">{value}</span>
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <h3 className="mb-4 text-lg font-bold text-slate-800">Próximas Acciones</h3>
          <div className="space-y-4">
            <div className="rounded-2xl border border-amber-100 bg-amber-50 p-4">
              <p className="text-xs uppercase tracking-wide text-amber-600">Reservas Activas</p>
              <p className="mt-2 text-2xl font-bold text-amber-900">{data.reservas_activas ?? 0}</p>
              <p className="mt-1 text-sm text-amber-700">En custodia: S/ {Number(data.monto_custodia || 0).toFixed(2)}</p>
              <Button className="mt-3 w-full" variant="secondary" onClick={() => window.location.href = '/reservas'}>Ir a Reservas</Button>
            </div>
            <div className="p-3 bg-blue-50 rounded-lg border border-blue-100">
              <p className="text-xs text-blue-600 font-bold uppercase mb-1">Producto más vendido</p>
              <p className="text-sm font-bold text-blue-900">
                {data.productosMasVendidos?.[0]?.nombre || 'Sin ventas aún'}
              </p>
            </div>
            <Button className="w-full" variant="outline" onClick={() => window.location.href = '/hotel'}>
              Ir al Mapa de Habitaciones
            </Button>
          </div>
        </Card>
      </section>

      {AuditTable()}
    </div>
  )
}
