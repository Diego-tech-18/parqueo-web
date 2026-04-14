import api from './auth'
import { API_ENDPOINTS } from '@/constants/api'



export function getUsuarios() {
  return api.get(API_ENDPOINTS.USUARIOS.LIST)  // ✅ Desde constants
}

/**
 * Obtiene un usuario específico por ID
 * @param {number} id - ID del usuario
 * @returns {Promise}
 */
export function getUsuario(id) {
  return api.get(API_ENDPOINTS.USUARIOS.DETAIL(id))  // ✅ Función dinámica
}


export function crearUsuario(datosUsuario) {
  return api.post(API_ENDPOINTS.USUARIOS.CREATE, datosUsuario)  // ✅ Desde constants
}


export function actualizarUsuario(id, datosUsuario) {
  return api.put(API_ENDPOINTS.USUARIOS.UPDATE(id), datosUsuario)  // ✅ Función dinámica
}


export function actualizarUsuarioParcial(id, datosUsuario) {
  return api.patch(API_ENDPOINTS.USUARIOS.UPDATE(id), datosUsuario)
}


export function eliminarUsuario(id) {
  return api.delete(API_ENDPOINTS.USUARIOS.DELETE(id))  // ✅ Función dinámica
}