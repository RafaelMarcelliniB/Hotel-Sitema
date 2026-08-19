import { Badge } from '../ui/Badge'

// Mapeo exacto con los strings en MAYÚSCULAS que vienen de Django
const ESTADOS_COLOR = {
  DISPONIBLE: 'bg-green-100 text-green-800 border-green-300',
  OCUPADO: 'bg-red-100 text-red-800 border-red-300',
  RESERVADO: 'bg-amber-100 text-amber-800 border-amber-300',
  BLOQUEADO: 'bg-gray-100 text-gray-800 border-gray-300',
  MANTENIMIENTO: 'bg-gray-100 text-gray-700 border-gray-400',
  SUCIO: 'bg-amber-100 text-amber-800 border-amber-300' // Color ámbar/amarillo para falta de limpieza
}

export default function HabitacionCard({ habitacion, onClick, onRequestMaintenance }) {
  const estaSucia = habitacion.estado_limpieza === 'SUCIO';
  const estaOcupada = habitacion.estado_ocupacion === 'OCUPADO';
  const estaEnMantenimiento = habitacion.estado_ocupacion === 'MANTENIMIENTO';
  
  // Si no está ocupada pero está sucia, forzamos que use el color SUCIO
  const estadoVisual = (estaSucia && !estaOcupada) ? 'SUCIO' : habitacion.estado_ocupacion;
  const colorClass = ESTADOS_COLOR[estadoVisual] || ESTADOS_COLOR.DISPONIBLE

  return (
    <div
      onClick={() => onClick(habitacion)}
      onContextMenu={(event) => {
        event.preventDefault();
        if (onRequestMaintenance && (habitacion.estado_ocupacion === 'DISPONIBLE' || estaEnMantenimiento)) {
          onRequestMaintenance(habitacion);
        }
      }}
      className={`cursor-pointer p-4 rounded-xl border-2 transition-all hover:shadow-md ${colorClass}`}
    >
      <div className="flex justify-between items-start mb-2">
        <span className="text-2xl font-bold">#{habitacion.numero}</span>
        <Badge variant={habitacion.estado_ocupacion === 'DISPONIBLE' && !estaSucia ? 'success' : 'warning'}>
          {habitacion.tipo}
        </Badge>
      </div>
      
      <div className="text-sm font-medium">
        {estaEnMantenimiento ? (
          <p className="text-gray-600 font-semibold">Habitación fuera de servicio</p>
        ) : estaOcupada ? (
          <p className="truncate">👤 {habitacion.huesped_actual || 'Huésped activo'}</p>
        ) : estaSucia ? (
          <p className="text-amber-700 font-semibold">🧹 Requiere limpieza / desinfección</p>
        ) : (
          <p>S/ {habitacion.tarifa_dia} - {habitacion.estado_limpieza}</p>
        )}
      </div>
      
      <div className="mt-3 text-xs uppercase tracking-wider font-black opacity-80">
        {estaEnMantenimiento ? 'Mantenimiento' : (estaSucia && !estaOcupada) ? 'Falta Limpieza' : habitacion.estado_ocupacion}
      </div>
    </div>
  )
}