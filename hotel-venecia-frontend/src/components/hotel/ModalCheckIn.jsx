import React, { useState, useEffect } from 'react';
import { Button } from '../ui/Button';
import { Select } from '../ui/Select';
import CajaBlockedModal from '../ui/CajaBlockedModal';
import { useCajaBlocked } from '../../hooks/useCajaBlocked';
import { useNavigate } from 'react-router-dom';
import api from '../../api/axiosConfig';

export default function ModalCheckIn({ habitacion, onClose, onSuccess, initialData }) {
  const navigate = useNavigate();
  const { mostrarBloqueo, cajaActiva } = useCajaBlocked();
  
  const [loading, setLoading] = useState(false);
  const [montoPagado, setMontoPagado] = useState(habitacion?.precio || 0);
  const [turnoIngreso, setTurnoIngreso] = useState('DIA');
  const [tipoPago, setTipoPago] = useState('EFECTIVO');
  const [esPareja, setEsPareja] = useState(false);
  const [showCajaBlocked, setShowCajaBlocked] = useState(false);

  // Formulario del Huésped
  const [huesped, setHuesped] = useState({
    nombre: '',
    apellido: '',
    dni_pasaporte: '',
    telefono: '',
    ciudad_origen: '',
    nacionalidad: 'PERU',
    estado_civil: 'SOLTERO',
    tipo_visita: 'INDEPENDIENTE'
  });

  // Prefill with initialData when provided (e.g., coming from a reserva)
  const splitNombreCompleto = (valor) => {
    const raw = String(valor || '').trim()
    if (!raw) return { nombre: '', apellido: '' }
    const partes = raw.split(/\s+/)
    if (partes.length === 1) return { nombre: partes[0], apellido: '' }
    return {
      nombre: partes[0],
      apellido: partes.slice(1).join(' '),
    }
  }

  useEffect(() => {
    if (!initialData) return
    const nombreRaw = initialData?.huesped?.nombre || initialData?.cliente_nombre || ''
    const { nombre, apellido } = splitNombreCompleto(nombreRaw)
    if (initialData.huesped) {
      setHuesped(prev => ({
        ...prev,
        ...initialData.huesped,
        nombre: initialData.huesped.nombre || nombre || prev.nombre || '',
        apellido: initialData.huesped.apellido || apellido || prev.apellido || '',
      }))
    } else {
      setHuesped(prev => ({
        ...prev,
        nombre: nombre || prev.nombre || '',
        apellido: apellido || prev.apellido || '',
      }))
    }
    // Asegurar mapeo flexible y determinista del teléfono desde la reserva
    const celularReal = (
      initialData?.cliente_telefono ||
      initialData?.telefono ||
      initialData?.celular ||
      initialData?.cliente?.celular ||
      initialData?.cliente?.telefono ||
      ''
    )
    setHuesped(prev => ({
      ...prev,
      telefono: prev.telefono || celularReal || (initialData.huesped && initialData.huesped.telefono) || ''
    }))
    // Prefill monto pagado a partir de los posibles campos de reserva
    const montoPrefill = initialData.monto_pagado ?? initialData.monto_garantia ?? initialData.monto_adelanto ?? initialData.monto_adelanto
    if (montoPrefill !== undefined) setMontoPagado(montoPrefill)
    if (initialData.tipo_pago) setTipoPago(initialData.tipo_pago)
    if (initialData.turno_ingreso) setTurnoIngreso(initialData.turno_ingreso)
  }, [initialData])

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setHuesped(prev => ({ ...prev, [name]: value }));
  };

  const handleBuscarHuesped = async () => {
    if (!huesped.dni_pasaporte) return;
    try {
      setLoading(true);
      const response = await api.get(`/hotel/huespedes/?dni=${huesped.dni_pasaporte}`);
      if (response.data && response.data.length > 0) {
        const found = response.data[0];
        setHuesped({
          nombre: found.nombre || '',
          apellido: found.apellido || '',
          dni_pasaporte: found.dni_pasaporte || '',
          telefono: found.telefono || '',
          ciudad_origen: found.ciudad_origen || '',
          nacionalidad: found.nacionalidad || 'PERU',
          estado_civil: found.estado_civil || 'SOLTERO',
          tipo_visita: found.tipo_visita || 'INDEPENDIENTE'
        });
      }
    } catch (err) {
      console.error("Error al buscar huésped:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmarIngreso = async (e) => {
    e.preventDefault();
    
    // 🔒 BLOQUEO DE SEGURIDAD: Validar caja abierta ANTES de enviar
    if (!cajaActiva) {
      setShowCajaBlocked(true);
      return;
    }
    
    if (!huesped.nombre || !huesped.apellido || !huesped.dni_pasaporte) {
      alert("Por favor, complete los datos obligatorios del huésped (Nombre, Apellido y Documento).");
      return;
    }

    try {
      setLoading(true);

      const payload = {
        turno_ingreso: turnoIngreso,
        tipo_pago: tipoPago,
        monto_pagado: Number(montoPagado),
        es_pareja: esPareja,
        habitacion_id: habitacion.id,
        // Si venimos desde una reserva, enviar `reserva_id` para que el backend lo asocie.
        ...(initialData?.id ? { reserva_id: initialData.id, from_reserva: true } : {}),
        // Preferir enviar `huesped_id` cuando existe, para evitar duplicados; sino enviar datos completos.
        ...(huesped?.id ? { huesped_id: huesped.id } : { huesped: {
          nombre: huesped.nombre,
          apellido: huesped.apellido,
          dni_pasaporte: huesped.dni_pasaporte,
          telefono: huesped.telefono,
          ciudad_origen: huesped.ciudad_origen,
          nacionalidad: huesped.nacionalidad,
          estado_civil: huesped.estado_civil,
          tipo_visita: huesped.tipo_visita
        }})
      };

      await api.post('/hotel/checkin/', payload);
      onSuccess();
    } catch (err) {
      console.error("Error en el Check-in:", err);
      
      // Si el error es de caja no abierta, mostrar modal de bloqueo
      if (err.response?.status === 400 && 
          err.response?.data?.detail?.includes("Debe aperturar")) {
        setShowCajaBlocked(true);
      } else {
        const errorServer = err.response?.data?.detail || 
                          err.response?.data?.error || 
                          "Error al registrar el ingreso.";
        alert(errorServer);
      }
    } finally {
      setLoading(false);
    }
  };

  if (!habitacion) return null;

  return (
    <>
      {/* MODAL DE BLOQUEO DE CAJA */}
      <CajaBlockedModal 
        isOpen={showCajaBlocked}
        onClose={() => setShowCajaBlocked(false)}
        onNavigateToCaja={() => {
          navigate('/caja');
          onClose();
        }}
      />
      
      {/* Backdrop for drawer: lower than global alerts */}
      <div className="fixed inset-0 bg-slate-900/50 z-30 backdrop-blur-sm" onClick={onClose} />
      
      {/* Drawer modal: sits under global alerts (z-40) */}
      <div className="fixed right-0 top-0 h-full w-full max-w-md bg-white z-40 shadow-2xl flex flex-col animate-in slide-in-from-right duration-200">
        
        {/* Cabecera */}
        <div className="p-6 border-b bg-emerald-50 flex justify-between items-center">
          <div>
            <h3 className="text-xl font-bold text-emerald-900">Habitación #{habitacion.numero}</h3>
            <p className="text-[10px] text-emerald-600 font-black uppercase tracking-widest">Registrar Ingreso (Check-In)</p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-800 text-2xl">&times;</button>
        </div>

        <form onSubmit={handleConfirmarIngreso} className="flex-1 overflow-y-auto p-6 space-y-5">
          
          {/* Bloque Búsqueda de Huésped */}
          <div className="space-y-3 bg-slate-50 p-4 rounded-xl border border-slate-200">
            <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Datos del Huésped</h4>
            
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">DNI / Pasaporte *</label>
              <div className="flex gap-2">
                <input 
                  type="text" 
                  name="dni_pasaporte" 
                  value={huesped.dni_pasaporte} 
                  onChange={handleInputChange}
                  className="flex-1 text-sm border px-3 py-2 rounded-lg focus:outline-emerald-500"
                  required
                />
                <button 
                  type="button" 
                  onClick={handleBuscarHuesped}
                  className="bg-slate-800 text-white text-xs px-3 rounded-lg hover:bg-slate-700 transition-colors"
                >
                  Buscar
                </button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">Nombre *</label>
                <input type="text" name="nombre" value={huesped.nombre} onChange={handleInputChange} className="w-full text-sm border px-3 py-2 rounded-lg" required />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">Apellido *</label>
                <input type="text" name="apellido" value={huesped.apellido} onChange={handleInputChange} className="w-full text-sm border px-3 py-2 rounded-lg" required />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">Celular</label>
                <input type="text" name="telefono" value={huesped.telefono} onChange={handleInputChange} className="w-full text-sm border px-3 py-2 rounded-lg" />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">Ciudad de Origen</label>
                <input type="text" name="ciudad_origen" value={huesped.ciudad_origen} onChange={handleInputChange} className="w-full text-sm border px-3 py-2 rounded-lg" placeholder="Ej. Lima, Huánuco" />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 pt-1">
              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">Nacionalidad</label>
                <Select 
                  name="nacionalidad" 
                  value={huesped.nacionalidad} 
                  onChange={handleInputChange}
                >
                  <option value="PERU">Perú</option>
                  <option value="EXTRANJERO">Extranjero</option>
                </Select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">Estado Civil</label>
                <Select 
                  name="estado_civil" 
                  value={huesped.estado_civil} 
                  onChange={handleInputChange}
                >
                  <option value="SOLTERO">Soltero(a)</option>
                  <option value="PAREJA">En Pareja</option>
                  <option value="CASADO">Casado(a)</option>
                </Select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Tipo de Visita</label>
              <Select 
                name="tipo_visita" 
                value={huesped.tipo_visita} 
                onChange={handleInputChange}
              >
                <option value="INDEPENDIENTE">Independiente</option>
                <option value="VIAJERO">Viajero</option>
                <option value="TURISTA">Turista</option>
              </Select>
            </div>
          </div>

          {/* Detalles del Hospedaje */}
          <div className="space-y-4">
            <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest border-b pb-1">Detalles del Alquiler</h4>
            
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">Turno</label>
                <Select value={turnoIngreso} onChange={(e) => setTurnoIngreso(e.target.value)}>
                  <option value="DIA">Día</option>
                  <option value="TARDE">Tarde</option>
                  <option value="NOCHE">Noche</option>
                  <option value="MADRUGADA">Madrugada</option>
                </Select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">Método Pago</label>
                <Select value={tipoPago} onChange={(e) => setTipoPago(e.target.value)}>
                  <option value="EFECTIVO">Efectivo</option>
                  <option value="YAPE">Yape</option>
                  <option value="PLIN">Plin</option>
                  <option value="TRANSFERENCIA">Transferencia</option>
                  <option value="TARJETA">Tarjeta</option>
                </Select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Monto Pagado Adelantado (S/)</label>
              <input 
                type="number" 
                step="0.01" 
                value={montoPagado} 
                onChange={(e) => setMontoPagado(e.target.value)} 
                className="w-full text-sm border px-3 py-2 rounded-lg font-bold text-slate-800 focus:outline-emerald-500" 
              />
              <p className="text-[11px] text-slate-400 mt-1">Precio sugerido de la habitación: S/ {habitacion.precio}</p>
            </div>

            <div className="flex items-center gap-2 pt-1">
              <input 
                type="checkbox" 
                id="es_pareja" 
                checked={esPareja} 
                onChange={(e) => setEsPareja(e.target.checked)} 
                className="h-4 w-4 text-emerald-600 border-slate-300 rounded"
              />
              <label htmlFor="es_pareja" className="text-xs font-medium text-slate-700 select-none">¿Ingresa acompañado? (Pareja)</label>
            </div>
          </div>

          {/* Botón enviar */}
          <div className="pt-4">
            <Button 
              type="submit" 
              disabled={loading} 
              className="w-full py-4 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl shadow-lg transition-transform active:scale-95"
            >
              {loading ? 'Procesando Registro...' : 'Confirmar Ingreso'}
            </Button>
          </div>

        </form>
      </div>
    </>
  );
}