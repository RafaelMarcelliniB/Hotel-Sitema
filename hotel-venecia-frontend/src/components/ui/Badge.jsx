export  function Badge({ variant = 'neutral', className = '', children }) {
  const variants = {
    neutral: 'bg-neutral/15 text-slate-700',
    success: 'bg-success/15 text-success',
    warning: 'bg-warning/20 text-yellow-800',
    danger: 'bg-danger/15 text-danger',
    accent: 'bg-accent/15 text-accent',
  }

  return <span className={`inline-flex rounded-full px-3 py-1 text-xs font-bold ${variants[variant] || variants.neutral} ${className}`}>{children}</span>
}

export default Badge;