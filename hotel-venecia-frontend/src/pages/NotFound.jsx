import { Link } from 'react-router-dom'

import Button from '../components/ui/Button'

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-background text-center">
      <p className="text-sm uppercase tracking-[0.3em] text-slate-500">404</p>
      <h1 className="text-3xl font-bold">Página no encontrada</h1>
      <Link to="/">
        <Button>Volver al inicio</Button>
      </Link>
    </div>
  )
}
