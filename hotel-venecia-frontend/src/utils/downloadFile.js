import { notify } from './dialogs'

export function filenameFromDisposition(disposition, fallback) {
  const match = /filename\*?=(?:UTF-8'')?"?([^";]+)"?/i.exec(disposition || '')
  if (!match) return fallback
  try { return decodeURIComponent(match[1]) } catch { return match[1] }
}

function blobToBase64(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result).split(',')[1] || '')
    reader.onerror = () => reject(reader.error)
    reader.readAsDataURL(blob)
  })
}

// Guarda un blob como archivo. En la app de escritorio abre el diálogo "Guardar como";
// en el navegador usa la descarga estándar. Siempre avisa del resultado.
export async function saveBlobAsFile(blob, filename) {
  const api = window.pywebview?.api
  if (api?.save_download) {
    const content = await blobToBase64(blob)
    const result = await api.save_download(filename, content)
    if (!result?.path) {
      notify('Descarga cancelada.', 'info')
      return null
    }
    notify(`Archivo guardado en:\n${result.path}`, 'success')
    return result.path
  }

  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.style.display = 'none'
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.setTimeout(() => window.URL.revokeObjectURL(url), 1000)
  notify(`Descarga iniciada: ${filename}`, 'success')
  return filename
}

// Convierte la respuesta de error de DRF ({detail} o {campo: [mensajes]}) en texto legible.
export function apiErrorMessage(error, fallback) {
  const data = error?.response?.data
  if (!data) return error?.message ? `${fallback} (${error.message})` : fallback
  if (typeof data === 'string') return fallback
  if (data.detail) return String(data.detail)
  const lines = Object.entries(data).map(([field, messages]) => {
    const text = Array.isArray(messages) ? messages.join(' ') : String(messages)
    return field === 'non_field_errors' ? text : `${field}: ${text}`
  })
  return lines.length ? lines.join('\n') : fallback
}
