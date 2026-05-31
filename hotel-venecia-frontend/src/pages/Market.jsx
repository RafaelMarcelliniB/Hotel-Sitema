import Card from '../components/ui/Card'
import Table from '../components/ui/Table'
import { useProductos } from '../hooks/useProductos'

export default function Market() {
  const { data = [] } = useProductos()

  return (
    <Card>
      <h3 className="mb-4 text-lg font-semibold">Market</h3>
      <Table columns={['Producto', 'Categoría', 'Stock', 'Mínimo', 'Precio']}>
        {data.map((producto) => (
          <tr key={producto.id}>
            <td className="px-4 py-3">{producto.nombre}</td>
            <td className="px-4 py-3">{producto.categoria}</td>
            <td className="px-4 py-3">{producto.stock_actual}</td>
            <td className="px-4 py-3">{producto.stock_minimo}</td>
            <td className="px-4 py-3">S/ {producto.precio_unitario}</td>
          </tr>
        ))}
      </Table>
    </Card>
  )
}
