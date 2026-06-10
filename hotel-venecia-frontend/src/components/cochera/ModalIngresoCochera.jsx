import { useForm } from 'react-hook-form'
import { useState, useEffect } from 'react'
import { Modal } from '../ui/Modal'
import { Button } from '../ui/Button'
import { useEspacios } from '../../hooks/useEspacios'
import api from '../../api/axiosConfig'

export default function ModalIngresoCochera({ espacio, onClose }) {
  const { registrarIngreso } = useEspacios()
  const [checkinsActivos, setCheckinsActivos] = useState([])
  const [loadingCheckins, setLoadingCheckins] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const { 
    register, 
    handleSubmit, 
    watch,
    setValue,
    formState: { errors } 
  } = useForm({
    defaultValues: {
      placa: '',
      tipo_vehiculo: espacio?.tipo || 'AUTO',
      tipo_cliente: 'PUBLICO',
      tarifa_tipo: 'POR_HORA',
      checkin_vinculado_id: '',
      marca: '',
      color: '',
      nombre_conductor: '',
      dni_conductor: ''
    }
  })

  const watchTipoCliente = watch('tipo_cliente')

  // Aseguramos que el tipo de vehículo venga fijado al tipo del espacio y no sea editable
  useEffect(() => {
    if (espacio && espacio.tipo) {
      setValue('tipo_vehiculo', espacio.tipo)
    }
  }, [espacio, setValue])

  // 1. Cargar Check-Ins Activos desde la URL correcta del backend (/api/hotel/checkin/activos/)
  useEffect(() => {
    if (watchTipoCliente === 'HUESPED') {
      setLoadingCheckins(true)
      api.get('/hotel/checkin/activos/') // <-- Corregido a singular 'checkin' según tu views.py
        .then((res) => {
          setCheckinsActivos(res.data || [])
          setLoadingCheckins(false)
        })
        .catch((err) => {
          console.error("Error al cargar huéspedes activos:", err)
          setLoadingCheckins(false)
        })
    } else {
      // Si cambia a Eventual, limpiamos la vinculación
      setValue('checkin_vinculado_id', '')
    }
  }, [watchTipoCliente, setValue])

  // 2. FUNCIONALIDAD DE AUTOCOMPLETADO AUTOMÁTICO
  const handleCheckinChange = (e) => {
    const checkinId = e.target.value
    if (checkinId) {
      // Buscamos el objeto checkin seleccionado en el estado
      const seleccionado = checkinsActivos.find(c => c.id === parseInt(checkinId))
      
      if (seleccionado && seleccionado.huesped) {
        const nombreCompleto = `${seleccionado.huesped.nombre} ${seleccionado.huesped.apellido}`.trim()
        // Asignamos el valor al input usando la estructura exacta de HuespedSerializer
        setValue('nombre_conductor', nombreCompleto)
        setValue('dni_conductor', seleccionado.huesped.dni_pasaporte || '')
      }
    } else {
      // Limpiar si deselecciona
      setValue('nombre_conductor', '')
      setValue('dni_conductor', '')
    }
  }

  const onSubmit = async (data) => {
    if (submitting) return
    setSubmitting(true)
    
    try {
      const payload = {
        espacio_id: espacio.id,
        placa: data.placa.toUpperCase().trim(),
        tipo_vehiculo: data.tipo_vehiculo,
        marca: data.marca.trim() || 'N/A',
        color: data.color.trim() || 'N/A',
        nombre_conductor: data.nombre_conductor.trim() || 'CLIENTE',
        dni_conductor: data.dni_conductor.trim() || '00000000',
        tipo_cliente: data.tipo_cliente,
        tarifa_tipo: data.tarifa_tipo,
        checkin_vinculado_id: data.checkin_vinculado_id ? parseInt(data.checkin_vinculado_id) : null
      }

      await registrarIngreso(payload)
      onClose()
    } catch (err) {
      console.error("Error devuelto por Django:", err.response?.data)
      alert("Error en el servidor: " + JSON.stringify(err.response?.data || "Error desconocido"))
    } finally {
      setSubmitting(false)
    }
  }

  const onError = (formErrors) => {
    console.log("Campos con errores de validación de React:", formErrors)
    alert("Por favor rellena los campos obligatorios: Placa y Marca.")
  }

  const inputStyle = "w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"

  return (
    <Modal open={true} title={`Ingreso a Cochera - Espacio #${espacio.numero}`} onClose={onClose}>
      <form onSubmit={handleSubmit(onSubmit, onError)} className="space-y-4 max-h-[70vh] overflow-y-auto px-1">
        
        {/* TIPO DE CLIENTE */}
        <div>
          <label className="block text-xs font-bold text-slate-600 uppercase mb-1">Tipo de Cliente</label>
          <select {...register('tipo_cliente')} className={inputStyle}>
            <option value="PUBLICO">Público general</option>
            <option value="HUESPED">Huésped del Hotel</option>
          </select>
        </div>

        {/* SELECTOR DINÁMICO DE HABITACIONES OCUPADAS */}
        {watchTipoCliente === 'HUESPED' && (
          <div className="bg-blue-50 p-3 rounded-xl border border-blue-100">
            <label className="block text-xs font-bold text-blue-800 uppercase mb-1">Habitación / Huésped de referencia</label>
            {loadingCheckins ? (
              <p className="text-xs text-blue-600">Cargando habitaciones ocupadas...</p>
            ) : (
              <select 
                {...register('checkin_vinculado_id', { required: watchTipoCliente === 'HUESPED' })}
                onChange={handleCheckinChange} // Intercepta el cambio para autocompletar
                className={inputStyle}
              >
                <option value="">-- Seleccione una habitación activa --</option>
                {checkinsActivos.map((c) => (
                  <option key={c.id} value={c.id}>
                    Hab. {c.habitacion?.numero} - {c.huesped?.nombre} {c.huesped?.apellido}
                  </option>
                ))}
              </select>
            )}
            {errors.checkin_vinculado_id && <p className="text-xs text-red-500 mt-1">Es obligatorio vincular una habitación para huéspedes.</p>}
          </div>
        )}

        {/* PLACA */}
        <div>
          <label className="block text-xs font-bold text-slate-600 uppercase mb-1">Placa del Vehículo *</label>
          <input 
            type="text"
            placeholder="Ej: ABC-123"
            className={`${inputStyle} uppercase font-mono text-center text-lg`}
            {...register('placa', { required: true })}
          />
        </div>

        {/* DETALLES (TIPO, MARCA, COLOR) */}
        <div className="grid grid-cols-3 gap-2">
          <div>
            <label className="block text-xs font-bold text-slate-600 uppercase mb-1">Tipo</label>
            <select {...register('tipo_vehiculo')} className={inputStyle} disabled>
              {espacio?.tipo === 'MOTO' && <option value="MOTO">Moto</option>}
              {espacio?.tipo === 'AUTO' && <option value="AUTO">Auto</option>}
              {espacio?.tipo === 'BUS' && <option value="BUS">Bus</option>}
              {/* Fallback por si el espacio no trae tipo */}
              {!espacio?.tipo && (
                <>
                  <option value="AUTO">Auto</option>
                  <option value="MOTO">Moto</option>
                  <option value="BUS">Bus</option>
                </>
              )}
            </select>
          </div>
          <div>
            <label className="block text-xs font-bold text-slate-600 uppercase mb-1">Marca *</label>
            <input type="text" placeholder="Toyota" className={inputStyle} {...register('marca', { required: true })} />
          </div>
          <div>
            <label className="block text-xs font-bold text-slate-600 uppercase mb-1">Color</label>
            <input type="text" placeholder="Negro" className={inputStyle} {...register('color')} />
          </div>
        </div>

        {/* CONDUCTOR Y DOCUMENTO (SE AUTOCOMPLETAN) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          <div>
            <label className="block text-xs font-bold text-slate-600 uppercase mb-1">Nombre Completo Conductor *</label>
            <input 
              type="text" 
              placeholder="Nombre del conductor" 
              className={inputStyle} 
              {...register('nombre_conductor', { required: true })} 
              readOnly={watchTipoCliente === 'HUESPED' && !!watch('checkin_vinculado_id')}
            />
          </div>
          <div>
            <label className="block text-xs font-bold text-slate-600 uppercase mb-1">DNI / Documento</label>
            <input 
              type="text" 
              placeholder="DNI" 
              className={inputStyle} 
              {...register('dni_conductor')} 
              readOnly={watchTipoCliente === 'HUESPED' && !!watch('checkin_vinculado_id')}
            />
          </div>
        </div>

        {/* TARIFA */}
        <div>
          <label className="block text-xs font-bold text-slate-600 uppercase mb-1">Esquema de Tarifa</label>
          <select {...register('tarifa_tipo')} className={inputStyle}>
            <option value="POR_HORA">Por Hora Regular (S/ 5.00)</option>
            <option value="FRACCION">Por Fracción</option>
            <option value="DIA_COMPLETO">Día Completo (S/ 25.00)</option>
            <option value="NOCTURNA">Tarifa Nocturna (S/ 15.00)</option>
          </select>
        </div>

        {/* BOTONES DE ACCIÓN */}
        <div className="flex gap-2 justify-end pt-4 border-t border-slate-100">
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancelar
          </Button>
          {/* CORREGIDO: type="submit" explícito para asegurar que ejecute el formulario */}
          <Button type="submit" disabled={submitting}>
            {submitting ? 'Guardando...' : 'Confirmar Entrada'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}