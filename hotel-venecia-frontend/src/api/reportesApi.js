import api from './axiosConfig'

export async function downloadCajaReporte(cajaId) {
  const url = `/caja/${cajaId}/reporte-excel/`
  const resp = await api.get(url, { responseType: 'blob' })
  return { blob: resp.data, headers: resp.headers }
}

export async function downloadReporteVentas(params = {}) {
  const resp = await api.get('/reportes/ventas-excel/', { params, responseType: 'blob' })
  return { blob: resp.data, headers: resp.headers }
}

export default { downloadCajaReporte, downloadReporteVentas }
