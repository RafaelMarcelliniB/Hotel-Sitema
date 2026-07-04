import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { Modal } from '../ui/Modal'
import { Input } from '../ui/Input'
import { Button } from '../ui/Button'
import { Select } from '../ui/Select'
import { useTrabajadores } from '../../hooks/useTrabajadores'
import { globalValidations } from '../../utils/validations'

export default function ModalNuevoTrabajador({ onClose, initialData = null, id = null }) {
  const { crearTrabajador, editarTrabajador } = useTrabajadores()
  const { register, handleSubmit, formState: { errors }, reset } = useForm({ defaultValues: initialData || {} })

  // Si cambian los datos iniciales (modo edición), reiniciamos el formulario
  useEffect(() => {
    if (initialData) reset(initialData)
  }, [initialData, reset])

  const onSubmit = async (data) => {
    try {
      if (id) {
        await editarTrabajador({ id, data })
      } else {
        await crearTrabajador(data)
      }
      onClose()
      reset()
      alert('Usuario guardado correctamente')
    } catch (err) {
      const msg = err?.message || 'Error: los datos son inválidos o el usuario ya existe'
      alert(msg)
    }
  }

  return (
    <Modal open={true} title={id ? 'Editar Trabajador' : 'Nuevo Trabajador'} onClose={onClose}>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="mb-2 block text-sm text-slate-600">Usuario (nombre de usuario)</label>
          <Input 
            placeholder="Ej: juan.perez"
            {...register('username', { required: 'El usuario es obligatorio', minLength: { value: 3, message: 'Mínimo 3 caracteres' } })}
            aria-invalid={errors.username ? 'true' : 'false'}
          />
          {errors.username && <p className="mt-1 text-xs text-red-600">{errors.username.message}</p>}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-2 block text-sm text-slate-600">Nombres</label>
            <Input placeholder="Nombres completos" {...register('nombre', { required: true })} />
          </div>
          <div>
            <label className="mb-2 block text-sm text-slate-600">Apellidos</label>
            <Input placeholder="Apellidos" {...register('apellido', { required: true })} />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-2 block text-sm text-slate-600">Rol en el Sistema</label>
            <Select {...register('rol')}>
              <option value="">-- Seleccionar rol --</option>
              <option value="recepcionista">Recepcionista</option>
              <option value="cajero">Cajero</option>
              <option value="admin">Administrador</option>
            </Select>
          </div>
          <div>
            <label className="mb-2 block text-sm text-slate-600">Contraseña</label>
            <Input 
              placeholder={id ? 'Dejar en blanco para no cambiar' : 'Mínimo 6 caracteres'}
              type="password" 
              {...register('password', id ? { minLength: 6 } : { required: true, minLength: 6 })} 
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 items-end">
          <div>
            <label className="mb-2 block text-sm text-slate-600">Turno</label>
            <Select {...register('turno')}>
              <option value="">-- Seleccionar turno --</option>
              <option value="mañana">Mañana</option>
              <option value="tarde">Tarde</option>
              <option value="noche">Noche</option>
            </Select>
          </div>
          <div className="flex items-center gap-3">
            <input id="activo" type="checkbox" className="h-4 w-4" {...register('activo')} />
            <label htmlFor="activo" className="text-sm text-slate-600">Activo</label>
          </div>
        </div>
        <div className="flex justify-end gap-2 pt-4">
          <Button type="button" variant="ghost" onClick={onClose}>Cancelar</Button>
          <Button type="submit">{id ? 'Guardar cambios' : 'Guardar Usuario'}</Button>
        </div>
      </form>
    </Modal>
  )
}