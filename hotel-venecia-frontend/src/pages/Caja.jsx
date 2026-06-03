import { useState } from 'react'
import Card from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { useCajas } from '../hooks/useCajas'
import Spinner from '../components/ui/Spinner'
import ModalAperturaCaja from '../components/caja/ModalAperturaCaja'

export default function Caja() {
  const { useResumen, cerrarCaja, isLoading } = useCajas()
  const { data: resumen, isLoading: loadingResumen } = useResumen()
  const [showApertura, setShowApertura] = useState(false)

  if (isLoading || loadingResumen) return <Spinner />

  // Si no hay caja abierta (el backend devolvería 404 o null)
  if (!resumen || !resumen.id) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh]">
        <h2 className="text-xl font-bold mb-4">No hay una caja abierta para este turno</h2>
        <Button onClick={() => setShowApertura(true)}>Abrir Nueva Caja</Button>
        {showApertura && <ModalAperturaCaja onClose={() => setShowApertura(false)} />}
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Resumen de Caja: {resumen.turno}</h2>
        <Button variant="danger" onClick={() => { if(confirm("¿Cerrar turno?")) cerrarCaja({}) }}>
          Cerrar Caja
        </Button>
      </div>

      {/* Cards de Saldo */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-green-50 border-green-200">
          <p className="text-sm text-green-600 font-bold uppercase">Efectivo Esperado</p>
          <h3 className="text-3xl font-black">S/ {resumen.total_efectivo || '0.00'}</h3>
        </Card>
        <Card className="bg-blue-50 border-blue-200">
          <p className="text-sm text-blue-600 font-bold uppercase">Yape / Plin</p>
          <h3 className="text-3xl font-black">S/ {resumen.total_yape || '0.00'}</h3>
        </Card>
        <Card className="bg-purple-50 border-purple-200">
          <p className="text-sm text-purple-600 font-bold uppercase">Tarjeta</p>
          <h3 className="text-3xl font-black">S/ {resumen.total_tarjeta || '0.00'}</h3>
        </Card>
      </div>

      {/* Lista de Movimientos */}
      <Card>
        <h3 className="text-lg font-bold mb-4">Últimos Movimientos</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 border-b">
              <tr>
                <th className="p-3">Hora</th>
                <th className="p-3">Módulo</th>
                <th className="p-3">Concepto</th>
                <th className="p-3">Monto</th>
                <th className="p-3">Pago</th>
              </tr>
            </thead>
            <tbody>
              {resumen.movimientos?.map((m) => (
                <tr key={m.id} className="border-b">
                  <td className="p-3">{m.hora}</td>
                  <td className="p-3 font-bold text-slate-500">{m.modulo}</td>
                  <td className="p-3">{m.descripcion}</td>
                  <td className={`p-3 font-bold ${m.tipo === 'INGRESO' ? 'text-green-600' : 'text-red-600'}`}>
                    {m.tipo === 'INGRESO' ? '+' : '-'} S/ {m.monto}
                  </td>
                  <td className="p-3"><span className="px-2 py-1 bg-slate-100 rounded">{m.metodo_pago}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}