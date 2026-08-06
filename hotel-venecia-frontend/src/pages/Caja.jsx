import { useState } from 'react'
import { useCajas } from '../hooks/useCajas'
import { downloadCajaReporte } from '../api/reportesApi'
import { Modal } from '../components/ui/Modal'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import ModalAperturaCaja from '../components/caja/ModalAperturaCaja'

const getFileNameFromContentDisposition = (contentDisposition) => {
  if (!contentDisposition) return null

  const filenameRegex = /filename\*?=(?:UTF-8''|"|')?([^;"']+)/i
  const match = filenameRegex.exec(contentDisposition)
  if (!match) return null

  const rawFileName = match[1].replace(/^("|')|("|')$/g, '')
  try {
    return decodeURIComponent(rawFileName)
  } catch (error) {
    return rawFileName
  }
}

// Componente simple para mostrar estados de carga
const Spinner = () => (
  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
)

export default function Caja() {
  // Extraemos las utilidades de nuestro hook personalizado
  const { useResumen, cerrarCaja, isLoading: loadingHook } = useCajas()
  const { data: resumen, isLoading: loadingResumen, error } = useResumen()
  const [showApertura, setShowApertura] = useState(false)
  const [isDownloading, setIsDownloading] = useState(false)

  // 1. Estado de carga inicial
  if (loadingHook || loadingResumen) {
    return (
      <div className="flex justify-center items-center py-20">
        <Spinner />
        <span className="ml-3 text-slate-600">Cargando información de caja...</span>
      </div>
    )
  }

  // 2. Si no hay caja activa (el backend devuelve 404 o resumen.caja es nulo)
  if (!resumen || !resumen.caja) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] text-center px-4">
        <div className="bg-slate-100 p-6 rounded-full mb-4">
          <svg className="w-12 h-12 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 12H4M12 4v16m8-8H4" />
          </svg>
        </div>
        <h2 className="text-xl font-bold text-slate-800">No hay una caja abierta para este turno</h2>
        <p className="text-slate-500 mb-6">Debes realizar la apertura para registrar movimientos.</p>
        
        <Button onClick={() => setShowApertura(true)} className="px-8">
          Abrir Nueva Caja
        </Button>

        <ModalAperturaCaja 
          open={showApertura} 
          onClose={() => setShowApertura(false)} 
        />
      </div>
    )
  }

  // 3. Interfaz de Caja Activa (cuando el backend responde con 200 OK)
  return (
    <div className="space-y-6 p-6 max-w-7xl mx-auto">
      {/* Cabecera con Información del Turno */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white p-4 rounded-lg shadow-sm border border-slate-200">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">Gestión de Caja</h2>
          <div className="flex items-center gap-2 mt-1">
            <span className="flex h-2 w-2 rounded-full bg-green-500"></span>
            <p className="text-sm text-slate-600">
              Turno: <span className="font-bold uppercase text-blue-700">{resumen.caja.turno}</span>
            </p>
            <span className="text-slate-300">|</span>
            <p className="text-sm text-slate-600">
              Apertura: {(() => {
                const raw = resumen.caja.fecha_apertura
                if (!raw) return ''
                // Evitar desfase UTC cuando backend envía 'YYYY-MM-DD'
                const iso = (typeof raw === 'string' && raw.length === 10) ? `${raw}T00:00:00` : raw
                try {
                  const d = new Date(iso)
                  // Forzar visualización en zona local del navegador
                  return d.toLocaleDateString('es-PE')
                } catch (e) {
                  return raw
                }
              })()}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <Button
            variant="secondary"
            onClick={async () => {
              if (!resumen?.caja?.id) return
              try {
                setIsDownloading(true)
                const { blob, headers } = await downloadCajaReporte(resumen.caja.id)
                const fileName = getFileNameFromContentDisposition(headers?.['content-disposition']) || `reporte_caja_${resumen.caja.id}.xlsx`
                const url = window.URL.createObjectURL(new Blob([blob]))
                const link = document.createElement('a')
                link.href = url
                link.setAttribute('download', fileName)
                document.body.appendChild(link)
                link.click()
                link.parentNode.removeChild(link)
                window.URL.revokeObjectURL(url)
              } catch (err) {
                console.error(err)
                alert('Error al generar el reporte.')
              } finally {
                setIsDownloading(false)
              }
            }}
            disabled={isDownloading}
            className="mr-2"
          >
            {isDownloading ? 'Generando...' : 'Generar Reporte de Ventas'}
          </Button>

          <Button 
            variant="danger" 
            onClick={() => {
              if(window.confirm("¿Estás seguro que deseas cerrar el turno actual?")) {
                cerrarCaja({})
              }
            }}
            className="bg-red-600 hover:bg-red-700 text-white"
          >
            Finalizar Turno
          </Button>
        </div>
      </div>

      {/* Tarjetas de Totales - Ajustado de lg:grid-cols-4 a lg:grid-cols-5 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <Card className="border-l-4 border-l-blue-500">
          <p className="text-xs font-bold text-slate-500 uppercase">Monto Inicial</p>
          <p className="text-2xl font-bold text-slate-800">S/ {Number(resumen.monto_inicial).toFixed(2)}</p>
        </Card>
        
        <Card className="border-l-4 border-l-green-500">
          <p className="text-xs font-bold text-slate-500 uppercase">Efectivo Total</p>
          <p className="text-2xl font-bold text-green-600">S/ {Number(resumen.total_efectivo).toFixed(2)}</p>
        </Card>

        <Card className="border-l-4 border-l-purple-500">
          <p className="text-xs font-bold text-slate-500 uppercase">Yape / Plin</p>
          <p className="text-2xl font-bold text-purple-600">S/ {Number(resumen.total_yape).toFixed(2)}</p>
        </Card>

        <Card className="border-l-4 border-l-orange-500">
          <p className="text-xs font-bold text-slate-500 uppercase">Tarjetas</p>
          <p className="text-2xl font-bold text-orange-600">S/ {Number(resumen.total_tarjeta).toFixed(2)}</p>
        </Card>

        {/* AGREGADO: Quinto recuadro idéntico para el Total General */}
        <Card className="border-l-4 border-l-slate-700">
          <p className="text-xs font-bold text-slate-500 uppercase">Total General</p>
          <p className="text-2xl font-bold text-slate-800">S/ {Number(resumen.total_general || 0).toFixed(2)}</p>
        </Card>
      </div>

      {/* Sección de Movimientos Recientes */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
        <div className="p-4 border-b border-slate-100 bg-slate-50">
          <h3 className="font-bold text-slate-700">Movimientos del Turno</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-500 uppercase text-xs">
              <tr>
                <th className="px-4 py-3">Hora</th>
                <th className="px-4 py-3">Módulo</th>
                <th className="px-4 py-3">Descripción</th>
                <th className="px-4 py-3">Tipo</th>
                <th className="px-4 py-3 text-right">Monto</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {resumen.movimientos && resumen.movimientos.length > 0 ? (
                resumen.movimientos.map((mov) => (
                  <tr key={mov.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-3 text-slate-500">
                      {new Date(mov.fecha_hora).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                    </td>
                    <td className="px-4 py-3 font-medium text-slate-700">{mov.modulo}</td>
                    <td className="px-4 py-3 text-slate-600">{mov.descripcion || mov.referencia}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-full text-[10px] font-bold ${
                        mov.tipo === 'INGRESO' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                      }`}>\
                        {mov.tipo}
                      </span>
                    </td>
                    <td className={`px-4 py-3 text-right font-bold ${
                      mov.tipo === 'INGRESO' ? 'text-green-600' : 'text-red-600'
                    }`}>\
                      {mov.tipo === 'INGRESO' ? '+' : '-'} S/ {Number(mov.monto).toFixed(2)}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" className="px-4 py-10 text-center text-slate-400">
                    No hay movimientos registrados en este turno.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}