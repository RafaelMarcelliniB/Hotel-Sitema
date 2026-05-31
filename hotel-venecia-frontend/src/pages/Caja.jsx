import Card from '../components/ui/Card'
import Table from '../components/ui/Table'
import { useCajas } from '../hooks/useCajas'

export default function Caja() {
  const { data = [] } = useCajas()

  return (
    <Card>
      <h3 className="mb-4 text-lg font-semibold">Cajas</h3>
      <Table columns={['Trabajador', 'Turno', 'Estado', 'Monto inicial']}>
        {data.map((caja) => (
          <tr key={caja.id}>
            <td className="px-4 py-3">{caja.trabajador}</td>
            <td className="px-4 py-3">{caja.turno}</td>
            <td className="px-4 py-3">{caja.estado}</td>
            <td className="px-4 py-3">S/ {caja.monto_inicial}</td>
          </tr>
        ))}
      </Table>
    </Card>
  )
}
