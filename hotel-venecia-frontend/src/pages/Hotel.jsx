import Card from '../components/ui/Card'
import Table from '../components/ui/Table'
import { useHabitaciones } from '../hooks/useHabitaciones'

export default function Hotel() {
  const { data = [] } = useHabitaciones()

  return (
    <Card>
      <h3 className="mb-4 text-lg font-semibold">Habitaciones</h3>
      <Table columns={['Número', 'Tipo', 'Ocupación', 'Limpieza', 'Tarifa']}>
        {data.map((habitacion) => (
          <tr key={habitacion.id}>
            <td className="px-4 py-3">{habitacion.numero}</td>
            <td className="px-4 py-3">{habitacion.tipo}</td>
            <td className="px-4 py-3">{habitacion.estado_ocupacion}</td>
            <td className="px-4 py-3">{habitacion.estado_limpieza}</td>
            <td className="px-4 py-3">S/ {habitacion.tarifa_dia}</td>
          </tr>
        ))}
      </Table>
    </Card>
  )
}
