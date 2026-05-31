import Card from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import { useEspacios } from '../hooks/useEspacios'

export default function Cochera() {
  const { data = [] } = useEspacios()

  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {data.map((espacio) => (
        <Card key={espacio.id}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-500">Espacio</p>
              <h3 className="text-2xl font-bold">{espacio.numero}</h3>
            </div>
            <Badge variant={espacio.estado === 'LIBRE' ? 'success' : 'danger'}>{espacio.estado}</Badge>
          </div>
          <p className="mt-4 text-sm text-slate-600">Tipo: {espacio.tipo}</p>
        </Card>
      ))}
    </div>
  )
}
