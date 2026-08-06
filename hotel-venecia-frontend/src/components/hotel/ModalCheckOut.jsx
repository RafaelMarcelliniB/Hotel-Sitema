import React, { useState, useEffect } from 'react';
import { Button } from '../ui/Button';
import { Select } from '../ui/Select';
import api from '../../api/axiosConfig'; // Asegúrate de que esta ruta sea correcta

export default function ModalCheckOut({ habitacion, onClose, onSuccess }) {
  const [loading, setLoading] = useState(false);
  const [datosSalida, setDatosSalida] = useState(null);
  const [metodoPago, setMetodoPago] = useState('EFECTIVO');

  // 1. Identificamos el ID del check-in que viene del backend (Serializer actualizado)
  const checkinId = habitacion?.checkin_actual_id;

  // 2. Efecto para cargar los datos reales del check-in al abrir el modal
  useEffect(() => {
    const fetchResumenSalida = async () => {
      if (!checkinId) {
        console.warn("No se encontró checkin_actual_id en la habitación.");
        return;
      }

      try {
        setLoading(true);
        // Esta ruta debe coincidir con tu ViewSet de CheckIn o una ruta de detalle
        // Traerá: nombre del huésped, dni, subtotal de habitación, consumos, etc.
        const response = await api.get(`/hotel/checkin/${checkinId}/`);
        setDatosSalida(response.data);
      } catch (err) {
        console.error("Error al obtener datos del check-in:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchResumenSalida();
  }, [checkinId]);

  // 3. Función para procesar el pago y liberar la habitación
  const handleConfirmarSalida = async () => {
    if (!checkinId) {
      alert("Error: No hay un registro de ingreso asociado a esta habitación.");
      return;
    }

    try {
      setLoading(true);
      
      // POST al endpoint correcto de checkout
      await api.post(`/hotel/checkout/${checkinId}/`, {
        metodo_pago: metodoPago
      });
      
      alert("Check-out procesado correctamente. Habitación liberada.");
      
      if (onSuccess) {
        onSuccess(); // Esto gatilla useHabitaciones y refresca los datos de caja/dashboard
      }
      
      onClose();   // Cierra el modal
    } catch (err) {
      console.error("Error al procesar el check-out:", err);
      const errorMsg = err.response?.data?.error || "Error al procesar la salida.";
      alert(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  if (!habitacion) return null;

  return (
    <>
      {/* Overlay de fondo */}
      <div className="fixed inset-0 bg-slate-900/60 z-50 backdrop-blur-sm" onClick={onClose} />
      
      <div className="fixed right-0 top-0 h-full w-full max-w-md bg-white z-50 shadow-2xl flex flex-col animate-in slide-in-from-right duration-300">
        
        {/* Cabecera dinámica */}
        <div className="p-6 border-b bg-rose-50 flex justify-between items-center">
          <div>
            <h3 className="text-xl font-bold text-rose-900">Habitación #{habitacion.numero}</h3>
            <p className="text-[10px] text-rose-600 font-black uppercase tracking-widest">Finalizar Estancia (Check-Out)</p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-rose-600 transition-colors text-2xl">&times;</button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          
          {/* Información del Huésped Cargada desde el API */}
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
            <h4 className="text-[10px] font-black text-slate-400 uppercase mb-2 tracking-widest">Huésped Actual</h4>
            {loading && !datosSalida ? (
              <p className="text-xs animate-pulse">Cargando datos...</p>
            ) : (
              <>
                <p className="text-sm font-bold text-slate-800 uppercase">
                  {datosSalida?.huesped?.nombre || "HUESPED NO IDENTIFICADO"}
                </p>
                <p className="text-xs text-slate-500">
                  DNI: {datosSalida?.huesped?.dni_pasaporte || "N/A"}
                </p>
              </>
            )}
          </div>

          {/* Detalle de Cargos */}
          <div className="space-y-4">
            <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest border-b pb-2">Detalle de Cargos</h4>
            
            <div className="flex justify-between text-sm">
              <span className="text-slate-600">Alquiler de Habitación</span>
              {/* Mostrar solo el saldo restante de la habitación (no volver a cobrar lo ya pagado) */}
              <span className="font-bold">S/ {(Math.max((Number(datosSalida?.monto_habitacion || 0) - Number(datosSalida?.monto_pagado || 0)), 0)).toFixed(2)}</span>
            </div>

            {/* VEHÍCULO VINCULADO (si existe) */}
            {datosSalida?.vehiculos_cochera && datosSalida.vehiculos_cochera.length > 0 && (
              <div className="space-y-2 p-3 bg-slate-50 rounded">
                <h5 className="text-xs font-bold text-slate-600">Vehículo registrado en cochera</h5>
                {datosSalida.vehiculos_cochera.map((v) => (
                  <div key={v.id} className="text-sm flex justify-between">
                    <div>
                      <div className="font-semibold">{v.placa} {v.tipo_cliente === 'HUESPED' ? '(Huésped)' : ''}</div>
                      <div className="text-xs text-slate-500">{v.tipo_vehiculo} • Espacio #{v.espacio_numero || 'N/A'}</div>
                    </div>
                    <div className="font-bold text-emerald-700">S/ {Number(v.monto_total || 0).toFixed(2)} {Number(v.monto_total || 0) === 0 ? '(Cortesía)' : ''}</div>
                  </div>
                ))}
              </div>
            )}

            <hr className="border-dashed" />

            <div className="flex justify-between items-baseline">
              <span className="text-lg font-bold text-slate-900">TOTAL A PAGAR:</span>
              <span className="text-2xl font-black text-slate-900">
                S/ {(Number(datosSalida?.saldo_pendiente || 0)).toFixed(2)}
              </span>
            </div>

            {/* Alerta de saldo pendiente si existiera */}
            <div className="bg-rose-50 p-3 rounded-lg flex justify-between items-center text-rose-700">
              <span className="text-xs font-bold uppercase">Saldo Pendiente:</span>
              <span className="font-black">S/ {datosSalida?.saldo_pendiente || '0.00'}</span>
            </div>
          </div>

          {/* Selección de Método de Pago */}
          <div className="pt-2">
            <label className="text-[10px] font-black text-slate-400 uppercase block mb-2">Método de Pago para Saldo</label>
            <Select 
              value={metodoPago} 
              onChange={(e) => setMetodoPago(e.target.value)}
              className="w-full border-slate-200"
            >
              <option value="EFECTIVO">Efectivo</option>
              <option value="YAPE">Yape / Plin</option>
              <option value="TARJETA">Tarjeta de Crédito/Débito</option>
            </Select>
          </div>
        </div>

        {/* Acción Final */}
        <div className="p-6 border-t bg-slate-50">
          <Button 
            onClick={handleConfirmarSalida}
            disabled={loading || !checkinId}
            className="w-full py-4 bg-rose-600 hover:bg-rose-700 text-white font-bold rounded-xl shadow-lg shadow-rose-200 transition-all active:scale-95"
          >
            {loading ? 'Procesando...' : 'Confirmar Salida y Cobrar'}
          </Button>
          <p className="text-[9px] text-center text-slate-400 mt-4 uppercase font-bold tracking-tighter">
            Al confirmar, la habitación pasará a estado "SUCIO" automáticamente.
          </p>
        </div>
      </div>
    </>
  );
}