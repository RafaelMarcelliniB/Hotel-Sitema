import { useState } from 'react'
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
  const [saving, setSaving] = useState(false)

  if (user?.rol?.toLowerCase() !== 'admin') return null

  const close = () => { setModal(null); setSaving(false) }
  const update = (setter) => (event) => setter((current) => ({ ...current, [event.target.name]: event.target.value }))
  const submit = async (event, endpoint, data, reset, success) => {
    event.preventDefault()
    setSaving(true)
    try {
      await api.post(endpoint, data)
      alert(success)
      reset()
      close()
    } catch (error) {
      alert(error.response?.data?.detail || 'No se pudo guardar el registro.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-6 p-6">
      <div><h2 className="text-2xl font-bold text-slate-800">Administración</h2><p className="text-sm text-slate-500">Configuración de espacios y productos del sistema.</p></div>
      <div className="grid gap-4 md:grid-cols-3">
        <Card><h3 className="text-lg font-semibold text-slate-800">Habitaciones</h3><p className="mt-2 text-sm text-slate-500">Agrega habitaciones al mapa del hotel.</p><Button className="mt-5 w-full" onClick={() => setModal('room')}>Crear habitación</Button></Card>
        <Card><h3 className="text-lg font-semibold text-slate-800">Cochera</h3><p className="mt-2 text-sm text-slate-500">Agrega espacios para vehículos.</p><Button className="mt-5 w-full" onClick={() => setModal('parking')}>Crear espacio</Button></Card>
        <Card><h3 className="text-lg font-semibold text-slate-800">Market</h3><p className="mt-2 text-sm text-slate-500">Registra objetos disponibles para venta.</p><Button className="mt-5 w-full" onClick={() => setModal('product')}>Crear producto</Button></Card>
      </div>

      {modal && <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-4"><div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl">
        {modal === 'room' && <form className="space-y-4" onSubmit={(event) => submit(event, '/hotel/habitaciones/', { ...room, piso: Number(room.piso), tarifa_dia: Number(room.tarifa_dia), tarifa_noche: Number(room.tarifa_noche), tarifa_madrugada: Number(room.tarifa_madrugada) }, () => setRoom(initialRoom), 'Habitación creada correctamente.')}>
          <h3 className="text-xl font-bold">Crear habitación</h3><div className="grid grid-cols-2 gap-3"><Field label="Número"><Input name="numero" value={room.numero} onChange={update(setRoom)} required /></Field><Field label="Piso"><Input name="piso" type="number" min="1" value={room.piso} onChange={update(setRoom)} required /></Field></div>
          <div className="grid grid-cols-2 gap-3"><Field label="Tipo"><select name="tipo" value={room.tipo} onChange={update(setRoom)} className="w-full rounded-xl border border-slate-200 px-4 py-3">{[['SIMPLE','Simple'],['DOBLE','Doble'],['SUITE','Suite'],['MATRI','Matri'],['MATRI_VIP','Matri VIP'],['BLUE','Blue'],['RED','Red'],['TRIPLE','Triple'],['CAFETIN','Cafetín']].map(([value,label]) => <option key={value} value={value}>{label}</option>)}</select></Field><Field label="Tipo de cama"><select name="tipo_cama" value={room.tipo_cama} onChange={update(setRoom)} className="w-full rounded-xl border border-slate-200 px-4 py-3"><option value="DOS_PLAZAS">Dos plazas</option><option value="QUEEN">Queen</option><option value="KING">King</option></select></Field></div>
          <Field label="Marca de TV"><select name="marca_tv" value={room.marca_tv} onChange={update(setRoom)} className="w-full rounded-xl border border-slate-200 px-4 py-3">{['JVC','JVC_V','HISENSE','SM'].map((value) => <option key={value} value={value}>{value}</option>)}</select></Field><div className="grid grid-cols-3 gap-3"><Field label="Tarifa día"><Input name="tarifa_dia" type="number" step="0.01" min="0" value={room.tarifa_dia} onChange={update(setRoom)} required /></Field><Field label="Tarifa noche"><Input name="tarifa_noche" type="number" step="0.01" min="0" value={room.tarifa_noche} onChange={update(setRoom)} required /></Field><Field label="Tarifa madrugada"><Input name="tarifa_madrugada" type="number" step="0.01" min="0" value={room.tarifa_madrugada} onChange={update(setRoom)} required /></Field></div><FormActions saving={saving} onCancel={close} />
        </form>}
        {modal === 'parking' && <form className="space-y-4" onSubmit={(event) => submit(event, '/cochera/espacios/', parking, () => setParking(initialParking), 'Espacio de cochera creado correctamente.')}><h3 className="text-xl font-bold">Crear espacio de cochera</h3><Field label="Número"><Input name="numero" value={parking.numero} onChange={update(setParking)} required /></Field><Field label="Tipo"><select name="tipo" value={parking.tipo} onChange={update(setParking)} className="w-full rounded-xl border border-slate-200 px-4 py-3"><option value="AUTO">Auto</option><option value="MOTO">Moto</option><option value="BUS">Bus</option></select></Field><FormActions saving={saving} onCancel={close} /></form>}
        {modal === 'product' && <form className="space-y-4" onSubmit={(event) => submit(event, '/market/productos/', { ...product, precio_unitario: Number(product.precio_unitario), stock_almacen: Number(product.stock_almacen), stock_recepcion: Number(product.stock_recepcion), stock_refrigeradora: Number(product.stock_refrigeradora), stock_minimo: Number(product.stock_minimo) }, () => setProduct(initialProduct), 'Producto creado correctamente.')}><h3 className="text-xl font-bold">Crear producto para Market</h3><Field label="Nombre"><Input name="nombre" value={product.nombre} onChange={update(setProduct)} required /></Field><Field label="Categoría"><select name="categoria" value={product.categoria} onChange={update(setProduct)} className="w-full rounded-xl border border-slate-200 px-4 py-3">{['BEBIDA','ALCOHOL','SNACK','HIGIENE','CHICLE','CARAMELO','GALLETA','PRESERVATIVO','CUBIERTOS','VASITOS'].map((value) => <option key={value} value={value}>{value}</option>)}</select></Field><div className="grid grid-cols-2 gap-3"><Field label="Precio unitario"><Input name="precio_unitario" type="number" step="0.01" min="0" value={product.precio_unitario} onChange={update(setProduct)} required /></Field><Field label="Stock mínimo"><Input name="stock_minimo" type="number" min="0" value={product.stock_minimo} onChange={update(setProduct)} /></Field></div><div className="grid grid-cols-3 gap-3"><Field label="Almacén"><Input name="stock_almacen" type="number" min="0" value={product.stock_almacen} onChange={update(setProduct)} /></Field><Field label="Recepción"><Input name="stock_recepcion" type="number" min="0" value={product.stock_recepcion} onChange={update(setProduct)} /></Field><Field label="Refrigeradora"><Input name="stock_refrigeradora" type="number" min="0" value={product.stock_refrigeradora} onChange={update(setProduct)} /></Field></div><FormActions saving={saving} onCancel={close} /></form>}
      </div></div>}
    </div>
  )
}
