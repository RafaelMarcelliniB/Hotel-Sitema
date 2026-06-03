import { useForm } from 'react-hook-form'
import { Modal } from '../ui/Modal'
import { Input } from '../ui/Input'
import { Button } from '../ui/Button'
import { useEspacios } from '../../hooks/useEspacios'
import { globalValidations } from '../../utils/validations'

export default function ModalIngresoCochera({ espacio, onClose }) {
  const { registrarIngreso } = useEspacios()
  const { register, handleSubmit, formState: { errors } } = useForm()

  const onSubmit = async (data) => {
    try {
      await registrarIngreso({
        espacio_id: espacio.id,
        placa: data.placa.toUpperCase(),
        tipo_pago: 'EFECTIVO' // Por defecto
      })
      onClose()
    } catch (err) {
      alert("Error al registrar vehículo")
    }
  }

  return (
    <Modal title={`Ingreso a Cochera #${espacio.numero}`} onClose={onClose}>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <Input 
          label="Placa del Vehículo" 
          placeholder="ABC-123"
          className="uppercase text-center text-xl font-bold"
          {...register('placa', globalValidations.placa)}
          error={errors.placa?.message}
        />
        
        <div className="bg-slate-50 p-3 rounded text-sm text-slate-600">
          Tarifa sugerida: <span className="font-bold text-slate-900">S/ {espacio.tarifa_hora || '2.00'} por hora</span>
        </div>

        <div className="flex gap-2 justify-end mt-6">
          <Button type="button" variant="ghost" onClick={onClose}>Cancelar</Button>
          <Button type="submit">Confirmar Entrada</Button>
        </div>
      </form>
    </Modal>
  )
}