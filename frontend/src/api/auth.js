// autentificacion
import axios from 'axios'
import { useAuthStore } from '@/stores/auth.js'
import { API_BASE_URL, API_TIMEOUT, API_ENDPOINTS } from '@/constants/api'


const api = axios.create({
  baseURL: API_BASE_URL,    // ✅ Ahora desde constants
  timeout: API_TIMEOUT,      // ✅ Ahora desde constants
})


api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  
  return config
})


/**
 * Inicia sesión con email y contraseña
 @param {string} email 
 @param {string} password 
 @returns {Promise} - Respuesta del servidor
 * 
 * USO:
 *   try {
 *     await login(email, password)
 *     router.push('/home')
 *   } catch (error) {
 *     console.error('Login fallido')
 *   }
 */
export async function login(email, password) {
  // Hacer petición al backend
  const respuesta = await api.post(API_ENDPOINTS.AUTH.LOGIN, { 
    email, 
    password 
  })

  // Guardar token en localStorage
  localStorage.setItem('token', respuesta.data.access)

  // Guardar usuario en Pinia store
  const authStore = useAuthStore()
  authStore.guardarUsuario(respuesta.data.usuario)

  return respuesta.data
}


export function logout() {
  const authStore = useAuthStore()
  authStore.cerrarSesion()
}


export default api