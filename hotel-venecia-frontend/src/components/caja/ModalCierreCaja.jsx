import { useEffect, useRef } from 'react'
import { useForm } from 'react-hook-form'
import { Modal } from '../ui/Modal'
import Input from '../ui/Input'
import Button from '../ui/Button'

export default function ModalCierreCaja({ open, onClose, onSubmit, montoEsperado, isSaving }) {
  const inputRef = useRef(null)
  const { register, handleSubmit, watch, reset } = useForm({ defaultValues: { monto_real: '', notas: '' } })
  const montoRealField = register('monto_real', { required: true, min: 0 })
  const montoReal = Number(watch('monto_real') || 0)
  const esperado = Number(montoEsperado ?? 0)
  const diferencia = montoReal - esperado
  const diferenciaAbsoluta = Math.abs(diferencia)
  const diferenciaCero = diferenciaAbsoluta < 0.005

  useEffect(() => {
    if (open) {
      reset({ monto_real: '', notas: '' })
      window.setTimeout(() => inputRef.current?.focus(), 0)
    }
  }, [open, reset])

  return (
    <Modal open={open} title="Cerrar Turno" onClose={onClose}>
      <form onSubmit={handleSubmit((data) => onSubmit({
        monto_esperado: esperado,
        monto_real: Number(data.monto_real),
        diferencia,
        notas: data.notas || '',
      }))} className="space-y-5">
        <div className="rounded-2xl bg-slate-100 px-5 py-4 text-center">
          <p className="text-xs font-bold uppercase tracking-wide text-slate-500">Monto Esperado en Efectivo (S/)</p>
          <p className="mt-1 text-3xl font-black text-slate-900">S/ {esperado.toFixed(2)}</p>
        </div>
        <div>
          <label className="text-sm font-bold text-slate-700">Efectivo en Cajón (S/)</label>
          <Input
            {...montoRealField}
            ref={(element) => {
              inputRef.current = element
              montoRealField.ref(element)
            }}
            type="number"
            min="0"
            step="0.01"
            placeholder="0.00"
            required
          />
          <p className={`mt-2 text-sm font-bold ${diferenciaCero ? 'text-green-600' : diferencia < 0 ? 'text-red-600' : 'text-amber-600'}`}>
            {diferenciaCero ? '✓ Caja cuadrada' : `${diferencia < 0 ? 'Faltante' : 'Sobrante'}: S/ ${diferenciaAbsoluta.toFixed(2)}`}
          </p>
        </div>
        {!diferenciaCero && (
          <div>
            <label className="text-sm font-bold text-slate-700">Notas</label>
            <textarea className="w-full rounded-xl border border-slate-200 px-4 py-3 text-sm" rows="2" {...register('notas')} placeholder="Detalle de la diferencia (opcional)" />
          </div>
        )}
        <div className="flex justify-end gap-2 pt-1">
          <Button type="button" onClick={onClose} className="bg-slate-200 text-slate-700">Cancelar</Button>
          <Button type="submit" disabled={isSaving}>{isSaving ? 'Cerrando...' : 'Cerrar Caja'}</Button>
        </div>
      </form>
    </Modal>
  )
}