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

const UBICACIONES = [
  { value: 'TODOS', label: 'Todos', icon: '📦', badge: 'bg-slate-100 text-slate-700' },
  { value: 'ALMACEN', label: 'Almacén', icon: '📦', badge: 'bg-blue-100 text-blue-700' },
  { value: 'RECEPCION', label: 'Recepción', icon: '🛎️', badge: 'bg-emerald-100 text-emerald-700' },
  { value: 'REFRIGERADORA', label: 'Refrigeradora', icon: '❄️', badge: 'bg-cyan-100 text-cyan-700' },
]

const CATEGORIAS = [
  { value: 'TODAS', label: 'Todas' },
  { value: 'BEBIDA', label: 'Bebidas' },
  { value: 'ALCOHOL', label: 'Bebidas Alcohólicas' },
  { value: 'SNACK', label: 'Snacks' },
  { value: 'HIGIENE', label: 'Higiene Personal' },
  { value: 'PRESERVATIVO_CIGARRILLO', label: 'Preservativos / Cigarrillos' },
  { value: 'CUBIERTOS_OTROS', label: 'Cubiertos / Otros' },
]

const STOCK_FIELDS = {
  ALMACEN: 'stock_almacen',
  RECEPCION: 'stock_recepcion',
  REFRIGERADORA: 'stock_refrigeradora',
}

function stockPorUbicacion(producto, ubicacion) {
  const toNumber = (value) => {
    const parsed = Number(value)
    return Number.isFinite(parsed) ? parsed : 0
  }

  const stockAlmacen = toNumber(producto.stock_almacen)
  const stockRecepcion = toNumber(producto.stock_recepcion)
  const stockRefrigeradora = toNumber(producto.stock_refrigeradora)
  const stockTotalReal = stockAlmacen + stockRecepcion + stockRefrigeradora

  if (ubicacion === 'TODOS') {
    return stockTotalReal
  }

  return toNumber(producto[STOCK_FIELDS[ubicacion]])
}

function ubicacionesDisponibles(producto) {
  return UBICACIONES.slice(1).filter(({ value }) => stockPorUbicacion(producto, value) > 0)
}

