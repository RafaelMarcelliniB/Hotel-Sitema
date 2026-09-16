import { useEffect, useState } from 'react'
import api from '../api/axiosConfig'
import { useAuthStore } from '../store/authStore'
import Card from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'

const initialRoom = {
  numero: '', piso: '1', tipo: 'SIMPLE', marca_tv: 'JVC', tipo_cama: 'DOS_PLAZAS',
  tarifa_dia: '', tarifa_noche: '', tarifa_madrugada: '',
}
const initialParking = { numero: '', tipo: 'AUTO' }
const initialProduct = { nombre: '', categoria: 'BEBIDA', precio_unitario: '', stock_almacen: '0', stock_recepcion: '0', stock_refrigeradora: '0', stock_minimo: '0' }

function Field({ label, children }) {
  return <label className="block space-y-1 text-sm font-medium text-slate-700"><span>{label}</span>{children}</label>
}

function FormActions({ saving, onCancel }) {
  return <div className="flex justify-end gap-2 pt-2"><Button type="button" variant="ghost" onClick={onCancel}>Cancelar</Button><Button type="submit" disabled={saving}>{saving ? 'Guardando...' : 'Guardar'}</Button></div>
}

export default function Administracion() {
  const user = useAuthStore((state) => state.user)
  const [modal, setModal] = useState(null)
  const [room, setRoom] = useState(initialRoom)
  const [parking, setParking] = useState(initialParking)
  const [product, setProduct] = useState(initialProduct)
  const [rooms, setRooms] = useState([])
  const [parkingSpaces, setParkingSpaces] = useState([])
  const [products, setProducts] = useState([])
  const [editing, setEditing] = useState(null)
  const [saving, setSaving] = useState(false)

  if (user?.rol?.toLowerCase() !== 'admin') return null

  const loadData = async () => {
    const [roomsResponse, parkingResponse, productsResponse] = await Promise.all([
      api.get('/hotel/habitaciones/'),
      api.get('/cochera/espacios/'),
      api.get('/market/productos/'),
    ])
    setRooms(roomsResponse.data || [])
    setParkingSpaces(parkingResponse.data || [])
    setProducts(productsResponse.data || [])
  }

  useEffect(() => { loadData().catch(() => {}) }, [])

  const close = () => { setModal(null); setEditing(null); setSaving(false) }
  const update = (setter) => (event) => setter((current) => ({ ...current, [event.target.name]: event.target.value }))
  const submit = async (event, endpoint, data, reset, success) => {
    event.preventDefault()
    setSaving(true)
    try {
      if (editing) await api.patch(`${endpoint}${editing.id}/`, data)
      else await api.post(endpoint, data)
      alert(editing ? success.replace('creada', 'actualizada').replace('creado', 'actualizado').replace('guardado', 'actualizado') : success)
      reset()
      close()
      await loadData()
    } catch (error) {
      alert(error.response?.data?.detail || 'No se pudo guardar el registro.')
    } finally {
      setSaving(false)
    }
  }

  const startCreate = (type) => {
    setEditing(null)
    if (type === 'room') setRoom(initialRoom)
    if (type === 'parking') setParking(initialParking)
    if (type === 'product') setProduct(initialProduct)
    setModal(type)
  }

  const startEdit = (type, item) => {
    setEditing({ type, id: item.id })
    if (type === 'room') setRoom({ numero: item.numero, piso: String(item.piso), tipo: item.tipo, marca_tv: item.marca_tv, tipo_cama: item.tipo_cama, tarifa_dia: String(item.tarifa_dia), tarifa_noche: String(item.tarifa_noche), tarifa_madrugada: String(item.tarifa_madrugada) })
    if (type === 'parking') setParking({ numero: item.numero, tipo: item.tipo, estado: item.estado })
    if (type === 'product') setProduct({ nombre: item.nombre, categoria: item.categoria, precio_unitario: String(item.precio_unitario), stock_almacen: String(item.stock_almacen), stock_recepcion: String(item.stock_recepcion), stock_refrigeradora: String(item.stock_refrigeradora), stock_minimo: String(item.stock_minimo) })
    setModal(type)
  }

  const remove = async (endpoint, id, label) => {
    if (!window.confirm(`¿Eliminar ${label}?`)) return
    try { await api.delete(`${endpoint}${id}/`); await loadData(); alert(`${label} eliminado correctamente.`) }
    catch (error) { alert(error.response?.data?.detail || `No se pudo eliminar el registro (HTTP ${error.response?.status || 'desconocido'}).`) }
  }

  return (
    <div className="space-y-6 p-6">
      <div><h2 className="text-2xl font-bold text-slate-800">Administración</h2><p className="text-sm text-slate-500">Configuración de espacios y productos del sistema.</p></div>
      <div className="grid gap-4 md:grid-cols-3">
        <Card><h3 className="text-lg font-semibold text-slate-800">Habitaciones</h3><p className="mt-2 text-sm text-slate-500">Agrega y administra habitaciones.</p><Button className="mt-5 w-full" onClick={() => startCreate('room')}>Crear habitación</Button></Card>
        <Card><h3 className="text-lg font-semibold text-slate-800">Cochera</h3><p className="mt-2 text-sm text-slate-500">Agrega y administra espacios.</p><Button className="mt-5 w-full" onClick={() => startCreate('parking')}>Crear espacio</Button></Card>
        <Card><h3 className="text-lg font-semibold text-slate-800">Market</h3><p className="mt-2 text-sm text-slate-500">Registra y administra productos.</p><Button className="mt-5 w-full" onClick={() => startCreate('product')}>Crear producto</Button></Card>
      </div>

      {[['Habitaciones', rooms, 'room', '/hotel/habitaciones/'], ['Espacios de cochera', parkingSpaces, 'parking', '/cochera/espacios/'], ['Productos Market', products, 'product', '/market/productos/']].map(([title, items, type, endpoint]) => (
        <Card key={title}><h3 className="mb-3 text-lg font-semibold text-slate-800">{title}</h3><div className="space-y-2">{items.map((item) => <div key={item.id} className="flex items-center justify-between rounded-lg border border-slate-200 px-3 py-2"><span className="text-sm text-slate-700">{type === 'room' ? `#${item.numero} - ${item.tipo}` : type === 'parking' ? `#${item.numero} - ${item.tipo}` : `${item.nombre} - S/ ${item.precio_unitario}`}</span><span className="flex gap-2"><Button variant="ghost" className="h-8 px-2 text-blue-600" onClick={() => startEdit(type, item)}>Editar</Button><Button variant="ghost" className="h-8 px-2 text-red-600" onClick={() => remove(endpoint, item.id, type === 'room' ? 'habitación' : type === 'parking' ? 'espacio' : 'producto')}>Eliminar</Button></span></div>)}</div></Card>
      ))}

      {modal && <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-4"><div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl">
        {modal === 'room' && <form className="space-y-4" onSubmit={(event) => submit(event, '/hotel/habitaciones/', { ...room, piso: Number(room.piso), tarifa_dia: Number(room.tarifa_dia), tarifa_noche: Number(room.tarifa_noche), tarifa_madrugada: Number(room.tarifa_madrugada) }, () => setRoom(initialRoom), 'Habitación creada correctamente.')}>
          <h3 className="text-xl font-bold">{editing ? 'Editar habitación' : 'Crear habitación'}</h3><div className="grid grid-cols-2 gap-3"><Field label="Número"><Input name="numero" value={room.numero} onChange={update(setRoom)} required /></Field><Field label="Piso"><Input name="piso" type="number" min="1" value={room.piso} onChange={update(setRoom)} required /></Field></div>
          <div className="grid grid-cols-2 gap-3"><Field label="Tipo"><select name="tipo" value={room.tipo} onChange={update(setRoom)} className="w-full rounded-xl border border-slate-200 px-4 py-3">{[['SIMPLE','Simple'],['DOBLE','Doble'],['SUITE','Suite'],['MATRI','Matri'],['MATRI_VIP','Matri VIP'],['BLUE','Blue'],['RED','Red'],['TRIPLE','Triple'],['CAFETIN','Cafetín']].map(([value,label]) => <option key={value} value={value}>{label}</option>)}</select></Field><Field label="Tipo de cama"><select name="tipo_cama" value={room.tipo_cama} onChange={update(setRoom)} className="w-full rounded-xl border border-slate-200 px-4 py-3"><option value="DOS_PLAZAS">Dos plazas</option><option value="QUEEN">Queen</option><option value="KING">King</option></select></Field></div>
          <Field label="Marca de TV"><select name="marca_tv" value={room.marca_tv} onChange={update(setRoom)} className="w-full rounded-xl border border-slate-200 px-4 py-3">{['JVC','JVC_V','HISENSE','SM'].map((value) => <option key={value} value={value}>{value}</option>)}</select></Field><div className="grid grid-cols-3 gap-3"><Field label="Tarifa día"><Input name="tarifa_dia" type="number" step="0.01" min="0" value={room.tarifa_dia} onChange={update(setRoom)} required /></Field><Field label="Tarifa noche"><Input name="tarifa_noche" type="number" step="0.01" min="0" value={room.tarifa_noche} onChange={update(setRoom)} required /></Field><Field label="Tarifa madrugada"><Input name="tarifa_madrugada" type="number" step="0.01" min="0" value={room.tarifa_madrugada} onChange={update(setRoom)} required /></Field></div><FormActions saving={saving} onCancel={close} />
        </form>}
        {modal === 'parking' && <form className="space-y-4" onSubmit={(event) => submit(event, '/cochera/espacios/', parking, () => setParking(initialParking), 'Espacio de cochera guardado correctamente.')}><h3 className="text-xl font-bold">{editing ? 'Editar espacio de cochera' : 'Crear espacio de cochera'}</h3><Field label="Número"><Input name="numero" value={parking.numero} onChange={update(setParking)} required /></Field><Field label="Tipo"><select name="tipo" value={parking.tipo} onChange={update(setParking)} className="w-full rounded-xl border border-slate-200 px-4 py-3"><option value="AUTO">Auto</option><option value="MOTO">Moto</option><option value="BUS">Bus</option></select></Field><FormActions saving={saving} onCancel={close} /></form>}
        {modal === 'product' && <form className="space-y-4" onSubmit={(event) => submit(event, '/market/productos/', { ...product, precio_unitario: Number(product.precio_unitario), stock_almacen: Number(product.stock_almacen), stock_recepcion: Number(product.stock_recepcion), stock_refrigeradora: Number(product.stock_refrigeradora), stock_minimo: Number(product.stock_minimo) }, () => setProduct(initialProduct), 'Producto guardado correctamente.')}><h3 className="text-xl font-bold">{editing ? 'Editar producto' : 'Crear producto para Market'}</h3><Field label="Nombre"><Input name="nombre" value={product.nombre} onChange={update(setProduct)} required /></Field><Field label="Categoría"><select name="categoria" value={product.categoria} onChange={update(setProduct)} className="w-full rounded-xl border border-slate-200 px-4 py-3">{['BEBIDA','ALCOHOL','SNACK','HIGIENE','CHICLE','CARAMELO','GALLETA','PRESERVATIVO','CUBIERTOS','VASITOS'].map((value) => <option key={value} value={value}>{value}</option>)}</select></Field><div className="grid grid-cols-2 gap-3"><Field label="Precio unitario"><Input name="precio_unitario" type="number" step="0.01" min="0" value={product.precio_unitario} onChange={update(setProduct)} required /></Field><Field label="Stock mínimo"><Input name="stock_minimo" type="number" min="0" value={product.stock_minimo} onChange={update(setProduct)} /></Field></div><div className="grid grid-cols-3 gap-3"><Field label="Almacén"><Input name="stock_almacen" type="number" min="0" value={product.stock_almacen} onChange={update(setProduct)} /></Field><Field label="Recepción"><Input name="stock_recepcion" type="number" min="0" value={product.stock_recepcion} onChange={update(setProduct)} /></Field><Field label="Refrigeradora"><Input name="stock_refrigeradora" type="number" min="0" value={product.stock_refrigeradora} onChange={update(setProduct)} /></Field></div><FormActions saving={saving} onCancel={close} /></form>}
      </div></div>}
    </div>
  )
}
