import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { Modal } from '../ui/Modal' 
import Input from '../ui/Input'
import Button from '../ui/Button'
import Select from '../ui/Select'
import { useCajas } from '../../hooks/useCajas'
import api from '../../api/axiosConfig'

export default function ModalAperturaCaja({ open, onClose }) {
  const { abrirCaja } = useCajas()
  
  // CORRECCIÓN: Los defaultValues deben coincidir con las claves del modelo en Django
  const { register, handleSubmit, setValue } = useForm({
    defaultValues: { monto_inicial: 0, turno: 'mañana' }
  })

  const [montoSugerido, setMontoSugerido] = useState(0)

  useEffect(() => {
    if (!open) return
    api.get('/caja/apertura/sugerida/')
      .then(({ data }) => {
        const sugerido = Number(data.monto_sugerido || 0)
        setMontoSugerido(sugerido)
        setValue('monto_inicial', sugerido)
      })
      .catch(() => {
        setMontoSugerido(0)
        setValue('monto_inicial', 0)
      })
  }, [open, setValue])

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
      alert('Caja abierta correctamente.')
    } catch (err) {
      const msg = err.response?.data?.detail || err.response?.data?.error || 'Verifique los datos'
      alert("Error al abrir caja: " + msg)
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
          <p className="mt-1 text-xs text-blue-700">
            Monto inicial sugerido del turno anterior: S/ {montoSugerido.toFixed(2)}
          </p>
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