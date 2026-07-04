import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Card from '../components/ui/Card'
import { Input } from '../components/ui/Input'
import { Button } from '../components/ui/Button'
import CajaBlockedModal from '../components/ui/CajaBlockedModal'
import { useProductos } from '../hooks/useProductos'
import { useHabitaciones } from '../hooks/useHabitaciones'
import { useCajaBlocked } from '../hooks/useCajaBlocked'
import Spinner from '../components/ui/Spinner'

export default function Market() {
  const navigate = useNavigate()
  const { productos, isLoading, procesarVenta } = useProductos()
  const { habitaciones } = useHabitaciones()
  const { cajaActiva } = useCajaBlocked()
  
  const [filtro, setFiltro] = useState('')
  const [carrito, setCarrito] = useState([])
  const [showCajaBlocked, setShowCajaBlocked] = useState(false)
  
  // Estados para método de pago y habitación
  const [metodoPago, setMetodoPago] = useState('EFECTIVO')
  const [habitacionSeleccionada, setHabitacionSeleccionada] = useState(null)
  
  // Filtrar solo habitaciones ocupadas con checkin activo
  const habitacionesOcupadas = habitaciones.filter(h => 
    h.estado_ocupacion === 'OCUPADO' && h.checkin_actual_id
  )

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

  // Funciones para gestión del carrito
  const incrementarCantidad = (productoId, stock_maximo) => {
    setCarrito(prev =>
      prev.map(item =>
        item.id === productoId && item.cantidad < stock_maximo
          ? { ...item, cantidad: item.cantidad + 1 }
          : item
      )
    )
  }

  const decrementarCantidad = (productoId) => {
    setCarrito(prev => {
      const actualizado = prev.map(item =>
        item.id === productoId
          ? { ...item, cantidad: Math.max(0, item.cantidad - 1) }
          : item
      )
      // Remover producto si cantidad llega a 0
      return actualizado.filter(item => item.cantidad > 0)
    })
  }

  const removerDelCarrito = (productoId) => {
    setCarrito(prev => prev.filter(item => item.id !== productoId))
  }

  // Helper para determinar estado de stock
  const getEstadoStock = (stock) => {
    if (stock === 0) return 'agotado'
    if (stock <= 3) return 'bajo'
    return 'disponible'
  }

  const finalizarVenta = async () => {
    if (carrito.length === 0) return
    
    // 🔒 BLOQUEO DE SEGURIDAD: Validar caja abierta ANTES de procesar
    if (!cajaActiva) {
      setShowCajaBlocked(true)
      return
    }
    
    // Validar que se haya seleccionado habitación si es "Cargar a Habitación"
    if (metodoPago === 'CARGAR_HABITACION' && !habitacionSeleccionada) {
      alert('Por favor, selecciona una habitación para cargar los consumos')
      return
    }

    try {
      // CORRECCIÓN CRÍTICA: Ajustamos el payload al contrato exacto de Django
      await procesarVenta({
        tipo_venta: metodoPago === 'CARGAR_HABITACION' ? 'CARGADO_HABITACION' : 'DIRECTO',
        metodo_pago: metodoPago === 'CARGAR_HABITACION' ? 'EFECTIVO' : metodoPago,
        checkin_vinculado_id: metodoPago === 'CARGAR_HABITACION' ? habitacionSeleccionada : null,
        detalles: carrito.map(i => ({ 
          producto_id: i.id,
          cantidad: i.cantidad 
        }))
      })
      
      setCarrito([])
      setMetodoPago('EFECTIVO')
      setHabitacionSeleccionada(null)
      alert("✅ Venta realizada con éxito. Stock actualizado.")
    } catch (err) {
      console.error(err)
      
      // Si el error es de caja no abierta, mostrar modal de bloqueo
      if (err.response?.status === 400 && 
          err.response?.data?.detail?.includes("Debe aperturar")) {
        setShowCajaBlocked(true)
      } else {
        const mensajeError = err.response?.data?.detail || "Error al procesar la venta"
        alert(`⚠️ Atención: ${mensajeError}`)
      }
    }
  }

  if (isLoading) return <Spinner />

  return (
    <>
      {/* MODAL DE BLOQUEO DE CAJA */}
      <CajaBlockedModal 
        isOpen={showCajaBlocked}
        onClose={() => setShowCajaBlocked(false)}
        onNavigateToCaja={() => {
          navigate('/caja')
        }}
      />

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
          {productosFiltrados.map(p => {
            const estadoStock = getEstadoStock(p.stock_actual)
            const isDisabled = estadoStock === 'agotado'
            
            return (
              <div 
                key={p.id} 
                onClick={() => !isDisabled && agregarAlCarrito(p)}
                className={`p-4 rounded-xl shadow-sm border flex flex-col justify-between transition-all ${
                  isDisabled
                    ? 'bg-gray-100 border-gray-300 opacity-50 cursor-not-allowed'
                    : 'bg-white hover:border-blue-500 cursor-pointer'
                }`}
              >
                <div>
                  <h4 className="font-bold text-slate-800">{p.nombre}</h4>
                  <p className={`text-sm mt-1 font-semibold ${
                    estadoStock === 'agotado' ? 'text-gray-400' :
                    estadoStock === 'bajo' ? 'text-red-500' : 'text-gray-500'
                  }`}>
                    Stock: {p.stock_actual}
                    {estadoStock === 'bajo' && ' ⚠️'}
                  </p>
                </div>
                <p className={`font-bold mt-2 text-lg ${
                  isDisabled
                    ? 'text-gray-500 italic'
                    : 'text-blue-600'
                }`}>
                  {isDisabled ? 'Agotado' : `S/ ${Number(p.precio_unitario).toFixed(2)}`}
                </p>
              </div>
            )
          })}
        </div>
      </div>

      {/* Sección de Carrito */}
      <div className="space-y-4">
        <Card className="h-full flex flex-col justify-between">
          <div>
            <h3 className="text-lg font-bold mb-4">Resumen de Venta</h3>
            <div className="space-y-3 overflow-y-auto max-h-[300px] pr-1">
              {carrito.map(item => (
                <div key={item.id} className="flex justify-between items-center text-sm border-b pb-2 group">
                  <div className="flex-1">
                    <p className="font-medium text-slate-700">{item.nombre}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <button
                        onClick={() => decrementarCantidad(item.id)}
                        className="w-6 h-6 rounded bg-red-100 text-red-600 font-bold hover:bg-red-200 transition flex items-center justify-center"
                        title="Disminuir cantidad"
                      >
                        −
                      </button>
                      <span className="w-6 text-center font-semibold text-slate-700">{item.cantidad}</span>
                      <button
                        onClick={() => incrementarCantidad(item.id, item.stock_actual)}
                        className="w-6 h-6 rounded bg-green-100 text-green-600 font-bold hover:bg-green-200 transition flex items-center justify-center"
                        title="Aumentar cantidad"
                        disabled={item.cantidad >= item.stock_actual}
                      >
                        +
                      </button>
                    </div>
                  </div>
                  <div className="text-right mr-2">
                    <span className="font-semibold text-slate-900">S/ {(item.precio_unitario * item.cantidad).toFixed(2)}</span>
                  </div>
                  <button
                    onClick={() => removerDelCarrito(item.id)}
                    className="w-6 h-6 rounded bg-slate-100 text-slate-600 hover:bg-slate-200 hover:text-red-600 transition flex items-center justify-center opacity-0 group-hover:opacity-100"
                    title="Remover producto"
                  >
                    🗑️
                  </button>
                </div>
              ))}
              {carrito.length === 0 && <p className="text-center text-gray-400 py-10">Carrito vacío</p>}
            </div>
          </div>

          <div className="mt-6 pt-4 border-t space-y-4">
            {/* Selector de Método de Pago dinámico */}
            {carrito.length > 0 && (
              <>
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Método de Pago</label>
                  <select 
                    value={metodoPago} 
                    onChange={(e) => {
                      setMetodoPago(e.target.value)
                      setHabitacionSeleccionada(null) // Resetea habitación al cambiar método
                    }}
                    className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm font-medium text-slate-700 focus:outline-none focus:border-blue-500"
                  >
                    <option value="EFECTIVO">💵 Efectivo</option>
                    <option value="YAPE">📱 Yape / Plin</option>
                    <option value="TARJETA">💳 Tarjeta Crédito/Débito</option>
                    <option value="CARGAR_HABITACION">🏠 Cargar a Habitación</option>
                  </select>
                </div>

                {/* Selector de Habitaciones - Se muestra solo si "Cargar a Habitación" está activo */}
                {metodoPago === 'CARGAR_HABITACION' && (
                  <div className="space-y-1.5 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    {habitacionesOcupadas.length > 0 ? (
                      <>
                        <label className="text-xs font-bold text-blue-700 uppercase tracking-wider">Selecciona Habitación</label>
                        <select 
                          value={habitacionSeleccionada || ''} 
                          onChange={(e) => setHabitacionSeleccionada(e.target.value ? parseInt(e.target.value) : null)}
                          className="w-full p-2.5 bg-white border border-blue-300 rounded-lg text-sm font-medium text-slate-700 focus:outline-none focus:border-blue-600"
                        >
                          <option value="">-- Selecciona una habitación --</option>
                          {habitacionesOcupadas.map(hab => (
                            <option key={hab.id} value={hab.checkin_actual_id}>
                              Hab. {hab.numero} (Checkin ID: {hab.checkin_actual_id})
                            </option>
                          ))}
                        </select>
                        <p className="text-xs text-blue-600 font-medium">El consumo se agregará a la deuda de hospedaje</p>
                      </>
                    ) : (
                      <p className="text-xs text-yellow-700 font-medium">⚠️ No hay habitaciones ocupadas disponibles para cargar consumos</p>
                    )}
                  </div>
                )}
              </>
            )}

            <div className="flex justify-between text-xl font-black pt-2">
              <span className="text-slate-700">Total:</span>
              <span className="text-green-600">S/ {total.toFixed(2)}</span>
            </div>
            
            <Button 
              className="w-full py-4 text-lg font-bold" 
              disabled={carrito.length === 0 || (metodoPago === 'CARGAR_HABITACION' && !habitacionSeleccionada)}
              onClick={finalizarVenta}
            >
              Procesar Pago
            </Button>
          </div>
        </Card>
      </div>
      </div>
    </>
  )
}