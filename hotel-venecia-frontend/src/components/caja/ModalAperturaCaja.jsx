import { useForm } from 'react-hook-form'
import { Modal } from '../ui/Modal'
import { Input } from '../ui/Input'
import { Button } from '../ui/Button'
import { Select } from '../ui/Select'
import { useCajas } from '../../hooks/useCajas'

export default function ModalAperturaCaja({ onClose }) {
  const { abrirCaja } = useCajas()
  const { register, handleSubmit } = useForm({
    defaultValues: { monto_inicial: 0, turno: 'MAÑANA' }
  })

  const onSubmit = async (data) => {
    try {
      await abrirCaja(data)
      onClose()
    } catch (err) {
      alert("Error al abrir caja: " + (err.response?.data?.error || "Error desconocido"))
    }
  }

  return (
    <Modal title="Apertura de Turno" onClose={onClose}>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <Input 
          label="Monto Inicial en Efectivo (S/)" 
          type="number" 
          step="0.10"
          {...register('monto_inicial', { required: true })}
        />
        <Select label="Seleccionar Turno" {...register('turno')}>
          <option value="MAÑANA">Mañana</option>
          <option value="TARDE">Tarde</option>
          <option value="NOCHE">Noche</option>
          <option value="MADRUGADA">Madrugada</option>
        </Select>
        <div className="flex justify-end gap-2 pt-4">
          <Button type="button" variant="ghost" onClick={onClose}>Cancelar</Button>
          <Button type="submit">Iniciar Turno</Button>
        </div>
      </form>
    </Modal>
  )
}