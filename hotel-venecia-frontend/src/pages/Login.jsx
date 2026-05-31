import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import Input from '../components/ui/Input'
import { login } from '../api/authApi'
import { useAuthStore } from '../store/authStore'

export default function Login() {
  const navigate = useNavigate()
  const setSession = useAuthStore((state) => state.setSession)
  const [form, setForm] = useState({ username: 'admin', password: 'admin123' })
  const [error, setError] = useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')

    try {
      const data = await login(form)
      setSession({ user: data.user, token: data.access })
      navigate('/', { replace: true })
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-6">
      <Card className="w-full max-w-md space-y-5">
        <div>
          <p className="text-sm text-slate-500">Hotel Venecia</p>
          <h1 className="text-3xl font-bold">Acceso al sistema</h1>
        </div>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <Input value={form.username} onChange={(event) => setForm({ ...form, username: event.target.value })} placeholder="Usuario" />
          <Input type="password" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} placeholder="Contraseña" />
          {error ? <p className="text-sm text-danger">{error}</p> : null}
          <Button className="w-full" type="submit">Ingresar</Button>
        </form>
      </Card>
    </div>
  )
}
