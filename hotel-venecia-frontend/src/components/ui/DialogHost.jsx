import { useEffect, useState } from 'react'
import { subscribeDialogs } from '../../utils/dialogs'

const TONE_STYLES = {
  success: 'border-emerald-200 bg-emerald-50 text-emerald-900',
  error: 'border-red-200 bg-red-50 text-red-900',
  info: 'border-slate-200 bg-white text-slate-800',
}

export default function DialogHost() {
  const [toasts, setToasts] = useState([])
  const [confirms, setConfirms] = useState([])

  useEffect(() => subscribeDialogs((event) => {
    if (event.type === 'toast') {
      setToasts((current) => [...current, event])
      const duration = event.tone === 'error' || event.message.length > 90 ? 9000 : 5000
      setTimeout(() => setToasts((current) => current.filter((toast) => toast.id !== event.id)), duration)
    } else if (event.type === 'confirm') {
      setConfirms((current) => [...current, event])
    }
  }), [])

  const closeToast = (id) => setToasts((current) => current.filter((toast) => toast.id !== id))
  const answer = (dialog, value) => {
    setConfirms((current) => current.filter((item) => item.id !== dialog.id))
    dialog.resolve(value)
  }

  const activeConfirm = confirms[0]

  return (
    <>
      <div className="pointer-events-none fixed right-4 top-4 z-[100] flex w-full max-w-sm flex-col gap-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            role="status"
            className={`pointer-events-auto flex items-start gap-3 rounded-xl border px-4 py-3 text-sm shadow-lg ${TONE_STYLES[toast.tone] || TONE_STYLES.info}`}
          >
            <p className="flex-1 whitespace-pre-line break-words">{toast.message}</p>
            <button type="button" onClick={() => closeToast(toast.id)} className="text-lg leading-none opacity-60 hover:opacity-100" aria-label="Cerrar">×</button>
          </div>
        ))}
      </div>

      {activeConfirm && (
        <div className="fixed inset-0 z-[110] flex items-center justify-center bg-slate-950/60 p-4" role="alertdialog" aria-modal="true">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
            <p className="whitespace-pre-line text-sm text-slate-800">{activeConfirm.message}</p>
            <div className="mt-6 flex justify-end gap-2">
              <button type="button" onClick={() => answer(activeConfirm, false)} className="rounded-xl px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100">Cancelar</button>
              <button type="button" autoFocus onClick={() => answer(activeConfirm, true)} className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-700">Aceptar</button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
