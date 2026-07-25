import React, { useEffect, useRef, useState } from 'react'
import api from '../../api/axiosConfig'

/**
 * ImportUploader
 * - Botón principal "Descargar Plantilla" con dropdown para elegir formato
 * - Input file alineado y botón "Procesar" para subir y procesar el archivo
 * - Usa TailwindCSS para estilos y JS React (vanilla) para dropdown y manejo
 */
export default function ImportUploader({ onDone }) {
  const [open, setOpen] = useState(false)
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const containerRef = useRef(null)

  // Cierra el dropdown al hacer click fuera
  useEffect(() => {
    function onDocClick(e) {
      if (!containerRef.current) return
      if (!containerRef.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('click', onDocClick)
    return () => document.removeEventListener('click', onDocClick)
  }, [])

  const headers = ['Nombre', 'Categoria', 'Precio Unitario', 'Stock Actual', 'Stock Minimo', 'Tipo Registro', 'Activo']

  async function downloadTemplate(format) {
    try {
      const resp = await api.get(`/market/productos/plantilla/${format}/`, { responseType: 'blob' })
      const blob = new Blob([resp.data], { type: resp.headers['content-type'] })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = format === 'xlsx' ? 'plantilla_productos.xlsx' : 'plantilla_productos.csv'
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
      setOpen(false)
    } catch (e) {
      console.error('Error al descargar plantilla', e)
      alert('Error al descargar plantilla')
    }
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!file) return alert('Seleccione un archivo (.csv, .xlsx, .xls)')
    setLoading(true)
    const fd = new FormData()
    fd.append('file', file)
    try {
      const { data } = await api.post('/market/productos/importar-excel/', fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      alert(`Importación finalizada. Creado: ${data.created} - Actualizado: ${data.updated}`)
      if (onDone) onDone(data)
    } catch (err) {
      console.error(err)
      const msg = err?.response?.data?.detail || 'Error al procesar el archivo'
      alert(msg)
    } finally {
      setLoading(false)
      setFile(null)
      // limpiar input file a nivel DOM si es necesario
      const input = document.querySelector('#import-file-input')
      if (input) input.value = ''
    }
  }

  return (
    <div className="flex items-center space-x-3" ref={containerRef}>
      {/* Dropdown botón principal */}
      <div className="relative inline-block text-left">
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          className="inline-flex items-center px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none"
          aria-expanded={open}
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"></path></svg>
          Descargar Plantilla
          <svg className="w-4 h-4 ml-2" viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.584l3.71-4.354a.75.75 0 111.14.98l-4.25 5a.75.75 0 01-1.14 0l-4.25-5a.75.75 0 01.02-1.06z" clipRule="evenodd"/></svg>
        </button>

        {open && (
          <div className="origin-top-left absolute left-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-20">
            <div className="py-1">
              <button onClick={() => downloadTemplate('xlsx')} className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Plantilla Excel (.xlsx)</button>
              <button onClick={() => downloadTemplate('csv')} className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Plantilla CSV (.csv)</button>
            </div>
          </div>
        )}
      </div>

      {/* Formulario de carga */}
      <form onSubmit={handleSubmit} className="flex items-center space-x-2">
        <label className="flex items-center px-3 py-2 bg-white border rounded-md cursor-pointer text-sm text-gray-700">
          <input id="import-file-input" type="file" accept=".csv,.xlsx,.xls" onChange={(e) => setFile(e.target.files?.[0] || null)} className="hidden" />
          <svg className="w-5 h-5 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 7v4a1 1 0 001 1h3m10-6v6a1 1 0 001 1h3M16 3l-4 4-4-4"></path></svg>
          <span>{file ? file.name : 'Seleccionar archivo'}</span>
        </label>

        <button type="submit" disabled={loading} className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-60">
          {loading ? 'Procesando...' : 'Procesar'}
        </button>
      </form>
    </div>
  )
}
