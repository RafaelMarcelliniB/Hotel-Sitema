import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { Modal } from '../ui/Modal'
import Input from '../ui/Input'
import Button from '../ui/Button'
import Select from '../ui/Select'
import api from '../../api/axiosConfig'

export default function ModalAjusteTarifa({ open, onClose, onSubmit, defaultCheckinId = '' }) {
  const { register, handleSubmit, reset, watch } = useForm({
    defaultValues: { accion: 'REEMBOLSO', tipo_caja: 'EFECTIVO', checkin_id: defaultCheckinId || '' },
  })
  const [checkins, setCheckins] = useState([])
  const [loadingCheckins, setLoadingCheckins] = useState(false)
  const checkinId = watch('checkin_id')
  const openedFromMovement = Boolean(defaultCheckinId)

  useEffect(() => {
    if (!open) return
    setLoadingCheckins(true)
    api.get('/hotel/checkin/activos/')
      .then(({ data }) => setCheckins(Array.isArray(data) ? data : []))
      .catch(() => setCheckins([]))
      .finally(() => setLoadingCheckins(false))
    reset({ accion: 'REEMBOLSO', tipo_caja: 'EFECTIVO', checkin_id: defaultCheckinId || '' })
  }, [open, defaultCheckinId, reset])

  const formatCheckin = (checkin) => {
    const habitacion = checkin.habitacion?.numero || 'Sin habitación'
    const huesped = [checkin.huesped?.nombre, checkin.huesped?.apellido].filter(Boolean).join(' ') || 'Sin huésped'
    return `Hab. ${habitacion} - ${huesped} (Check-in #${checkin.id})`
  }

  return (
    <Modal open={open} title="Ajustar Tarifa / Reembolsar" onClose={onClose}>
      <form onSubmit={handleSubmit((data) => onSubmit({ ...data, monto: Number(data.monto), checkin_id: Number(data.checkin_id) }))} className="space-y-4">
        <div>
          <label className="text-sm font-bold text-slate-700">Tipo de Acción</label>
          <Select {...register('accion')}>
            <option value="REEMBOLSO">Devolución por Sobrecobro</option>
            <option value="COBRO_ADICIONAL">Cobro Adicional por Diferencia</option>
          </Select>
        </div>
        <div>
          <label className="text-sm font-bold text-slate-700">Habitación / Huésped *</label>
          <Select {...register('checkin_id', { required: true })} disabled={openedFromMovement || loadingCheckins}>
            <option value="">{loadingCheckins ? 'Cargando Check-ins...' : 'Seleccionar Check-in'}</option>
            {checkins.map((checkin) => (
              <option key={checkin.id} value={checkin.id}>{formatCheckin(checkin)}</option>
            ))}
          </Select>
          {openedFromMovement && (
            <p className="mt-1 text-xs text-slate-500">Registro vinculado automáticamente desde el movimiento seleccionado.</p>
          )}
        </div>
        <div>
          <label className="text-sm font-bold text-slate-700">Monto a Ajustar (S/) *</label>
          <Input type="number" step="0.01" min="0.01" {...register('monto', { required: true, min: 0.01 })} />
        </div>
        <div>
          <label className="text-sm font-bold text-slate-700">Motivo / Justificación *</label>
          <textarea className="w-full rounded-xl border border-slate-200 px-4 py-3 text-sm" rows="3" {...register('motivo', { required: true })} placeholder="Corrección por error de digitación en tarifa" />
        </div>
        <div>
          <label className="text-sm font-bold text-slate-700">Método de Pago</label>
          <Select {...register('tipo_caja')}>
            <option value="EFECTIVO">Efectivo</option>
            <option value="YAPE">Yape</option>
            <option value="PLIN">Plin</option>
            <option value="TARJETA">Tarjeta</option>
          </Select>
        </div>
        <div className="flex justify-end gap-2 pt-2">
          <Button type="button" onClick={onClose} className="bg-slate-200 text-slate-700">Cancelar</Button>
          <Button type="submit" disabled={!checkinId || loadingCheckins}>Aplicar Ajuste</Button>
        </div>
      </form>
    </Modal>
  )
}
