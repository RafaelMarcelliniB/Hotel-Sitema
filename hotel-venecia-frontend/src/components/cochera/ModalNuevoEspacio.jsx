import { useForm } from 'react-hook-form'
import { Modal } from '../ui/Modal'
import { Input } from '../ui/Input'
import { Button } from '../ui/Button'
import { Select } from '../ui/Select'
import { useEspacios } from '../../hooks/useEspacios'

const TIPOS_ESPACIO = [
  { value: 'AUTO', label: 'Auto' },
  { value: 'MOTO', label: 'Moto' },
  { value: 'BUS', label: 'Bus' },
]

export default function ModalNuevoEspacio({ onClose, espacios = [] }) {
  const { crearEspacio, isCreatingEspacio } = useEspacios()
  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: {
      tipo: 'AUTO',
      estado: 'LIBRE',
    }
  })

  const existingNumbers = espacios.map(e => e.numero)

  const onSubmit = async (data) => {
    try {
      await crearEspacio(data)
      onClose()
      alert('Espacio de cochera creado correctamente')
    } catch (err) {
      const msg = err?.response?.data?.detail || err?.message || 'Error al crear el espacio'
      alert(msg)
    }
  }

  return (
    <Modal open={true} title="Nuevo Espacio de Cochera" onClose={onClose}>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="mb-2 block text-sm text-slate-600">Número de Espacio</label>
          <Input
            placeholder="Ej: C-01, C-02, A-01"
            {...register('numero', { 
              required: 'El número es obligatorio',
              validate: value => existingNumbers.includes(value) ? 'Este número ya existe' : true
            })}
            aria-invalid={errors.numero ? 'true' : 'false'}
          />
          {errors.numero && <p className="mt-1 text-xs text-red-600">{errors.numero.message}</p>}
        </div>

        <div>
          <label className="mb-2 block text-sm text-slate-600">Tipo de Espacio</label>
          <Select {...register('tipo', { required: 'El tipo es obligatorio' })}>
            <option value="">-- Seleccionar tipo --</option>
            {TIPOS_ESPACIO.map(tipo => (
              <option key={tipo.value} value={tipo.value}>{tipo.label}</option>
            ))}
          </Select>
          {errors.tipo && <p className="mt-1 text-xs text-red-600">{errors.tipo.message}</p>}
        </div>

        <div>
          <label className="mb-2 block text-sm text-slate-600">Estado Inicial</label>
          <Select {...register('estado')}>
            <option value="LIBRE">Libre</option>
            <option value="OCUPADO">Ocupado</option>
          </Select>
        </div>

        <div className="flex justify-end gap-2 pt-4">
          <Button type="button" variant="ghost" onClick={onClose} disabled={isCreatingEspacio}>Cancelar</Button>
          <Button type="submit" disabled={isCreatingEspacio}>
            {isCreatingEspacio ? 'Creando...' : 'Crear Espacio'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}