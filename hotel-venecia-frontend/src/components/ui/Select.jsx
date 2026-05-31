import { forwardRef } from 'react'

const Select = forwardRef(function Select({ className = '', children, ...props }, ref) {
  return (
    <select
      ref={ref}
      className={`w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20 ${className}`}
      {...props}
    >
      {children}
    </select>
  )
})

export default Select
