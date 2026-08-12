import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import Card from '../components/ui/Card'
import { Input } from '../components/ui/Input'
import { Button } from '../components/ui/Button'
import CajaBlockedModal from '../components/ui/CajaBlockedModal'
import { useProductos } from '../hooks/useProductos'
import { useHabitaciones } from '../hooks/useHabitaciones'
import { useCajaBlocked } from '../hooks/useCajaBlocked'
import { useAuthStore } from '../store/authStore'
import Spinner from '../components/ui/Spinner'
import api from '../api/axiosConfig'

function TemplatesDropdown() {
  const [showTemplates, setShowTemplates] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    function onDocClick(e) {
      if (!ref.current) return
      if (!ref.current.contains(e.target)) setShowTemplates(false)
    }
    document.addEventListener('click', onDocClick)
    return () => document.removeEventListener('click', onDocClick)
  }, [])

  async function downloadTemplate(format) {
    try {
      const resp = await api.get(`/market/productos/plantilla/${format}/`, { responseType: 'blob' })
      const blob = new Blob([resp.data], { type: resp.headers['content-type'] })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = format === 'xlsx' ? 'plantilla_productos.xlsx' : 'plantilla_productos.csv'
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
      setShowTemplates(false)
    } catch (e) {
      console.error('Error al descargar plantilla', e)
      alert('Error al descargar plantilla')
    }
  }

  return (
    <div className="relative inline-block text-left" ref={ref}>
      <button
        type="button"
        onClick={() => setShowTemplates((v) => !v)}
        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg text-sm flex items-center gap-2"
      >
        📄 Plantilla
        <span className="ml-1">▾</span>
      </button>

      {showTemplates && (
        <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-100 z-50 py-1">
          <button onClick={() => downloadTemplate('xlsx')} className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">📊 Plantilla Excel (.xlsx)</button>
          <button onClick={() => downloadTemplate('csv')} className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">📝 Plantilla CSV (.csv)</button>
        </div>
      )}
    </div>
  )
}

