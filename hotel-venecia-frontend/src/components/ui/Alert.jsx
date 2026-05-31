export default function Alert({ variant = 'neutral', className = '', children }) {
  const variants = {
    neutral: 'bg-slate-100 text-slate-700',
    success: 'bg-success/10 text-success',
    warning: 'bg-warning/20 text-yellow-900',
    danger: 'bg-danger/10 text-danger',
  }

  return <div className={`rounded-xl px-4 py-3 text-sm ${variants[variant] || variants.neutral} ${className}`}>{children}</div>
}
