/**
 * Componente: CajaBlockedModal
 * 
 * Modal que se muestra cuando un empleado intenta una operación sin caja abierta.
 * 
 * Props:
 *  - isOpen: boolean - Si el modal está abierto
 *  - onClose: function - Callback para cerrar el modal
 *  - onNavigateToCaja: function - Callback para ir al módulo de caja
 * 
 * Estilo: Alerta llamativa con tema rojo/advertencia
 */

import React from 'react'
import { Button } from './Button'

export default function CajaBlockedModal({ isOpen, onClose, onNavigateToCaja }) {
  if (!isOpen) return null

  return (
    <>
      {/* Overlay (z-45) */}
      <div 
        className="fixed inset-0 bg-slate-900/50 z-[45] backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal (z-50) */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="w-full max-w-sm bg-white rounded-2xl shadow-2xl border-2 border-red-200 animate-in zoom-in duration-200 z-50">
          
          {/* Header */}
          <div className="bg-gradient-to-r from-red-50 to-orange-50 px-6 py-4 border-b border-red-100 flex items-start gap-3">
            <div className="text-4xl mt-1">🔒</div>
            <div>
              <h3 className="text-xl font-black text-red-900">Acción Bloqueada</h3>
              <p className="text-xs text-red-600 font-medium uppercase tracking-wider">Caja no abierta</p>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 space-y-4">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-sm text-red-900 font-medium">
                Es <strong>obligatorio activar tu caja</strong> en el módulo de Caja antes de continuar.
              </p>
            </div>

            <div className="space-y-2 text-sm text-slate-600">
              <p>✓ Abre la app de <strong>Caja</strong></p>
              <p>✓ Haz clic en <strong>"Abrir Caja"</strong></p>
              <p>✓ Ingresa el monto inicial</p>
              <p>✓ Regresa para continuar</p>
            </div>

            {/* Información adicional */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
              <p className="text-xs text-yellow-800">
                <strong>💡 Nota:</strong> Sin caja abierta, no puedes registrar huéspedes ni realizar ventas.
              </p>
            </div>
          </div>

          {/* Footer */}
          <div className="bg-slate-50 px-6 py-4 border-t border-slate-100 flex gap-3">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
            >
              Cancelar
            </button>
            <button
              onClick={onNavigateToCaja}
              className="flex-1 px-4 py-2 text-sm font-bold text-white bg-gradient-to-r from-red-600 to-red-700 rounded-lg hover:from-red-700 hover:to-red-800 transition-all shadow-lg hover:shadow-xl"
            >
              Ir a Caja
            </button>
          </div>
        </div>
      </div>
    </>
  )
}
