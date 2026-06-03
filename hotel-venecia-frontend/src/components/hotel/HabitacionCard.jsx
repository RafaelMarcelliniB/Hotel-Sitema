import { Card } from '../ui/Card'
import { Badge } from '../ui/Badge'

const ESTADOS_COLOR = {
  disponible: 'bg-green-100 text-green-800 border-green-200',
  ocupado: 'bg-red-100 text-red-800 border-red-200',
  limpieza: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  mantenimiento: 'bg-gray-100 text-gray-800 border-gray-200',
  salida_proxima: 'bg-orange-100 text-orange-800 border-orange-200'
}

export default function HabitacionCard({ habitacion, onClick }) {
  const colorClass = ESTADOS_COLOR[habitacion.estado_ocupacion] || ESTADOS_COLOR.disponible

  return (
    <div 
      onClick={() => onClick(habitacion)}
      className={`cursor-pointer p-4 rounded-xl border-2 transition-all hover:shadow-md ${colorClass}`}
    >
      <div className="flex justify-between items-start mb-2">
        <span className="text-2xl font-bold">#{habitacion.numero}</span>
        <Badge variant={habitacion.estado_ocupacion === 'disponible' ? 'success' : 'warning'}>
          {habitacion.tipo}
        </Badge>
      </div>
      
      <div className="text-sm font-medium">
        {habitacion.estado_ocupacion === 'ocupado' ? (
          <p className="truncate">👤 {habitacion.huesped_actual || 'Huésped activo'}</p>
        ) : (
          <p>S/ {habitacion.tarifa_dia} - {habitacion.estado_limpieza}</p>
        )}
      </div>
      
      <div className="mt-3 text-xs uppercase tracking-wider font-bold opacity-70">
        {habitacion.estado_ocupacion}
      </div>
    </div>
  )
}