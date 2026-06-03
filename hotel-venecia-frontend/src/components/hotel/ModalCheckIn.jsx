import { useForm } from 'react-hook-form'
import { Modal } from '../ui/Modal'
import { Input } from '../ui/Input'
import { Button } from '../ui/Button'
import { Select } from '../ui/Select'
import api from '../../api/axiosConfig'
import { globalValidations } from '../../utils/validations'

export default function ModalCheckIn({ habitacion, onClose, onSuccess }) {
  const { register, handleSubmit, setValue, watch, formState: { errors } } = useForm({
    defaultValues: {
      habitacion_id: habitacion.id,
      monto_pagado: habitacion.tarifa_dia,
      tipo_pago: 'EFECTIVO'
    }
  })

  const buscarDNI = async () => {
    const dni = watch('dni')
    if (dni?.length === 8) {
      try {
        const { data } = await api.get(`/hotel/huespedes/?dni=${dni}`)
        if (data) {
          setValue('nombre', data.nombre)
          setValue('apellido', data.apellido)
          setValue('huesped_id', data.id)
        }
      } catch (err) {
        console.log("Huésped nuevo")
      }
    }
  }

  const onSubmit = async (data) => {
    try {
      await api.post('/hotel/checkin/', data)
      onSuccess()
      onClose()
    } catch (err) {
      alert("Error al registrar check-in")
    }
  }

  return (
    <Modal title={`Check-In: Habitación ${habitacion.numero}`} onClose={onClose}>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="flex gap-2 items-end">
          <Input 
            label="DNI Huésped" 
            {...register('dni', globalValidations.dni)} 
            error={errors.dni?.message}
          />
          <Button type="button" onClick={buscarDNI} variant="outline">Buscar</Button>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Input label="Nombre" {...register('nombre', { required: true })} />
          <Input label="Apellido" {...register('apellido', { required: true })} />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Select label="Turno" {...register('turno_ingreso')}>
            <option value="DIA">Día</option>
            <option value="NOCHE">Noche</option>
          </Select>
          <Input 
            label="Monto a Pagar" 
            type="number" 
            {...register('monto_pagado', globalValidations.monto)} 
          />
        </div>

        <Select label="Método de Pago" {...register('tipo_pago')}>
          <option value="EFECTIVO">Efectivo</option>
          <option value="YAPE">Yape</option>
          <option value="TARJETA">Tarjeta</option>
        </Select>

        <div className="flex justify-end gap-2 mt-6">
          <Button type="button" variant="ghost" onClick={onClose}>Cancelar</Button>
          <Button type="submit">Confirmar Ingreso</Button>
        </div>
      </form>
    </Modal>
  )
}