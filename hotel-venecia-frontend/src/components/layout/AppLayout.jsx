import { Outlet } from 'react-router-dom'

import Sidebar from './Sidebar'
import TopBar from './TopBar'

export default function AppLayout() {
  return (
    <div className="flex min-h-screen bg-background text-slate-900">
      <Sidebar />
      <main className="flex min-w-0 flex-1 flex-col">
        <TopBar />
        <div className="flex-1 p-6">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
