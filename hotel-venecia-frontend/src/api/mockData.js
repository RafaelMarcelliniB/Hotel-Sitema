export const demoUser = {
  username: 'admin',
  nombre: 'Admin',
  apellido: 'Hotel',
  rol: 'admin',
  turno: 'mañana',
  activo: true,
}

export const dashboardMetrics = {
  habitaciones: {
    ocupadas: 18,
    disponibles: 26,
    limpieza: 4,
    mantenimiento: 2,
    reservadas: 3,
  },
  ingresosDia: 12580,
  deudasPendientes: 3180,
  proximosCheckouts: 6,
  pagos: [
    { name: 'Efectivo', value: 54 },
    { name: 'Yape', value: 31 },
    { name: 'Tarjeta', value: 15 },
  ],
  ocupacionPorTipo: [
    { name: 'Simple', ocupadas: 5 },
    { name: 'Doble', ocupadas: 4 },
    { name: 'Suite', ocupadas: 3 },
    { name: 'Matri', ocupadas: 6 },
  ],
  ingresosSemana: [
    { name: 'Lun', ingresos: 8200 },
    { name: 'Mar', ingresos: 9400 },
    { name: 'Mié', ingresos: 10100 },
    { name: 'Jue', ingresos: 12350 },
    { name: 'Vie', ingresos: 13620 },
    { name: 'Sáb', ingresos: 14980 },
    { name: 'Dom', ingresos: 11800 },
  ],
  productosMasVendidos: [
    { name: 'Agua', ventas: 34 },
    { name: 'Papas', ventas: 28 },
    { name: 'Pilas', ventas: 19 },
    { name: 'Preservativo', ventas: 16 },
  ],
  horasPico: [
    { name: '18h', ingresos: 4 },
    { name: '20h', ingresos: 8 },
    { name: '22h', ingresos: 12 },
    { name: '00h', ingresos: 10 },
    { name: '02h', ingresos: 6 },
  ],
}

export const habitaciones = [
  { id: 1, numero: '101', piso: 1, tipo: 'SIMPLE', estado_ocupacion: 'DISPONIBLE', estado_limpieza: 'LIMPIO', tarifa_dia: 70 },
  { id: 2, numero: '102', piso: 1, tipo: 'DOBLE', estado_ocupacion: 'OCUPADO', estado_limpieza: 'SUCIO', tarifa_dia: 90 },
  { id: 3, numero: '201', piso: 2, tipo: 'SUITE', estado_ocupacion: 'RESERVADO', estado_limpieza: 'LIMPIO', tarifa_dia: 140 },
]

export const productos = [
  { id: 1, nombre: 'Agua', categoria: 'BEBIDA', stock_almacen: 30, stock_recepcion: 8, stock_refrigeradora: 4, stock_total: 42, stock_minimo: 10, precio_unitario: 3.5, activo: true },
  { id: 2, nombre: 'Papas', categoria: 'SNACK', stock_almacen: 18, stock_recepcion: 0, stock_refrigeradora: 0, stock_total: 18, stock_minimo: 8, precio_unitario: 5.0, activo: true },
  { id: 3, nombre: 'Preservativo', categoria: 'PRESERVATIVO', stock_almacen: 9, stock_recepcion: 0, stock_refrigeradora: 0, stock_total: 9, stock_minimo: 12, precio_unitario: 8.5, activo: true },
]

export const espacios = [
  { id: 1, numero: 'C-01', tipo: 'AUTO', estado: 'LIBRE' },
  { id: 2, numero: 'C-02', tipo: 'MOTO', estado: 'OCUPADO' },
  { id: 3, numero: 'C-03', tipo: 'BUS', estado: 'LIBRE' },
]

export const cajas = [
  { id: 1, trabajador: 'Admin Hotel', turno: 'mañana', estado: 'ABIERTA', monto_inicial: 300 },
  { id: 2, trabajador: 'María Recepción', turno: 'tarde', estado: 'CERRADA', monto_inicial: 250 },
]

export const recados = [
  { id: 1, contenido: 'Revisar habitación 201 antes de las 20:00', prioridad: 'ALTA', color_alerta: 'ROJO', leido: false },
  { id: 2, contenido: 'Hay stock bajo de agua y papas', prioridad: 'MEDIA', color_alerta: 'AMARILLO', leido: true },
]
