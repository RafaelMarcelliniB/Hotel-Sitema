import { useState } from 'react'
import Card from '../components/ui/Card'
import { Input } from '../components/ui/Input'
import { Button } from '../components/ui/Button'
import { useProductos } from '../hooks/useProductos'
import Spinner from '../components/ui/Spinner'

export default function Market() {
  const { productos, isLoading, procesarVenta } = useProductos()
  const [filtro, setFiltro] = useState('')
  const [carrito, setCarrito] = useState([])

  // Filtrar productos por nombre
  const productosFiltrados = productos.filter(p => 
    p.nombre.toLowerCase().includes(filtro.toLowerCase())
  )

  const agregarAlCarrito = (producto) => {
    if (producto.stock_actual <= 0) return alert("Sin stock disponible")
    
    setCarrito(prev => {
      const existe = prev.find(item => item.id === producto.id)
      if (existe) {
        return prev.map(item => 
          item.id === producto.id ? { ...item, cantidad: item.cantidad + 1 } : item
        )
      }
      return [...prev, { ...producto, cantidad: 1 }]
    })
  }

  const total = carrito.reduce((acc, item) => acc + (item.precio_unitario * item.cantidad), 0)

  const finalizarVenta = async () => {
    if (carrito.length === 0) return
    try {
      await procesarVenta({
        productos: carrito.map(i => ({ id: i.id, cantidad: i.cantidad })),
        tipo_pago: 'EFECTIVO',
        total: total
      })
      setCarrito([])
      alert("Venta realizada con éxito")
    } catch (err) {
      alert("Error al procesar la venta")
    }
  }

  if (isLoading) return <Spinner />

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Sección de Selección */}
      <div className="lg:col-span-2 space-y-4">
        <Card>
          <Input 
            placeholder="Buscar producto..." 
            value={filtro}
            onChange={(e) => setFiltro(e.target.value)}
          />
        </Card>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {productosFiltrados.map(p => (
            <div 
              key={p.id} 
              onClick={() => agregarAlCarrito(p)}
              className="bg-white p-4 rounded-xl shadow-sm border hover:border-blue-500 cursor-pointer transition-all"
            >
              <h4 className="font-bold">{p.nombre}</h4>
              <p className="text-sm text-gray-500">Stock: {p.stock_actual}</p>
              <p className="text-blue-600 font-bold mt-2">S/ {p.precio_unitario}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Sección de Carrito */}
      <div className="space-y-4">
        <Card className="h-full flex flex-col">
          <h3 className="text-lg font-bold mb-4">Resumen de Venta</h3>
          <div className="flex-1 space-y-3 overflow-y-auto max-h-[400px]">
            {carrito.map(item => (
              <div key={item.id} className="flex justify-between items-center text-sm border-b pb-2">
                <div>
                  <p className="font-medium">{item.nombre}</p>
                  <p className="text-gray-400">x{item.cantidad}</p>
                </div>
                <span>S/ {(item.precio_unitario * item.cantidad).toFixed(2)}</span>
              </div>
            ))}
            {carrito.length === 0 && <p className="text-center text-gray-400 py-10">Carrito vacío</p>}
          </div>

          <div className="mt-6 pt-4 border-t">
            <div className="flex justify-between text-xl font-bold mb-4">
              <span>Total:</span>
              <span className="text-green-600">S/ {total.toFixed(2)}</span>
            </div>
            <Button 
              className="w-full py-4 text-lg" 
              disabled={carrito.length === 0}
              onClick={finalizarVenta}
            >
              Procesar Pago
            </Button>
          </div>
        </Card>
      </div>
    </div>
  )
}