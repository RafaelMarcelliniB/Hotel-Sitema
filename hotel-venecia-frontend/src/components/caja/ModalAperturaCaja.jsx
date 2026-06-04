import { useForm } from 'react-hook-form'
import { Modal } from '../ui/Modal' 
import Input from '../ui/Input'
import Button from '../ui/Button'
import Select from '../ui/Select'
import { useCajas } from '../../hooks/useCajas'

export default function ModalAperturaCaja({ open, onClose }) {
  const { abrirCaja } = useCajas()
  
  // CORRECCIÓN: Los defaultValues deben coincidir con las claves del modelo en Django
  const { register, handleSubmit } = useForm({
    defaultValues: { monto_inicial: 0, turno: 'mañana' }
  })

  if (!open) return null

  const onSubmit = async (data) => {
    try {
      // Aseguramos que el monto sea enviado como número decimal
      const formattedData = {
        ...data,
        monto_inicial: parseFloat(data.monto_inicial)
      }
      await abrirCaja(formattedData)
      onClose()
    } catch (err) {
      alert("Error al abrir caja: " + (err.response?.data?.error || "Verifique los datos"))
    }
  }

  return (
    <Modal open={open} title="Apertura de Turno" onClose={onClose}>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="space-y-1">
          <label className="text-sm font-bold text-slate-700">Monto Inicial (S/)</label>
          <Input 
            type="number" 
            step="0.10"
            {...register('monto_inicial', { required: true })}
          />
        </div>
        
        <div className="space-y-1">
          <label className="text-sm font-bold text-slate-700">Turno</label>
          {/* CORRECCIÓN: Los 'value' deben ser exactamente iguales a los del models.py */}
          <Select {...register('turno')}>
            <option value="mañana">Mañana</option>
            <option value="tarde">Tarde</option>
            <option value="noche">Noche</option>
            <option value="madrugada">Madrugada</option>
          </Select>
        </div>

        <div className="flex justify-end gap-2 pt-4">
          <Button type="button" onClick={onClose} className="bg-slate-200 text-slate-700">
            Cancelar
          </Button>
          <Button type="submit">Iniciar Turno</Button>
        </div>
      </form>
    </Modal>
  )
}