export default function Market() {
  const navigate = useNavigate()
    const { productos, isLoading, procesarVenta, importarProductos, previewProductos } = useProductos()
    const { habitaciones } = useHabitaciones()
    const { cajaActiva } = useCajaBlocked()
    const user = useAuthStore(state => state.user)

    const [filtro, setFiltro] = useState('')
    const [carrito, setCarrito] = useState([])
    const [showCajaBlocked, setShowCajaBlocked] = useState(false)
    const [showImportModal, setShowImportModal] = useState(false)
    const [selectedFile, setSelectedFile] = useState(null)
    const [previewRows, setPreviewRows] = useState([])
    const [importing, setImporting] = useState(false)

    const [metodoPago, setMetodoPago] = useState('EFECTIVO')
    const [habitacionSeleccionada, setHabitacionSeleccionada] = useState(null)

    const habitacionesOcupadas = habitaciones.filter(h => h.estado_ocupacion === 'OCUPADO' && h.checkin_actual_id)
    const productosFiltrados = productos.filter(p => p.nombre.toLowerCase().includes(filtro.toLowerCase()))

    const agregarAlCarrito = (producto) => {
      if (producto.stock_actual <= 0) return alert('Sin stock disponible')
      setCarrito(prev => {
        const existe = prev.find(item => item.id === producto.id)
        if (existe) {
          if (existe.cantidad >= producto.stock_actual) {
            alert(`No puedes agregar más unidades. Stock máximo: ${producto.stock_actual}`)
            return prev
          }
          return prev.map(item => item.id === producto.id ? { ...item, cantidad: item.cantidad + 1 } : item)
        }
        return [...prev, { ...producto, cantidad: 1 }]
      })
    }

    const total = carrito.reduce((acc, item) => acc + (item.precio_unitario * item.cantidad), 0)

    const incrementarCantidad = (productoId, stock_maximo) => {
      setCarrito(prev => prev.map(item => item.id === productoId && item.cantidad < stock_maximo ? { ...item, cantidad: item.cantidad + 1 } : item))
    }

    const decrementarCantidad = (productoId) => {
      setCarrito(prev => prev.map(item => item.id === productoId ? { ...item, cantidad: Math.max(0, item.cantidad - 1) } : item).filter(i => i.cantidad > 0))
    }

    const removerDelCarrito = (productoId) => setCarrito(prev => prev.filter(item => item.id !== productoId))

    const getEstadoStock = (stock) => {
      if (stock === 0) return 'agotado'
      if (stock <= 3) return 'bajo'
      return 'disponible'
    }

    const finalizarVenta = async () => {
      if (carrito.length === 0) return
      if (!cajaActiva) {
        setShowCajaBlocked(true)
        return
      }
      if (metodoPago === 'CARGAR_HABITACION' && !habitacionSeleccionada) {
        alert('Por favor, selecciona una habitación para cargar los consumos')
        return
      }

      try {
        await procesarVenta({
          tipo_venta: metodoPago === 'CARGAR_HABITACION' ? 'CARGADO_HABITACION' : 'DIRECTO',
          metodo_pago: metodoPago === 'CARGAR_HABITACION' ? 'EFECTIVO' : metodoPago,
          checkin_vinculado_id: metodoPago === 'CARGAR_HABITACION' ? habitacionSeleccionada : null,
          detalles: carrito.map(i => ({ producto_id: i.id, cantidad: i.cantidad }))
        })
        setCarrito([])
        setMetodoPago('EFECTIVO')
        setHabitacionSeleccionada(null)
        alert('✅ Venta realizada con éxito. Stock actualizado.')
      } catch (err) {
        console.error(err)
        if (err.response?.status === 400 && err.response?.data?.detail?.includes('Debe aperturar')) {
          setShowCajaBlocked(true)
        } else {
          const mensajeError = err.response?.data?.detail || 'Error al procesar la venta'
          alert(`⚠️ Atención: ${mensajeError}`)
        }
      }
    }

    if (isLoading) return <Spinner />

    return (
      <>
        <CajaBlockedModal
          isOpen={showCajaBlocked}
          onClose={() => setShowCajaBlocked(false)}
          onNavigateToCaja={() => { setShowCajaBlocked(false); navigate('/caja') }}
        />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            <Card>
              <div className="flex items-center gap-3">
                <div className="flex-1">
                  <Input placeholder="Buscar producto..." value={filtro} onChange={(e) => setFiltro(e.target.value)} />
                </div>
                {(user?.rol?.toLowerCase() === 'admin' || user?.rol?.toLowerCase() === 'administrador') && (
                  <div className="flex items-center gap-2">
                    <Button className="bg-green-600" onClick={() => setShowImportModal(true)}>📥 Cargar Productos (Excel/CSV)</Button>

                    {/* Dropdown Plantilla */}
                    <TemplatesDropdown />
                  </div>
                )}
              </div>
            </Card>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {productosFiltrados.map(p => {
                const estadoStock = getEstadoStock(p.stock_actual)
                const isDisabled = estadoStock === 'agotado'
                return (
                  <div key={p.id} onClick={() => !isDisabled && agregarAlCarrito(p)} className={`p-4 rounded-xl shadow-sm border flex flex-col justify-between transition-all ${isDisabled ? 'bg-gray-100 border-gray-300 opacity-50 cursor-not-allowed' : 'bg-white hover:border-blue-500 cursor-pointer'}`}>
                    <div>
                      <h4 className="font-bold text-slate-800">{p.nombre}</h4>
                      <p className={`text-sm mt-1 font-semibold ${estadoStock === 'agotado' ? 'text-gray-400' : estadoStock === 'bajo' ? 'text-red-500' : 'text-gray-500'}`}>
                        Stock: {p.stock_actual}{estadoStock === 'bajo' && ' ⚠️'}
                      </p>
                    </div>
                    <p className={`font-bold mt-2 text-lg ${isDisabled ? 'text-gray-500 italic' : 'text-blue-600'}`}>{isDisabled ? 'Agotado' : `S/ ${Number(p.precio_unitario).toFixed(2)}`}</p>
                  </div>
                )
              })}
            </div>

            {showImportModal && (
              <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-4">
                <div className="w-full max-w-2xl rounded-3xl bg-white p-6 shadow-2xl">
                  <div className="mb-4 flex items-center justify-between gap-3">
                    <h3 className="text-lg font-bold text-slate-900">Cargar productos desde Excel</h3>
                    <button className="rounded-full px-3 py-1 text-slate-500 hover:bg-slate-100" onClick={() => { setShowImportModal(false); setSelectedFile(null); setPreviewRows([]) }} type="button">×</button>
                  </div>

                  <div className="space-y-4">
                    <input type="file" accept=".xlsx,.xls,.csv" onChange={async (e) => {
                      const file = e.target.files?.[0]
                      if (!file) return
                      setSelectedFile(file)
                      try {
                        const resp = await previewProductos(file)
                        setPreviewRows(resp.preview || [])
                      } catch (err) {
                        alert('Error al previsualizar: ' + (err.response?.data?.detail || err.message))
                      }
                    }} />

                    <div className="max-h-64 overflow-auto border rounded p-2">
                      {previewRows.length === 0 ? (
                        <p className="text-sm text-gray-500">Sube un archivo para ver una previsualización (hasta 20 filas).</p>
                      ) : (
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="text-left">
                              <th className="pr-2">Fila</th>
                              <th>Nombre</th>
                              <th>Categoria</th>
                              <th>Precio</th>
                              <th>Stock</th>
                            </tr>
                          </thead>
                          <tbody>
                            {previewRows.map(r => (
                              <tr key={r.fila} className="border-t">
                                <td className="pr-2">{r.fila}</td>
                                <td>{r.Nombre}</td>
                                <td>{r.Categoria}</td>
                                <td>{r['Precio Unitario']}</td>
                                <td>{r['Stock Actual']}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      )}
                    </div>

                    <div className="flex justify-end gap-3">
                      <button className="px-4 py-2 bg-gray-200 rounded" onClick={() => { setShowImportModal(false); setSelectedFile(null); setPreviewRows([]) }}>Cancelar</button>
                      <button className="px-4 py-2 bg-green-600 text-white rounded inline-flex items-center" disabled={!selectedFile || importing} onClick={async () => {
                        if (!selectedFile) return alert('Selecciona un archivo')
                        setImporting(true)
                        try {
                          const resp = await importarProductos(selectedFile)
                          alert(`Importado: ${resp.created} creados, ${resp.updated} actualizados`)
                          setShowImportModal(false)
                          setSelectedFile(null)
                          setPreviewRows([])
                        } catch (err) {
                          alert('Error al importar: ' + (err.response?.data?.detail || JSON.stringify(err.response?.data) || err.message))
                        } finally {
                          setImporting(false)
                        }
                      }}>
                        {importing ? (<><Spinner className="mr-2" /> Importando...</>) : 'Confirmar Importación'}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

          </div>

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
                          <button onClick={() => decrementarCantidad(item.id)} className="w-6 h-6 rounded bg-red-100 text-red-600 font-bold hover:bg-red-200 transition flex items-center justify-center" title="Disminuir cantidad">−</button>
                          <span className="w-6 text-center font-semibold text-slate-700">{item.cantidad}</span>
                          <button onClick={() => incrementarCantidad(item.id, item.stock_actual)} className="w-6 h-6 rounded bg-green-100 text-green-600 font-bold hover:bg-green-200 transition flex items-center justify-center" title="Aumentar cantidad" disabled={item.cantidad >= item.stock_actual}>+</button>
                        </div>
                      </div>
                      <div className="text-right mr-2">
                        <span className="font-semibold text-slate-900">S/ {(item.precio_unitario * item.cantidad).toFixed(2)}</span>
                      </div>
                      <button onClick={() => removerDelCarrito(item.id)} className="w-6 h-6 rounded bg-slate-100 text-slate-600 hover:bg-slate-200 hover:text-red-600 transition flex items-center justify-center opacity-0 group-hover:opacity-100" title="Remover producto">🗑️</button>
                    </div>
                  ))}
                  {carrito.length === 0 && <p className="text-center text-gray-400 py-10">Carrito vacío</p>}
                </div>
              </div>

              <div className="mt-6 pt-4 border-t space-y-4">
                {carrito.length > 0 && (
                  <>
                    <div className="space-y-1.5">
                      <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Método de Pago</label>
                      <select value={metodoPago} onChange={(e) => { setMetodoPago(e.target.value); setHabitacionSeleccionada(null) }} className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm font-medium text-slate-700 focus:outline-none focus:border-blue-500">
                        <option value="EFECTIVO">💵 Efectivo</option>
                        <option value="YAPE">📱 Yape / Plin</option>
                        <option value="TARJETA">💳 Tarjeta Crédito/Débito</option>
                        <option value="CARGAR_HABITACION">🏠 Cargar a Habitación</option>
                      </select>
                    </div>

                    {metodoPago === 'CARGAR_HABITACION' && (
                      <div className="space-y-1.5 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                        {habitacionesOcupadas.length > 0 ? (
                          <>
                            <label className="text-xs font-bold text-blue-700 uppercase tracking-wider">Selecciona Habitación</label>
                            <select value={habitacionSeleccionada || ''} onChange={(e) => setHabitacionSeleccionada(e.target.value ? parseInt(e.target.value) : null)} className="w-full p-2.5 bg-white border border-blue-300 rounded-lg text-sm font-medium text-slate-700 focus:outline-none focus:border-blue-600">
                              <option value="">-- Selecciona una habitación --</option>
                              {habitacionesOcupadas.map(hab => (<option key={hab.id} value={hab.checkin_actual_id}>Hab. {hab.numero} (Checkin ID: {hab.checkin_actual_id})</option>))}
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

                <Button className="w-full py-4 text-lg font-bold" disabled={carrito.length === 0 || (metodoPago === 'CARGAR_HABITACION' && !habitacionSeleccionada)} onClick={finalizarVenta}>Procesar Pago</Button>
              </div>
            </Card>
          </div>
        </div>
      </>
    )
  }