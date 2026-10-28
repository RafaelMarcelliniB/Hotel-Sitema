// Reemplazo no bloqueante de alert()/confirm().
// En la app de escritorio (pywebview/WebView2) los diálogos nativos del navegador
// dejan la ventana sin foco: los inputs dejan de aceptar texto hasta que se hace clic fuera.
// Por eso se usan avisos y confirmaciones dibujados dentro de la propia página.

const listeners = new Set()
let nextId = 1

function emit(event) {
  listeners.forEach((listener) => listener(event))
}

export function subscribeDialogs(listener) {
  listeners.add(listener)
  return () => listeners.delete(listener)
}

function inferTone(message) {
  const text = String(message).toLowerCase()
  if (/^(✅)|correctamente|con éxito|finalizada|registrada/.test(text)) return 'success'
  if (/^(⚠️|❌)|error|no se pudo|no puedes|inválid|expirada|insuficiente|obligatorios|selecciona|seleccione|debe ser|sin stock/.test(text)) return 'error'
  return 'info'
}

export function notify(message, tone) {
  const text = typeof message === 'string' ? message : String(message ?? '')
  emit({ type: 'toast', id: nextId++, message: text, tone: tone || inferTone(text) })
}

export function confirmDialog(message) {
  return new Promise((resolve) => {
    emit({ type: 'confirm', id: nextId++, message: String(message ?? ''), resolve })
  })
}

export function installDialogOverrides() {
  window.alert = (message) => notify(message)
}
