import { useForm } from 'react-hook-form'
import { Modal } from '../ui/Modal'
import { Input } from '../ui/Input'
import { Button } from '../ui/Button'
import { Select } from '../ui/Select'
import { useRecados } from '../../hooks/useRecados'

export default function ModalNuevoRecado({ onClose }) {
  const { crearRecado } = useRecados()
  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: { prioridad: 'MEDIA' }
  })

  const onSubmit = async (data) => {
    try {
      await crearRecado(data)
      onClose()
    } catch (err) {
      alert("Error al crear recado")
    }
  }

  return (
    <Modal title="Dejar un Recado" onClose={onClose}>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Contenido del Mensaje</label>
          <textarea 
            {...register('contenido', { required: "El mensaje no puede estar vacío" })}
            className="w-full p-3 border rounded-md h-32 focus:ring-2 focus:ring-blue-500 outline-none"
            placeholder="Ej: El huésped de la 204 pagará al salir..."
          />
          {errors.contenido && <span className="text-red-500 text-xs">{errors.contenido.message}</span>}
        </div>

        <Select label="Prioridad" {...register('prioridad')}>
          <option value="BAJA">Baja (Informativo)</option>
          <option value="MEDIA">Media (Aviso)</option>
          <option value="ALTA">Alta (Urgente / Crítico)</option>
        </Select>

        <div className="flex justify-end gap-2 pt-4">
          <Button type="button" variant="ghost" onClick={onClose}>Cancelar</Button>
          <Button type="submit">Guardar Recado</Button>
        </div>
      </form>
    </Modal>
  )
}