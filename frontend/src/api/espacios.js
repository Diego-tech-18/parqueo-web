
import api from './auth'
import { API_ENDPOINTS } from '@/constants/api'



// SECCIONES



/**
 * Obtiene la lista de todas las secciones
 * @returns {Promise}
 */
export function getSecciones() {
  return api.get(API_ENDPOINTS.SECCIONES.LIST)
}


export function getSeccion(id) {
  return api.get(API_ENDPOINTS.SECCIONES.DETAIL(id))
}


export function crearSeccion(datosSeccion) {
  return api.post(API_ENDPOINTS.SECCIONES.CREATE, datosSeccion)
}


export function actualizarSeccion(id, datosSeccion) {
  return api.put(API_ENDPOINTS.SECCIONES.UPDATE(id), datosSeccion)
}


export function eliminarSeccion(id) {
  return api.delete(API_ENDPOINTS.SECCIONES.DELETE(id))
}

/**
 * Reactiva una sección que estaba soft-deleted (activo=false).
 * Preserva el ID original y los espacios/registros asociados.
 */
export function reactivarSeccion(id) {
  return api.post(API_ENDPOINTS.SECCIONES.REACTIVAR(id))
}


// ESPACIOS



export function getEspacios(seccionId = null) {
  const url = seccionId 
    ? `${API_ENDPOINTS.ESPACIOS.LIST}?seccion=${seccionId}`
    : API_ENDPOINTS.ESPACIOS.LIST
  
  return api.get(url)
}


export function getEspacio(id) {
  return api.get(API_ENDPOINTS.ESPACIOS.DETAIL(id))
}


export function crearEspacio(datosEspacio) {
  return api.post(API_ENDPOINTS.ESPACIOS.CREATE, datosEspacio)
}


export function actualizarEspacio(id, datosEspacio) {
  return api.put(API_ENDPOINTS.ESPACIOS.UPDATE(id), datosEspacio)
}


export function eliminarEspacio(id) {
  return api.delete(API_ENDPOINTS.ESPACIOS.DELETE(id))
}


export function cambiarEstadoEspacio(id, datos) {
  return api.post(API_ENDPOINTS.ESPACIOS.CAMBIAR_ESTADO(id), {
    estado: datos.estado,
    notas: datos.notas || ''
  })
}

/**
 * Reactiva un espacio que estaba soft-deleted (activo=false).
 * Preserva el ID original y los registros históricos asociados.
 * @param {number} id - ID del espacio inactivo
 * @returns {Promise}
 */
export function reactivarEspacio(id) {
  return api.post(API_ENDPOINTS.ESPACIOS.REACTIVAR(id))
}



// MAPA COMPLETO


/**
 * Obtiene el mapa completo del parqueo
 * Incluye todas las secciones con sus espacios
 * @returns {Promise}
 * 
 * USO:
 *   const respuesta = await getMapaCompleto()
 *   const secciones = respuesta.data
 */
export function getMapaCompleto() {
  return api.get(API_ENDPOINTS.MAPA.COMPLETO)
}