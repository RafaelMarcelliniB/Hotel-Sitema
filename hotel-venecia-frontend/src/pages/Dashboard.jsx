import Card from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import Spinner from '../components/ui/Spinner'
import { useDashboard } from '../hooks/useDashboard'
import { Button } from '../components/ui/Button'

export default function Dashboard() {
  const { data, isLoading, isError, refetch } = useDashboard()

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

  return (
    <div className="space-y-6 p-2 md:p-6">
      <header className="flex justify-between items-center">
        <h2 className="text-2xl font-black text-slate-800">Panel de Control</h2>
        <p className="text-sm text-slate-500 font-medium">Hotel Venecia S.R.L.</p>
      </header>

      {/* KPIs Principales */}
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card className="border-l-4 border-l-blue-500">
          <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Hab. Ocupadas</p>
          <h3 className="mt-2 text-4xl font-black text-slate-900">{data.habitaciones?.ocupadas || 0}</h3>
          <div className="mt-2 text-xs text-blue-600 font-semibold">
            {Math.round((data.habitaciones?.ocupadas / (data.habitaciones?.ocupadas + data.habitaciones?.disponibles)) * 100) || 0}% Ocupación
          </div>
        </Card>

        <Card className="border-l-4 border-l-green-500">
          <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Ingresos del Día</p>
          <h3 className="mt-2 text-4xl font-black text-green-600">S/ {data.ingresosDia || '0.00'}</h3>
          <p className="text-xs text-slate-400 mt-2">Caja activa: Turno actual</p>
        </Card>

        <Card className="border-l-4 border-l-orange-500">
          <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Disponibles</p>
          <h3 className="mt-2 text-4xl font-black text-slate-900">{data.habitaciones?.disponibles || 0}</h3>
          <p className="text-xs text-orange-600 mt-2 font-medium">Listas para check-in</p>
        </Card>

        <Card className="border-l-4 border-l-red-500">
          <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Pendientes de Pago</p>
          <h3 className="mt-2 text-4xl font-black text-red-600">S/ {data.deudasPendientes || '0.00'}</h3>
          <p className="text-xs text-slate-400 mt-2">Cuentas por cobrar</p>
        </Card>
      </section>

      {/* Detalles y Alertas */}
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
            <div className="flex justify-between items-center p-3 bg-yellow-50 rounded-lg border border-yellow-100">
              <span className="text-sm font-medium text-yellow-800">Checkouts hoy</span>
              <Badge variant="warning">{data.proximosCheckouts || 0}</Badge>
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
    </div>
  )
}