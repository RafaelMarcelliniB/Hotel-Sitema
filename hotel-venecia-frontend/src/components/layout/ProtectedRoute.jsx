import { Navigate } from 'react-router-dom'

import { useAuthStore } from '../../store/authStore'

export default function ProtectedRoute({ allowedRoles = [], children }) {
  const user = useAuthStore((state) => state.user)

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (allowedRoles.length > 0 && !allowedRoles.includes(user.rol)) {
    return <Navigate to="/" replace />
  }

  return children
}
