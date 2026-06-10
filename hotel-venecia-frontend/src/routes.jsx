import { createBrowserRouter } from 'react-router-dom'

import AppLayout from './components/layout/AppLayout'
import ProtectedRoute from './components/layout/ProtectedRoute'
import Caja from './pages/Caja'
import Cochera from './pages/Cochera'
import Dashboard from './pages/Dashboard'
import Hotel from './pages/Hotel'
import Login from './pages/Login'
import Market from './pages/Market'
import NotFound from './pages/NotFound'
import Recados from './pages/Recados'
import Trabajadores from './pages/Trabajadores'

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <AppLayout />
      </ProtectedRoute>
    ),
    children: [
      { index: true, element: <Dashboard /> },
      { 
        path: 'hotel', 
        element: <ProtectedRoute allowedRoles={['admin', 'recepcionista']}><Hotel /></ProtectedRoute> 
      },
      { 
        path: 'market', 
        element: <ProtectedRoute allowedRoles={['admin', 'recepcionista', 'cajero']}><Market /></ProtectedRoute> 
      },
      { 
        path: 'cochera', 
        element: <ProtectedRoute allowedRoles={['admin', 'recepcionista', 'cajero']}><Cochera /></ProtectedRoute> 
      },
      { 
        path: 'caja', 
        element: <ProtectedRoute allowedRoles={['admin', 'cajero']}><Caja /></ProtectedRoute> 
      },
      { 
        path: 'recados', 
        element: <Recados /> // Acceso general para todos los trabajadores
      },
      { 
        path: 'trabajadores', 
        element: <ProtectedRoute allowedRoles={['admin']}><Trabajadores /></ProtectedRoute> 
      },
    ],
  },
  {
    path: '*',
    element: <NotFound />,
  },
])
