import Card from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import Spinner from '../components/ui/Spinner'
import { useDashboard } from '../hooks/useDashboard'

export default function Dashboard() {
  const { data, isLoading } = useDashboard()

  if (isLoading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <Spinner />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {[
          ['Ocupadas', data.habitaciones.ocupadas],
          ['Disponibles', data.habitaciones.disponibles],
          ['Ingresos', `S/ ${data.ingresosDia}`],
          ['Deudas', `S/ ${data.deudasPendientes}`],
        ].map(([label, value]) => (
          <Card key={label}>
            <p className="text-sm text-slate-500">{label}</p>
            <h3 className="mt-2 text-3xl font-bold text-slate-900">{value}</h3>
          </Card>
        ))}
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        <Card>
          <h3 className="mb-4 text-lg font-semibold">Estado de habitaciones</h3>
          <div className="flex flex-wrap gap-3">
            {Object.entries(data.habitaciones).map(([label, value]) => (
              <Badge key={label} variant="accent">{label}: {value}</Badge>
            ))}
          </div>
        </Card>
        <Card>
          <h3 className="mb-4 text-lg font-semibold">Resumen rápido</h3>
          <ul className="space-y-2 text-sm text-slate-600">
            <li>Próximos checkouts: {data.proximosCheckouts}</li>
            <li>Pagos registrados: {data.pagos.length}</li>
            <li>Productos top: {data.productosMasVendidos[0]?.name}</li>
          </ul>
        </Card>
      </section>
    </div>
  )
}