function categoriaCoincide(producto, categoria) {
  if (categoria === 'TODAS') return true
  if (categoria === 'PRESERVATIVO_CIGARRILLO') return ['PRESERVATIVO', 'CIGARRILLO', 'CIGARRILLOS'].includes(producto.categoria)
  if (categoria === 'CUBIERTOS_OTROS') return ['CUBIERTOS', 'VASITOS', 'CHICLE', 'CARAMELO', 'GALLETA'].includes(producto.categoria)
  return producto.categoria === categoria
}

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
    const { productos, isLoading, procesarVenta, importarProductos, previewProductos, transferirStock, isTransferring, refetchProductos } = useProductos()
    const { habitaciones } = useHabitaciones()
    const { cajaActiva } = useCajaBlocked()
    const user = useAuthStore(state => state.user)

    const [filtro, setFiltro] = useState('')
    const [ubicacionFiltro, setUbicacionFiltro] = useState('ALMACEN')
    const [categoriaFiltro, setCategoriaFiltro] = useState('TODAS')
    const [carrito, setCarrito] = useState([])
    const [showCajaBlocked, setShowCajaBlocked] = useState(false)
    const [showImportModal, setShowImportModal] = useState(false)
    const [showTransferModal, setShowTransferModal] = useState(false)
    const [selectedFile, setSelectedFile] = useState(null)
    const [previewRows, setPreviewRows] = useState([])
    const [importing, setImporting] = useState(false)
    const [transferForm, setTransferForm] = useState({
      productoId: '',
      origen: 'ALMACEN',
      destino: 'RECEPCION',
      cantidad: '1',
      motivo: 'Transferencia de stock'
    })

    const [metodoPago, setMetodoPago] = useState('EFECTIVO')
    const [habitacionSeleccionada, setHabitacionSeleccionada] = useState(null)

    const habitacionesOcupadas = habitaciones.filter(h => h.estado_ocupacion === 'OCUPADO' && h.checkin_actual_id)
    const productosFiltrados = productos.filter(p => (
      p.nombre.toLowerCase().includes(filtro.toLowerCase()) &&
      categoriaCoincide(p, categoriaFiltro) &&
      (ubicacionFiltro === 'TODOS' || stockPorUbicacion(p, ubicacionFiltro) > 0)
    ))

    const agregarAlCarrito = (producto) => {
      const ubicacion = ubicacionFiltro === 'TODOS'
        ? ubicacionesDisponibles(producto)[0]?.value
        : ubicacionFiltro
      const stockDisponible = ubicacion ? stockPorUbicacion(producto, ubicacion) : 0
      if (!ubicacion || stockDisponible <= 0) return alert('Sin stock disponible')
      setCarrito(prev => {
        const existe = prev.find(item => item.id === producto.id && item.ubicacion_stock === ubicacion)
        if (existe) {
          if (existe.cantidad >= stockDisponible) {
            alert(`No puedes agregar más unidades. Stock máximo: ${stockDisponible}`)
            return prev
          }
          return prev.map(item => item.id === producto.id && item.ubicacion_stock === ubicacion ? { ...item, cantidad: item.cantidad + 1 } : item)
        }
        return [...prev, { ...producto, cantidad: 1, ubicacion_stock: ubicacion }]
      })
    }

    const total = carrito.reduce((acc, item) => acc + (item.precio_unitario * item.cantidad), 0)

    const productoTransferencia = productos.find(p => Number(p.id) === Number(transferForm.productoId)) || null
    const origenTransferOptions = productoTransferencia
      ? UBICACIONES.slice(1).filter(u => (productoTransferencia[STOCK_FIELDS[u.value]] ?? 0) > 0)
      : UBICACIONES.slice(1)
    const destinoTransferOptions = UBICACIONES.slice(1).filter(u => u.value !== transferForm.origen)

    const handleTransferStock = async () => {
      if (!transferForm.productoId) {
        alert('Selecciona un producto para transferir')
        return
      }
      if (transferForm.origen === transferForm.destino) {
        alert('El origen y destino deben ser distintos')
        return
      }
      const cantidad = Number(transferForm.cantidad)
      if (!Number.isFinite(cantidad) || cantidad <= 0) {
        alert('La cantidad debe ser mayor que 0')
        return
      }
      const stockOrigen = Number(productoTransferencia?.[STOCK_FIELDS[transferForm.origen]] ?? 0)
      if (cantidad > stockOrigen) {
        alert(`No hay suficiente stock en ${UBICACIONES.find(u => u.value === transferForm.origen)?.label}. Disponible: ${stockOrigen}`)
        return
      }

      try {
        await transferirStock({
          productoId: transferForm.productoId,
          origen: transferForm.origen,
          destino: transferForm.destino,
          cantidad,
          motivo: transferForm.motivo || 'Transferencia de stock'
        })
        await refetchProductos()
        setShowTransferModal(false)
        setTransferForm({
          productoId: '',
          origen: 'ALMACEN',
          destino: 'RECEPCION',
          cantidad: '1',
          motivo: 'Transferencia de stock',
        })
        alert('✅ Transferencia registrada correctamente')
      } catch (err) {
        const mensajeError = err.response?.data?.detail || err.response?.data?.message || 'Error al transferir stock'
        alert(`⚠️ ${mensajeError}`)
      }
    }

    const incrementarCantidad = (productoId, ubicacion, stock_maximo) => {
      setCarrito(prev => prev.map(item => item.id === productoId && item.ubicacion_stock === ubicacion && item.cantidad < stock_maximo ? { ...item, cantidad: item.cantidad + 1 } : item))
    }

    const decrementarCantidad = (productoId, ubicacion) => {
      setCarrito(prev => prev.map(item => item.id === productoId && item.ubicacion_stock === ubicacion ? { ...item, cantidad: Math.max(0, item.cantidad - 1) } : item).filter(i => i.cantidad > 0))
    }

    const removerDelCarrito = (productoId, ubicacion) => setCarrito(prev => prev.filter(item => !(item.id === productoId && item.ubicacion_stock === ubicacion)))

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
          detalles: carrito.map(i => ({ producto_id: i.id, cantidad: i.cantidad, ubicacion_stock: i.ubicacion_stock }))
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
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                <div className="flex-1">
                  <Input placeholder="Buscar producto..." value={filtro} onChange={(e) => setFiltro(e.target.value)} />
                </div>
                {(user?.rol?.toLowerCase() === 'admin' || user?.rol?.toLowerCase() === 'administrador') && (
                  <div className="flex items-center gap-2 flex-wrap">
                    <Button className="bg-indigo-600 hover:bg-indigo-700" onClick={async () => { await refetchProductos(); setShowTransferModal(true) }}>🔁 Transferir stock</Button>
                    <Button className="bg-green-600" onClick={() => setShowImportModal(true)}>📥 Cargar Productos (Excel/CSV)</Button>

                    {/* Dropdown Plantilla */}
                    <TemplatesDropdown />
                  </div>
                )}
                </div>
                <div className="flex flex-wrap gap-2">
                  {UBICACIONES.map(ubicacion => (
                    <button key={ubicacion.value} type="button" onClick={() => setUbicacionFiltro(ubicacion.value)} className={`rounded-lg px-3 py-2 text-sm font-semibold transition ${ubicacionFiltro === ubicacion.value ? `${ubicacion.badge} ring-2 ring-offset-1 ring-current` : 'bg-slate-50 text-slate-500 hover:bg-slate-100'}`}>
                      {ubicacion.icon} {ubicacion.label}
                    </button>
                  ))}
                </div>
                <div className="flex flex-wrap gap-2">
                  {CATEGORIAS.map(categoria => (
                    <button key={categoria.value} type="button" onClick={() => setCategoriaFiltro(categoria.value)} className={`rounded-lg border px-3 py-1.5 text-xs font-semibold transition ${categoriaFiltro === categoria.value ? 'border-slate-800 bg-slate-800 text-white' : 'border-slate-200 bg-white text-slate-600 hover:border-slate-400'}`}>
                      {categoria.label}
                    </button>
                  ))}
                </div>
              </div>
            </Card>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {productosFiltrados.map(p => {
                const stock = stockPorUbicacion(p, ubicacionFiltro)
                const estadoStock = getEstadoStock(stock)
                const isDisabled = estadoStock === 'agotado'
                return (
                  <div key={p.id} onClick={() => !isDisabled && agregarAlCarrito(p)} className={`p-4 rounded-xl shadow-sm border flex flex-col justify-between transition-all ${isDisabled ? 'bg-gray-100 border-gray-300 opacity-50 cursor-not-allowed' : 'bg-white hover:border-blue-500 cursor-pointer'}`}>
                    <div>
                      <h4 className="font-bold text-slate-800">{p.nombre}</h4>
                      <div className="mt-2 flex flex-wrap gap-1">
                        {(ubicacionFiltro === 'TODOS' ? ubicacionesDisponibles(p) : UBICACIONES.filter(u => u.value === ubicacionFiltro)).map(ubicacion => (
                          <span key={ubicacion.value} className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${ubicacion.badge}`}>{ubicacion.icon} {ubicacion.label}</span>
                        ))}
                      </div>
                      <p className={`text-sm mt-1 font-semibold ${estadoStock === 'agotado' ? 'text-gray-400' : estadoStock === 'bajo' ? 'text-red-500' : 'text-gray-500'}`}>
                        Stock disponible: {stock}{estadoStock === 'bajo' && ' ⚠️'}
                      </p>
                    </div>
                    <p className={`font-bold mt-2 text-lg ${isDisabled ? 'text-gray-500 italic' : 'text-blue-600'}`}>{isDisabled ? 'Agotado' : `S/ ${Number(p.precio_unitario).toFixed(2)}`}</p>
                  </div>
                )
              })}
            </div>

            {showTransferModal && (
              <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-4">
                <div className="w-full max-w-xl rounded-3xl bg-white p-6 shadow-2xl">
                  <div className="mb-4 flex items-center justify-between gap-3">
                    <h3 className="text-lg font-bold text-slate-900">Transferir stock entre ubicaciones</h3>
                    <button className="rounded-full px-3 py-1 text-slate-500 hover:bg-slate-100" onClick={() => setShowTransferModal(false)} type="button">×</button>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <label className="mb-1 block text-xs font-bold uppercase tracking-wider text-slate-500">Producto</label>
                      <select value={transferForm.productoId} onChange={(e) => setTransferForm(prev => ({ ...prev, productoId: e.target.value }))} className="w-full rounded-lg border border-slate-200 bg-slate-50 p-2.5 text-sm text-slate-700">
                        <option value="">Selecciona un producto</option>
                        {productos.map(p => (
                          <option key={p.id} value={p.id}>{p.nombre}</option>
                        ))}
                      </select>
                    </div>

                    {productoTransferencia && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="mb-1 block text-xs font-bold uppercase tracking-wider text-slate-500">Origen</label>
                          <select value={transferForm.origen} onChange={(e) => setTransferForm(prev => ({ ...prev, origen: e.target.value, destino: e.target.value === 'ALMACEN' ? 'RECEPCION' : 'ALMACEN' }))} className="w-full rounded-lg border border-slate-200 bg-slate-50 p-2.5 text-sm text-slate-700">
                            {origenTransferOptions.map(u => (
                              <option key={u.value} value={u.value}>{u.label}</option>
                            ))}
                          </select>
                        </div>

                        <div>
                          <label className="mb-1 block text-xs font-bold uppercase tracking-wider text-slate-500">Destino</label>
                          <select value={transferForm.destino} onChange={(e) => setTransferForm(prev => ({ ...prev, destino: e.target.value }))} className="w-full rounded-lg border border-slate-200 bg-slate-50 p-2.5 text-sm text-slate-700">
                            {destinoTransferOptions.map(u => (
                              <option key={u.value} value={u.value}>{u.label}</option>
                            ))}
                          </select>
                        </div>
                      </div>
                    )}

                    {productoTransferencia && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="mb-1 block text-xs font-bold uppercase tracking-wider text-slate-500">Cantidad</label>
                          <input type="number" min="1" max={productoTransferencia[STOCK_FIELDS[transferForm.origen]] ?? 1} value={transferForm.cantidad} onChange={(e) => setTransferForm(prev => ({ ...prev, cantidad: e.target.value }))} className="w-full rounded-lg border border-slate-200 bg-slate-50 p-2.5 text-sm text-slate-700" />
                        </div>
                        <div>
                          <label className="mb-1 block text-xs font-bold uppercase tracking-wider text-slate-500">Stock disponible</label>
                          <div className="flex h-[46px] items-center rounded-lg border border-slate-200 bg-slate-100 px-3 text-sm font-semibold text-slate-700">
                            {productoTransferencia[STOCK_FIELDS[transferForm.origen]] ?? 0} unidades
                          </div>
                        </div>
                      </div>
                    )}

                    <div>
                      <label className="mb-1 block text-xs font-bold uppercase tracking-wider text-slate-500">Motivo</label>
                      <input value={transferForm.motivo} onChange={(e) => setTransferForm(prev => ({ ...prev, motivo: e.target.value }))} className="w-full rounded-lg border border-slate-200 bg-slate-50 p-2.5 text-sm text-slate-700" placeholder="Ej. Reposición de recepción" />
                    </div>

                    <div className="flex justify-end gap-3 pt-2">
                      <button type="button" className="rounded-lg bg-slate-200 px-4 py-2 text-sm font-semibold text-slate-700" onClick={() => setShowTransferModal(false)}>Cancelar</button>
                      <button type="button" disabled={isTransferring} className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-60" onClick={handleTransferStock}>
                        {isTransferring ? 'Transferiendo...' : 'Confirmar traslado'}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

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
                              <th>Almacén</th>
                              <th>Recepción</th>
                              <th>Refrigeradora</th>
                            </tr>
                          </thead>
                          <tbody>
                            {previewRows.map(r => (
                              <tr key={r.fila} className="border-t">
                                <td className="pr-2">{r.fila}</td>
                                <td>{r.Nombre}</td>
                                <td>{r.Categoria}</td>
                                <td>{r['Precio Unitario']}</td>
                                <td>{r['Stock Almacen']}</td>
                                <td>{r['Stock Recepcion']}</td>
                                <td>{r['Stock Refrigeradora']}</td>
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
            <Card className="flex flex-col">
              <div>
                <h3 className="text-lg font-bold mb-4">Resumen de Venta</h3>
                <div className="space-y-3 min-h-[260px] pr-1">
                  {carrito.map(item => (
                    <div key={`${item.id}-${item.ubicacion_stock}`} className="flex justify-between items-center text-sm border-b pb-2 group">
                      <div className="flex-1">
                        <p className="font-medium text-slate-700">{item.nombre}</p>
                        <p className="text-[11px] font-semibold text-slate-500">{UBICACIONES.find(u => u.value === item.ubicacion_stock)?.label}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <button onClick={() => decrementarCantidad(item.id, item.ubicacion_stock)} className="w-6 h-6 rounded bg-red-100 text-red-600 font-bold hover:bg-red-200 transition flex items-center justify-center" title="Disminuir cantidad">−</button>
                          <span className="w-6 text-center font-semibold text-slate-700">{item.cantidad}</span>
                          <button onClick={() => incrementarCantidad(item.id, item.ubicacion_stock, stockPorUbicacion(item, item.ubicacion_stock))} className="w-6 h-6 rounded bg-green-100 text-green-600 font-bold hover:bg-green-200 transition flex items-center justify-center" title="Aumentar cantidad" disabled={item.cantidad >= stockPorUbicacion(item, item.ubicacion_stock)}>+</button>
                        </div>
                      </div>
                      <div className="text-right mr-2">
                        <span className="font-semibold text-slate-900">S/ {(item.precio_unitario * item.cantidad).toFixed(2)}</span>
                      </div>
                      <button onClick={() => removerDelCarrito(item.id, item.ubicacion_stock)} className="w-6 h-6 rounded bg-slate-100 text-slate-600 hover:bg-slate-200 hover:text-red-600 transition flex items-center justify-center opacity-0 group-hover:opacity-100" title="Remover producto">🗑️</button>
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