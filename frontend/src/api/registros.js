import api from './auth'
import { API_ENDPOINTS } from '@/constants/api'


/**
 * Registra la entrada de un vehículo
 * @param {Object} datos - { placa, tipo_vehiculo, espacio, notas }
 * @returns {Promise}
 */
export function registrarEntrada(datos) {
  return api.post(API_ENDPOINTS.REGISTROS.ENTRADA, datos)
}



// REGISTRAR SALIDA


/**
 * Registra la salida de un vehículo
 * @param {Object} datos - { placa?, registro_id?, notas }
 * @returns {Promise}
 */
export function registrarSalida(datos) {
  return api.post(API_ENDPOINTS.REGISTROS.SALIDA, datos)
}



// BUSCAR REGISTRO ACTIVO


/**
 * Busca un registro activo por placa
 * @param {string} placa - Placa del vehículo
 * @returns {Promise}
 */
export function buscarPorPlaca(placa) {
  return api.get(`${API_ENDPOINTS.REGISTROS.BUSCAR}?placa=${placa}`)
}

/**
 * Busca un registro activo por espacio
 * @param {number} espacioId - ID del espacio
 * @returns {Promise}
 */
export function buscarPorEspacio(espacioId) {
  return api.get(`${API_ENDPOINTS.REGISTROS.BUSCAR}?espacio=${espacioId}`)
}



// HISTORIAL


/**
 * Obtiene el historial de registros con filtros opcionales
 * @param {Object} filtros - { estado?, fecha_desde?, fecha_hasta?, placa? }
 * @returns {Promise}
 */
export function getHistorial(filtros = {}) {
  // Construir query params
  const params = new URLSearchParams()
  
  if (filtros.estado) params.append('estado', filtros.estado)
  if (filtros.fecha_desde) params.append('fecha_desde', filtros.fecha_desde)
  if (filtros.fecha_hasta) params.append('fecha_hasta', filtros.fecha_hasta)
  if (filtros.placa) params.append('placa', filtros.placa)
  
  const queryString = params.toString()
  const url = queryString 
    ? `${API_ENDPOINTS.REGISTROS.HISTORIAL}?${queryString}`
    : API_ENDPOINTS.REGISTROS.HISTORIAL
  
  return api.get(url)
}