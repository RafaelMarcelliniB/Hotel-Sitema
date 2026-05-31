export default function Modal({ open, title, children, onClose }) {
  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-4">
      <div className="w-full max-w-lg rounded-3xl bg-white p-6 shadow-2xl">
        <div className="mb-4 flex items-center justify-between gap-3">
          <h3 className="text-lg font-bold text-slate-900">{title}</h3>
          <button className="rounded-full px-3 py-1 text-slate-500 hover:bg-slate-100" onClick={onClose} type="button">×</button>
        </div>
        {children}
      </div>
    </div>
  )
}
