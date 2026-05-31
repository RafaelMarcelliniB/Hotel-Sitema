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
      { path: 'hotel', element: <Hotel /> },
      { path: 'market', element: <Market /> },
      { path: 'cochera', element: <Cochera /> },
      { path: 'caja', element: <Caja /> },
      { path: 'recados', element: <Recados /> },
    ],
  },
  {
    path: '*',
    element: <NotFound />,
  },
])
