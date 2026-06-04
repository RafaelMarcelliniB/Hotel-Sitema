import { useForm } from 'react-hook-form'
import { Input } from '../ui/Input'
import { Button } from '../ui/Button'
import { Select } from '../ui/Select'
import api from '../../api/axiosConfig'

export default function ModalCheckIn({ habitacion, onClose, onSuccess }) {
  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: {
      habitacion_id: habitacion.id,
      monto_pagado: habitacion.tarifa_dia,
      tipo_pago: 'EFECTIVO',
      turno_ingreso: 'DIA',
      nacionalidad: 'Perú' // Valor por defecto común
    }
  })

  const onSubmit = async (data) => {
    const formattedData = {
      habitacion_id: data.habitacion_id,
      turno_ingreso: data.turno_ingreso,
      tipo_pago: data.tipo_pago,
      monto_pagado: data.monto_pagado,
      // Agrupamos todos los datos del nuevo huésped
      huesped: {
        dni_pasaporte: data.dni_pasaporte,
        nombre: data.nombre,
        apellido: data.apellido,
        nacionalidad: data.nacionalidad,
        ciudad_origen: data.ciudad_origen,
        estado_civil: 'SOLTERO', // Campos opcionales o con defecto
        tipo_visita: 'TURISTA'
      }
    }

    try {
      await api.post('/hotel/checkin/', formattedData)
      onSuccess()
      onClose()
    } catch (err) {
      console.error("Error al registrar:", err.response?.data)
      const errorMsg = err.response?.data?.error || "Error al procesar el check-in."
      alert(errorMsg)
    }
  }

  if (!habitacion) return null

  return (
    <>
      <div className="fixed inset-0 bg-slate-900/40 z-50 backdrop-blur-sm" onClick={onClose} />
      <div className="fixed right-0 top-0 h-full w-full max-w-md bg-white z-50 shadow-2xl flex flex-col">
        
        <div className="p-6 border-b bg-slate-50 flex justify-between items-center">
          <div>
            <h3 className="text-xl font-bold text-slate-800">Habitación #{habitacion.numero}</h3>
            <p className="text-[10px] text-slate-500 font-black uppercase tracking-widest">Registro de Ingreso</p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-800 text-2xl">&times;</button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-8">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            
            {/* SECCIÓN DEL HUÉSPED */}
            <div className="space-y-4">
              <h4 className="text-[10px] font-black text-blue-600 uppercase tracking-widest">Información Personal</h4>
              
              <Input 
                label="DNI / Pasaporte" 
                placeholder="Número de documento" 
                {...register('dni_pasaporte', { required: "Este campo es obligatorio" })} 
                error={errors.dni_pasaporte?.message}
              />
              
              <div className="grid grid-cols-2 gap-4">
                <Input label="Nombres" placeholder="Nombre(s)" {...register('nombre', { required: true })} />
                <Input label="Apellidos" placeholder="Apellido(s)" {...register('apellido', { required: true })} />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <Input label="Nacionalidad" placeholder="Ej. Nacionalidad" {...register('nacionalidad')} />
                <Input label="Ciudad de Origen" placeholder="Ej. Ciudad de Origen" {...register('ciudad_origen')} />
              </div>
            </div>

            {/* SECCIÓN DE PAGO */}
            <div className="space-y-4 pt-6 border-t border-slate-100">
              <h4 className="text-[10px] font-black text-blue-600 uppercase tracking-widest">Detalles de Estancia y Pago</h4>
              
              <div className="grid grid-cols-2 gap-4">
                <Select label="Turno de Ingreso" {...register('turno_ingreso')}>
                  <option value="DIA">Turno Día</option>
                  <option value="NOCHE">Turno Tarde</option>
                  <option value="NOCHE">Turno Noche</option>
                  <option value="MADRUGADA">Madrugada</option>
                </Select>
                <Input 
                  label="Tarifa Aplicada (S/)" 
                  type="number" 
                  step="0.01" 
                  {...register('monto_pagado')} 
                />
              </div>

              <Select label="Método de Pago" {...register('tipo_pago')}>
                <option value="EFECTIVO">Efectivo</option>
                <option value="YAPE">Yape / Plin</option>
                <option value="TARJETA">Tarjeta de Débito/Crédito</option>
              </Select>
            </div>

            <div className="pt-4">
              <Button type="submit" className="w-full py-4 text-base font-bold shadow-lg shadow-blue-200">
                Confirmar e Iniciar Estancia
              </Button>
              <button 
                type="button" 
                onClick={onClose}
                className="w-full mt-4 text-sm font-semibold text-slate-400 hover:text-slate-600 transition-colors"
              >
                Cancelar registro
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  )
}