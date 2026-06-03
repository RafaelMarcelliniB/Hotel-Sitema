import { useForm } from 'react-hook-form'
import { Modal } from '../ui/Modal'
import { Input } from '../ui/Input'
import { Button } from '../ui/Button'
import { Select } from '../ui/Select'
import { useTrabajadores } from '../../hooks/useTrabajadores'
import { globalValidations } from '../../utils/validations'

export default function ModalNuevoTrabajador({ onClose }) {
  const { crearTrabajador } = useTrabajadores()
  const { register, handleSubmit, formState: { errors } } = useForm()

  const onSubmit = async (data) => {
    try {
      await crearTrabajador(data)
      onClose()
    } catch (err) {
      alert("Error: El DNI ya existe o los datos son inválidos")
    }
  }

  return (
    <Modal title="Nuevo Trabajador" onClose={onClose}>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <Input 
          label="DNI (Será su nombre de usuario)" 
          {...register('username', globalValidations.dni)}
          error={errors.username?.message}
        />
        <div className="grid grid-cols-2 gap-4">
          <Input label="Nombres" {...register('first_name', { required: true })} />
          <Input label="Apellidos" {...register('last_name', { required: true })} />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <Select label="Rol en el Sistema" {...register('rol')}>
            <option value="recepcionista">Recepcionista</option>
            <option value="cajero">Cajero</option>
            <option value="admin">Administrador</option>
          </Select>
          <Input 
            label="Contraseña" 
            type="password" 
            {...register('password', { required: true, minLength: 6 })} 
          />
        </div>
        <div className="flex justify-end gap-2 pt-4">
          <Button type="button" variant="ghost" onClick={onClose}>Cancelar</Button>
          <Button type="submit">Guardar Trabajador</Button>
        </div>
      </form>
    </Modal>
  )
}