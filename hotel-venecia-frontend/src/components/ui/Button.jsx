export default function Button({ as: Component = 'button', variant = 'primary', className = '', ...props }) {
  const variants = {
    primary: 'bg-primary text-white hover:bg-indigo-900',
    secondary: 'bg-secondary text-slate-900 hover:bg-yellow-500',
    ghost: 'bg-transparent text-slate-700 hover:bg-slate-100',
    danger: 'bg-danger text-white hover:opacity-90',
  }

  return (
    <Component
      className={`inline-flex items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold transition ${variants[variant] || variants.primary} ${className}`}
      {...props}
    />
  )
}
