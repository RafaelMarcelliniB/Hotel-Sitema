import { useForm } from 'react-hook-form'
import { Modal } from '../ui/Modal'
import Input from '../ui/Input'
import Button from '../ui/Button'
import Select from '../ui/Select'

const CATEGORIAS = [
  ['SERVICIOS', 'Servicios'],
  ['INSUMOS_LIMPIEZA', 'Insumos/Limpieza'],
  ['COMPRAS_MARKET', 'Compras Market'],
  ['DEVOLUCION', 'Devolución'],
  ['GASTOS_VARIOS', 'Gastos Varios'],
]

export default function ModalEgresoCaja({ open, onClose, onSubmit, isSaving }) {
  const { register, handleSubmit, reset } = useForm({
    defaultValues: { categoria: 'SERVICIOS', tipo_caja: 'EFECTIVO' },
  })

  const submit = async (data) => {
    await onSubmit({ ...data, monto: Number(data.monto) })
    reset({ categoria: 'SERVICIOS', tipo_caja: 'EFECTIVO' })
  }

  return (
    <Modal open={open} title="Registrar Egreso" onClose={onClose}>
      <form onSubmit={handleSubmit(submit)} className="space-y-4">
        <div>
          <label className="text-sm font-bold text-slate-700">Categoría</label>
          <Select {...register('categoria')}>
            {CATEGORIAS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </Select>
        </div>
        <div>
          <label className="text-sm font-bold text-slate-700">Descripción *</label>
          <Input {...register('descripcion', { required: true })} placeholder="Detalle del gasto" />
        </div>
        <div>
          <label className="text-sm font-bold text-slate-700">Monto (S/) *</label>
          <Input type="number" step="0.01" min="0.01" {...register('monto', { required: true, min: 0.01 })} />
        </div>
        <div>
          <label className="text-sm font-bold text-slate-700">Método de Pago</label>
          <Select {...register('tipo_caja')}>
            <option value="EFECTIVO">Efectivo</option>
            <option value="YAPE">Yape</option>
          </Select>
        </div>
        <div className="flex justify-end gap-2 pt-2">
          <Button type="button" onClick={onClose} className="bg-slate-200 text-slate-700">Cancelar</Button>
          <Button type="submit" disabled={isSaving}>{isSaving ? 'Guardando...' : 'Registrar Egreso'}</Button>
        </div>
      </form>
    </Modal>
  )
}
