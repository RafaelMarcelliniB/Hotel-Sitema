import Card from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import { useRecados } from '../hooks/useRecados'

export default function Recados() {
  const { data = [] } = useRecados()

  return (
    <div className="space-y-4">
      {data.map((recado) => (
        <Card key={recado.id} className="flex items-center justify-between gap-4">
          <div>
            <p className="text-sm text-slate-500">Recado #{recado.id}</p>
            <h3 className="text-lg font-semibold">{recado.contenido}</h3>
          </div>
          <Badge variant={recado.prioridad === 'ALTA' ? 'danger' : 'warning'}>{recado.prioridad}</Badge>
        </Card>
      ))}
    </div>
  )
}
