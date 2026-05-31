export default function Spinner({ className = '' }) {
  return <div className={`h-6 w-6 animate-spin rounded-full border-4 border-slate-200 border-t-primary ${className}`} />
}
