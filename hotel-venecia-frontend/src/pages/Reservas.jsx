import { useState, useEffect, useMemo } from 'react'
import { useDisponibles, useVencidas } from '../hooks/useReservas'
import { getReservasPorHabitacion } from '../api/reservaApi'
import HabitacionCard from '../components/hotel/HabitacionCard'
import ModalCheckIn from '../components/hotel/ModalCheckIn'
import ModalReserva from '../components/reservas/ModalReserva'
import ModalVencidas from '../components/reservas/ModalVencidas'
import ModalProcesarReserva from '../components/reservas/ModalProcesarReserva'
import Spinner from '../components/ui/Spinner'
import Card from '../components/ui/Card'
import api from '../api/axiosConfig'

export default function Reservas() {
  const { data: habitaciones, isLoading, refetch } = useDisponibles()
  const [selected, setSelected] = useState(null)
  const [showModal, setShowModal] = useState(false)
  const [procesarOpen, setProcesarOpen] = useState(false)
  const [showCheckIn, setShowCheckIn] = useState(false)
  const [checkInInitialData, setCheckInInitialData] = useState(null)

  const { refetch: refetchVencidas } = useVencidas()
  const [vencidasOpen, setVencidasOpen] = useState(false)
  const [vencidasData, setVencidasData] = useState([])
  const [vencidasLoading, setVencidasLoading] = useState(false)
  const [vencidasError, setVencidasError] = useState(null)

  const handleClick = (hab) => {
    // Si la habitación está RESERVADO abrimos el modal para procesar la reserva activa
    if (hab.estado_ocupacion === 'RESERVADO') {
      setSelected(hab)
      setProcesarOpen(true)
      return
    }
    // Si está DISPONIBLE abrimos el modal de nueva reserva
    setSelected(hab)
    setShowModal(true)
  }

  const handleSuccess = () => {
    setShowModal(false)
    setSelected(null)
    refetch()
    // Forzar actualización de vencidas
    try { refetchVencidas() } catch(e){}
  }

  const handleProcesarSuccess = () => {
    setProcesarOpen(false)
    setSelected(null)
    refetch()
    try { refetchVencidas() } catch(e){}
  }

  const handleOpenCheckInFromReserva = (payload) => {
    setSelected(payload.habitacion || selected)
    setCheckInInitialData({
      id: payload.id,
      huesped: {
        nombre: payload.cliente_nombre || '',
        apellido: payload.cliente_apellido || '',
        dni_pasaporte: payload.cliente_dni || '',
        telefono: payload.cliente_telefono || ''
      },
      monto_pagado: payload.monto_adelanto ?? payload.garantia ?? 0,
      garantia: payload.garantia ?? 0
    })
    setProcesarOpen(false)
    setShowCheckIn(true)
  }

  // Hooks de métricas y tolerancia (siempre en top-level)
  const [reservasByHabitacion, setReservasByHabitacion] = useState({})

  useEffect(() => {
    let mounted = true
    async function fetchReservasPorHab() {
      try {
        const habitacionesReservadas = (habitaciones || []).filter(h => h.estado_ocupacion === 'RESERVADO')
        const map = {}
        await Promise.all(habitacionesReservadas.map(async (h) => {
          try {
            const res = await getReservasPorHabitacion(h.id)
            const reservas = Array.isArray(res) ? res : (res?.data || [])
            map[h.id] = reservas
          } catch (e) {
            map[h.id] = []
          }
        }))
        if (mounted) setReservasByHabitacion(map)
      } catch (e) {
        if (mounted) setReservasByHabitacion({})
      }
    }

    if ((habitaciones || []).length > 0) fetchReservasPorHab()
    else setReservasByHabitacion({})

    return () => { mounted = false }
  }, [habitaciones])

  const { enToleranciaCount, porVencerCount } = useMemo(() => {
    const now = new Date()
    let enTol = 0
    let porVen = 0
    Object.values(reservasByHabitacion).forEach((reservas) => {
      const pendiente = (reservas || []).find(r => r.estado === 'PENDIENTE')
      if (pendiente && pendiente.created_at) {
        const created = new Date(pendiente.created_at)
        const hours = (now - created) / (1000 * 60 * 60)
        if (hours < 3) enTol += 1
        else if (hours >= 3 && hours < 4) porVen += 1
      }
    })
    return { enToleranciaCount: enTol, porVencerCount: porVen }
  }, [reservasByHabitacion])

  if (isLoading) return (<div className="flex h-screen items-center justify-center"><Spinner /></div>)

  return (
    <div className="p-6 bg-slate-50 min-h-screen">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-slate-800">Reservas</h2>
            <p className="text-sm text-slate-500">Crea reservas y gestiona garantías.</p>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Card className="col-span-2">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-slate-500 font-bold uppercase tracking-wider">ESTADO DE HABITACIONES</div>
                <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-2">
                  <div className="flex items-center justify-start text-sm text-slate-700">
                    <span className="w-2.5 h-2.5 rounded-full inline-block mr-2 bg-emerald-500" />
                    <span className="flex-1">Disponibles</span>
                    <span className="font-bold text-slate-800">{(habitaciones || []).filter(h=>h.estado_ocupacion==='DISPONIBLE').length}</span>
                  </div>

                  <div className="flex items-center justify-start text-sm text-slate-700">
                    <span className="w-2.5 h-2.5 rounded-full inline-block mr-2 bg-amber-500" />
                    <span className="flex-1">Reservadas</span>
                    <span className="font-bold text-slate-800">{(habitaciones || []).filter(h=>h.estado_ocupacion==='RESERVADO').length}</span>
                  </div>

                  <div className="flex items-center justify-start text-sm text-slate-700">
                    <span className="w-2.5 h-2.5 rounded-full inline-block mr-2 bg-blue-500" />
                    <span className="flex-1">En Tolerancia</span>
                    <span className="font-bold text-slate-800">{enToleranciaCount}</span>
                  </div>

                  <div className="flex items-center justify-start text-sm text-slate-700">
                    <span className="w-2.5 h-2.5 rounded-full inline-block mr-2 bg-orange-500" />
                    <span className="flex-1">Por Vencer</span>
                    <span className="font-bold text-slate-800">{porVencerCount}</span>
                  </div>
                </div>
              </div>

              <div className="text-xs text-slate-400">Actualizado</div>
            </div>
          </Card>

          <Card className="cursor-pointer" onClick={async () => {
            setVencidasOpen(true)
            setVencidasLoading(true)
            setVencidasError(null)
            try {
              const data = await refetchVencidas()
              setVencidasData(data?.data || data)
            } catch (e) {
              setVencidasError(e)
            } finally {
              setVencidasLoading(false)
            }
          }}>
            <div className="text-sm text-slate-500">Vencidas / Reembolsos Pendientes</div>
            <div className="text-2xl font-bold text-amber-600">{(vencidasData || []).length}</div>
          </Card>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
        {(habitaciones || []).map(hab => (
          <HabitacionCard key={hab.id} habitacion={hab} onClick={handleClick} />
        ))}
      </div>

        {showCheckIn && selected && (
          <ModalCheckIn
            habitacion={selected}
            onClose={() => { setShowCheckIn(false); setSelected(null); setCheckInInitialData(null) }}
            onSuccess={() => { setShowCheckIn(false); setSelected(null); refetch(); }}
            initialData={checkInInitialData}
          />
        )}

      {showModal && selected && (
        <ModalReserva habitacion={selected} onClose={() => setShowModal(false)} onSuccess={handleSuccess} />
      )}

      {procesarOpen && selected && (
        <ModalProcesarReserva
          habitacion={selected}
          isOpen={procesarOpen}
          onClose={() => setProcesarOpen(false)}
          onSuccess={handleProcesarSuccess}
          onOpenCheckIn={handleOpenCheckInFromReserva}
        />
      )}

      <ModalVencidas isOpen={vencidasOpen} onClose={() => setVencidasOpen(false)} reservas={vencidasData || []} loading={vencidasLoading} error={vencidasError} />
    </div>
  )
}
