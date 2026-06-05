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
  
  // Nuevo estado para el método de pago dinámico requerido por el backend
  const [metodoPago, setMetodoPago] = useState('EFECTIVO')

  // Filtrar productos por nombre
  const productosFiltrados = productos.filter(p => 
    p.nombre.toLowerCase().includes(filtro.toLowerCase())
  )

  const agregarAlCarrito = (producto) => {
    if (producto.stock_actual <= 0) return alert("Sin stock disponible")
    
    setCarrito(prev => {
      const existe = prev.find(item => item.id === producto.id)
      if (existe) {
        // Validación extra: no agregar más del stock disponible en la UI
        if (existe.cantidad >= producto.stock_actual) {
          alert(`No puedes agregar más unidades. Stock máximo: ${producto.stock_actual}`);
          return prev;
        }
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
      // CORRECCIÓN CRÍTICA: Ajustamos el payload al contrato exacto de Django
      await procesarVenta({
        tipo_venta: 'DIRECTO', // Venta directa de mostrador
        metodo_pago: metodoPago, // 'EFECTIVO', 'YAPE' o 'TARJETA'
        checkin_vinculado_id: null, // No se carga a ninguna habitación
        detalles: carrito.map(i => ({ 
          producto_id: i.id, // Django espera 'producto_id'
          cantidad: i.cantidad 
        }))
      })
      
      setCarrito([])
      alert("Venta realizada con éxito")
    } catch (err) {
      // CAPTURA INTELIGENTE DEL ERROR: lee la respuesta estructurada de Django
      console.error(err)
      const mensajeError = err.response?.data?.detail || "Error al procesar la venta"
      alert(`⚠️ Atención: ${mensajeError}`)
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
              className="bg-white p-4 rounded-xl shadow-sm border hover:border-blue-500 cursor-pointer transition-all flex flex-col justify-between"
            >
              <div>
                <h4 className="font-bold text-slate-800">{p.nombre}</h4>
                <p className="text-sm text-gray-500">Stock: {p.stock_actual}</p>
              </div>
              <p className="text-blue-600 font-bold mt-2 text-lg">S/ {Number(p.precio_unitario).toFixed(2)}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Sección de Carrito */}
      <div className="space-y-4">
        <Card className="h-full flex flex-col justify-between">
          <div>
            <h3 className="text-lg font-bold mb-4">Resumen de Venta</h3>
            <div className="space-y-3 overflow-y-auto max-h-[300px] pr-1">
              {carrito.map(item => (
                <div key={item.id} className="flex justify-between items-center text-sm border-b pb-2">
                  <div>
                    <p className="font-medium text-slate-700">{item.nombre}</p>
                    <p className="text-gray-400">x{item.cantidad}</p>
                  </div>
                  <span className="font-semibold text-slate-900">S/ {(item.precio_unitario * item.cantidad).toFixed(2)}</span>
                </div>
              ))}
              {carrito.length === 0 && <p className="text-center text-gray-400 py-10">Carrito vacío</p>}
            </div>
          </div>

          <div className="mt-6 pt-4 border-t space-y-4">
            {/* Selector de Método de Pago dinámico */}
            {carrito.length > 0 && (
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Método de Pago</label>
                <select 
                  value={metodoPago} 
                  onChange={(e) => setMetodoPago(e.target.value)}
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm font-medium text-slate-700 focus:outline-none focus:border-blue-500"
                >
                  <option value="EFECTIVO">💵 Efectivo</option>
                  <option value="YAPE">📱 Yape / Plin</option>
                  <option value="TARJETA">💳 Tarjeta Crédito/Débito</option>
                </select>
              </div>
            )}

            <div className="flex justify-between text-xl font-black pt-2">
              <span className="text-slate-700">Total:</span>
              <span className="text-green-600">S/ {total.toFixed(2)}</span>
            </div>
            
            <Button 
              className="w-full py-4 text-lg font-bold" 
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