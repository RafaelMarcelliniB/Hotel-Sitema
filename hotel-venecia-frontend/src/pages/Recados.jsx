import { useMemo, useState } from 'react'
import Card from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { useRecados } from '../hooks/useRecados'
import Spinner from '../components/ui/Spinner'
import { Modal } from '../components/ui/Modal'
import { Input } from '../components/ui/Input'
import { Select } from '../components/ui/Select'

const FILTERS = [
  { key: 'ALL', label: 'Todos' },
  { key: 'PENDIENTE', label: 'Pendientes' },
  { key: 'PROCESO', label: 'En Proceso' },
  { key: 'RESUELTO', label: 'Resueltos' },
]

const CATEGORY_META = {
  MARKET: { label: 'Market', chip: 'bg-rose-100 text-rose-700', accent: 'border-rose-400' },
  MANTENIMIENTO: { label: 'Mantenimiento', chip: 'bg-amber-100 text-amber-700', accent: 'border-amber-400' },
  LIMPIEZA: { label: 'Limpieza', chip: 'bg-cyan-100 text-cyan-700', accent: 'border-cyan-400' },
  GENERAL: { label: 'General', chip: 'bg-slate-100 text-slate-700', accent: 'border-slate-400' },
}

const STATE_META = {
  PENDIENTE: { label: 'Pendiente', chip: 'bg-rose-100 text-rose-700' },
  PROCESO: { label: 'En Proceso', chip: 'bg-amber-100 text-amber-700' },
  RESUELTO: { label: 'Resuelto', chip: 'bg-emerald-100 text-emerald-700' },
}

export default function Recados() {
  const { recados, isLoading, crearRecado, actualizarEstado } = useRecados()
  const [showModal, setShowModal] = useState(false)
  const [filter, setFilter] = useState('ALL')
  const [form, setForm] = useState({ titulo: '', categoria: 'GENERAL', descripcion: '' })
  const [submitting, setSubmitting] = useState(false)

  const filteredRecados = useMemo(() => {
    if (filter === 'ALL') return recados
    return recados.filter((item) => item.estado === filter)
  }, [filter, recados])

  const handleCreate = async (event) => {
    event.preventDefault()
    if (!form.titulo.trim() || !form.descripcion.trim()) return
    setSubmitting(true)
    try {
      await crearRecado({
        titulo: form.titulo.trim(),
        categoria: form.categoria,
        descripcion: form.descripcion.trim(),
      })
      setForm({ titulo: '', categoria: 'GENERAL', descripcion: '' })
      setShowModal(false)
    } finally {
      setSubmitting(false)
    }
  }

  const handleEstado = async (id, nextState) => {
    await actualizarEstado({ id, estado: nextState })
  }

  if (isLoading) return <Spinner />

  return (
    <div className="space-y-6 p-6">
      <div className="flex flex-col gap-4 rounded-3xl border border-slate-200 bg-white p-5 shadow-sm lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">Comunicación interna</h2>
          <p className="text-sm text-slate-500">Seguimiento rápido entre administrador y recepción.</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {FILTERS.map((item) => (
            <button
              key={item.key}
              type="button"
              onClick={() => setFilter(item.key)}
              className={`rounded-full px-3 py-2 text-sm font-semibold transition ${filter === item.key ? 'bg-primary text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'}`}
            >
              {item.label}
            </button>
          ))}
          <Button onClick={() => setShowModal(true)}>+ Nuevo Recado</Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {filteredRecados.map((recado) => {
          const category = CATEGORY_META[recado.categoria] || CATEGORY_META.GENERAL
          const state = STATE_META[recado.estado] || STATE_META.PENDIENTE
          return (
            <Card key={recado.id} className={`border-l-4 ${category.accent} bg-white shadow-sm`}>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">{recado.titulo}</p>
                  <h3 className="mt-2 text-lg font-semibold text-slate-800">{recado.descripcion}</h3>
                </div>
                <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${category.chip}`}>{category.label}</span>
              </div>

              <div className="mt-4 flex flex-wrap items-center gap-2">
                <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${state.chip}`}>{state.label}</span>
                <span className="text-xs text-slate-500">
                  Por: {recado.creado_por_nombre || 'Sistema'}{recado.creado_por_rol ? ` - ${recado.creado_por_rol}` : ''}
                </span>
              </div>

              <div className="mt-5 border-t border-slate-200 pt-4">
                {recado.estado === 'PENDIENTE' && (
                  <Button className="w-full" onClick={() => handleEstado(recado.id, 'PROCESO')}>
                    Iniciar Tarea
                  </Button>
                )}
                {recado.estado === 'PROCESO' && (
                  <Button className="w-full" variant="secondary" onClick={() => handleEstado(recado.id, 'RESUELTO')}>
                    Marcar como Resuelto
                  </Button>
                )}
                {recado.estado === 'RESUELTO' && (
                  <div className="rounded-xl bg-emerald-50 px-3 py-2 text-sm font-medium text-emerald-700">
                    Tarea completada
                  </div>
                )}
              </div>
            </Card>
          )
        })}
      </div>

      {filteredRecados.length === 0 && (
        <div className="rounded-3xl border border-dashed border-slate-300 bg-slate-50 p-10 text-center text-slate-500">
          No hay recados para este filtro en este momento.
        </div>
      )}

      <Modal open={showModal} title="Nuevo recado" onClose={() => setShowModal(false)}>
        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Título</label>
            <Input
              value={form.titulo}
              onChange={(event) => setForm((current) => ({ ...current, titulo: event.target.value }))}
              placeholder="Ej. Falta de papel higiénico"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Categoría</label>
            <Select
              value={form.categoria}
              onChange={(event) => setForm((current) => ({ ...current, categoria: event.target.value }))}
            >
              <option value="MARKET">Market</option>
              <option value="MANTENIMIENTO">Mantenimiento</option>
              <option value="LIMPIEZA">Limpieza</option>
              <option value="GENERAL">General</option>
            </Select>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Descripción</label>
            <textarea
              value={form.descripcion}
              onChange={(event) => setForm((current) => ({ ...current, descripcion: event.target.value }))}
              className="min-h-28 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none transition placeholder:text-slate-400 focus:border-primary focus:ring-2 focus:ring-primary/20"
              placeholder="Describe la solicitud o comunicación"
            />
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="ghost" onClick={() => setShowModal(false)}>
              Cancelar
            </Button>
            <Button type="submit" disabled={submitting}>
              {submitting ? 'Guardando...' : 'Guardar recado'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}