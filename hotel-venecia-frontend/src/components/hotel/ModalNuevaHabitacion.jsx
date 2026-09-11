import { useForm } from 'react-hook-form'
import { Modal } from '../ui/Modal'
import { Input } from '../ui/Input'
import { Button } from '../ui/Button'
import { Select } from '../ui/Select'
import { useHabitaciones } from '../../hooks/useHabitaciones'

const TIPOS_HABITACION = [
  { value: 'SIMPLE', label: 'Simple' },
  { value: 'DOBLE', label: 'Doble' },
  { value: 'SUITE', label: 'Suite' },
  { value: 'MATRI', label: 'Matrimonial' },
  { value: 'TRIPLE', label: 'Triple' },
  { value: 'CUADRUPLE', label: 'Cuádruple' },
]

const MARCAS_TV = [
  { value: 'JVC', label: 'JVC' },
  { value: 'JVC_V', label: 'JVC V' },
  { value: 'HISENSE', label: 'Hisense' },
  { value: 'SM', label: 'SM' },
]

const TIPOS_CAMA = [
  { value: 'DOS_PLAZAS', label: 'Dos Plazas' },
  { value: 'QUEEN', label: 'Queen' },
  { value: 'KING', label: 'King' },
]

export default function ModalNuevaHabitacion({ onClose, habitaciones = [] }) {
  const { crearHabitacion, isCreating } = useHabitaciones()
  const { register, handleSubmit, formState: { errors }, watch } = useForm({
    defaultValues: {
      tipo: 'SIMPLE',
      estado_ocupacion: 'DISPONIBLE',
      estado_limpieza: 'LIMPIO',
      marca_tv: 'JVC',
      tipo_cama: 'DOS_PLAZAS',
    }
  })

  const selectedPiso = watch('piso')

  const existingFloors = [...new Set(habitaciones.map(h => h.piso))].sort((a, b) => a - b)

  const onSubmit = async (data) => {
    try {
      // Si seleccionó "otro", usar el piso manual
      const habitacionData = {
        ...data,
        piso: data.piso === 'otro' ? data.piso_manual : Number(data.piso),
        tarifa_noche: data.tarifa_noche || data.tarifa_dia,
        tarifa_madrugada: data.tarifa_madrugada || data.tarifa_dia,
      }
      // Eliminar el campo auxiliar piso_manual
      delete habitacionData.piso_manual
      
      await crearHabitacion(habitacionData)
      onClose()
      alert('Habitación creada correctamente')
    } catch (err) {
      const msg = err?.response?.data?.detail || err?.message || 'Error al crear la habitación'
      alert(msg)
    }
  }

  return (
    <Modal open={true} title="Nueva Habitación" onClose={onClose}>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="mb-2 block text-sm text-slate-600">Número de Habitación</label>
          <Input
            placeholder="Ej: 101, 205, 312"
            {...register('numero', { 
              required: 'El número es obligatorio',
              pattern: { value: /^\d+$/, message: 'Solo números' }
            })}
            aria-invalid={errors.numero ? 'true' : 'false'}
          />
          {errors.numero && <p className="mt-1 text-xs text-red-600">{errors.numero.message}</p>}
        </div>

        <div>
          <label className="mb-2 block text-sm text-slate-600">Piso</label>
          <Select {...register('piso', { required: 'El piso es obligatorio' })}>
            <option value="">-- Seleccionar piso --</option>
            {existingFloors.map(piso => (
              <option key={piso} value={piso}>Piso {piso}</option>
            ))}
            <option value="otro">Otro (ingresar manualmente)...</option>
          </Select>
          {errors.piso && <p className="mt-1 text-xs text-red-600">{errors.piso.message}</p>}
        </div>

        {selectedPiso === 'otro' && (
          <div>
            <label className="mb-2 block text-sm text-slate-600">Número de Piso</label>
            <Input
              type="number"
              min="1"
              placeholder="Ej: 7, 8, 9..."
              {...register('piso_manual', { 
                required: 'El piso es obligatorio',
                min: { value: 1, message: 'Mínimo piso 1' },
                valueAsNumber: true
              })}
              aria-invalid={errors.piso_manual ? 'true' : 'false'}
            />
            {errors.piso_manual && <p className="mt-1 text-xs text-red-600">{errors.piso_manual.message}</p>}
          </div>
        )}

        <div>
          <label className="mb-2 block text-sm text-slate-600">Tipo de Habitación</label>
          <Select {...register('tipo', { required: 'El tipo es obligatorio' })}>
            <option value="">-- Seleccionar tipo --</option>
            {TIPOS_HABITACION.map(tipo => (
              <option key={tipo.value} value={tipo.value}>{tipo.label}</option>
            ))}
          </Select>
          {errors.tipo && <p className="mt-1 text-xs text-red-600">{errors.tipo.message}</p>}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-2 block text-sm text-slate-600">Tarifa Diaria (S/)</label>
            <Input
              type="number"
              min="0"
              step="0.1"
              placeholder="Ej: 70.00"
              {...register('tarifa_dia', { 
                required: 'La tarifa es obligatoria',
                min: { value: 0, message: 'Debe ser mayor a 0' },
                valueAsNumber: true
              })}
              aria-invalid={errors.tarifa_dia ? 'true' : 'false'}
            />
            {errors.tarifa_dia && <p className="mt-1 text-xs text-red-600">{errors.tarifa_dia.message}</p>}
          </div>
          <div>
            <label className="mb-2 block text-sm text-slate-600">Tarifa Noche (S/)</label>
            <Input
              type="number"
              min="0"
              step="0.1"
              placeholder="Ej: 90.00"
              {...register('tarifa_noche', { 
                min: { value: 0, message: 'Debe ser mayor a 0' },
                valueAsNumber: true
              })}
              aria-invalid={errors.tarifa_noche ? 'true' : 'false'}
            />
            {errors.tarifa_noche && <p className="mt-1 text-xs text-red-600">{errors.tarifa_noche.message}</p>}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-2 block text-sm text-slate-600">Tarifa Madrugada (S/)</label>
            <Input
              type="number"
              min="0"
              step="0.1"
              placeholder="Ej: 50.00"
              {...register('tarifa_madrugada', { 
                min: { value: 0, message: 'Debe ser mayor a 0' },
                valueAsNumber: true
              })}
              aria-invalid={errors.tarifa_madrugada ? 'true' : 'false'}
            />
            {errors.tarifa_madrugada && <p className="mt-1 text-xs text-red-600">{errors.tarifa_madrugada.message}</p>}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-2 block text-sm text-slate-600">Marca TV</label>
            <Select {...register('marca_tv', { required: 'La marca de TV es obligatoria' })}>
              <option value="">-- Seleccionar marca --</option>
              {MARCAS_TV.map(marca => (
                <option key={marca.value} value={marca.value}>{marca.label}</option>
              ))}
            </Select>
            {errors.marca_tv && <p className="mt-1 text-xs text-red-600">{errors.marca_tv.message}</p>}
          </div>
          <div>
            <label className="mb-2 block text-sm text-slate-600">Tipo de Cama</label>
            <Select {...register('tipo_cama', { required: 'El tipo de cama es obligatorio' })}>
              <option value="">-- Seleccionar tipo --</option>
              {TIPOS_CAMA.map(cama => (
                <option key={cama.value} value={cama.value}>{cama.label}</option>
              ))}
            </Select>
            {errors.tipo_cama && <p className="mt-1 text-xs text-red-600">{errors.tipo_cama.message}</p>}
          </div>
        </div>

        <div className="flex justify-end gap-2 pt-4">
          <Button type="button" variant="ghost" onClick={onClose} disabled={isCreating}>Cancelar</Button>
          <Button type="submit" disabled={isCreating}>
            {isCreating ? 'Creando...' : 'Crear Habitación'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}