export  function Card({ className = '', children, ...props }) {
  return (
    <section className={`rounded-2xl bg-surface p-5 shadow-sm ring-1 ring-black/5 ${className}`} {...props}>
      {children}
    </section>
  )
}

export default Card;