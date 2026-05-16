// ════════════════════════════════════════════════════════════════════
// API: Autenticación + interceptor de refresh automático - VORTEX
// ════════════════════════════════════════════════════════════════════
//
// Este archivo configura la instancia global de Axios y maneja:
//   1. Inyectar el access token en cada request.
//   2. Detectar 401 (token expirado) y refrescar automáticamente.
//   3. Reintentar la petición original con el nuevo token.
//   4. Si el refresh también falla → cerrar sesión y mandar al login.
//
// Esto es transparente para el resto del frontend: composables y
// componentes nunca tienen que pensar en tokens expirados.

import axios from 'axios'
import { useAuthStore } from '@/stores/auth.js'
import { API_BASE_URL, API_TIMEOUT, API_ENDPOINTS } from '@/constants/api'


// ── Instancia principal usada por toda la app ───────────────────────
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
})


// ════════════════════════════════════════════════════════════════════
// INTERCEPTOR DE REQUEST: añade el token a cada petición
// ════════════════════════════════════════════════════════════════════

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})


// ════════════════════════════════════════════════════════════════════
// INTERCEPTOR DE RESPONSE: maneja 401 con refresh automático
// ════════════════════════════════════════════════════════════════════

// Estado para evitar múltiples refreshes simultáneos.
// Si llegan 5 peticiones al mismo tiempo y todas reciben 401, queremos
// hacer UN solo refresh y reintentar las 5 con el nuevo token.
let estaRefrescando = false
let colaDePeticiones = []  // peticiones que esperan al refresh

function procesarCola(error, nuevoToken = null) {
  colaDePeticiones.forEach(peticion => {
    if (error) {
      peticion.reject(error)
    } else {
      peticion.resolve(nuevoToken)
    }
  })
  colaDePeticiones = []
}

api.interceptors.response.use(
  // Caso éxito: dejar pasar la respuesta
  response => response,

  // Caso error: aquí está la magia
  async error => {
    const peticionOriginal = error.config

    // Si NO es 401, o ya intentamos refrescar esta petición, propagar el error
    if (error.response?.status !== 401 || peticionOriginal._reintentado) {
      return Promise.reject(error)
    }

    // El endpoint de refresh fallando con 401 = refresh token también murió
    if (peticionOriginal.url?.includes('/auth/refresh/')) {
      cerrarSesionYRedirigir()
      return Promise.reject(error)
    }

    // Si ya hay un refresh en curso, ponemos esta petición en cola
    if (estaRefrescando) {
      return new Promise((resolve, reject) => {
        colaDePeticiones.push({ resolve, reject })
      }).then(nuevoToken => {
        peticionOriginal.headers.Authorization = `Bearer ${nuevoToken}`
        return api(peticionOriginal)
      })
    }

    // Iniciamos el refresh
    peticionOriginal._reintentado = true
    estaRefrescando = true

    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) {
      // No hay refresh token → no podemos refrescar → al login
      estaRefrescando = false
      cerrarSesionYRedirigir()
      return Promise.reject(error)
    }

    try {
      // Pedimos un nuevo access token al backend
      const respuesta = await axios.post(
        `${API_BASE_URL}${API_ENDPOINTS.AUTH.REFRESH}`,
        { refresh: refreshToken }
      )

      const nuevoAccessToken = respuesta.data.access
      localStorage.setItem('token', nuevoAccessToken)

      // Soltar la cola de peticiones que esperaban
      procesarCola(null, nuevoAccessToken)

      // Reintentar la petición original con el nuevo token
      peticionOriginal.headers.Authorization = `Bearer ${nuevoAccessToken}`
      return api(peticionOriginal)

    } catch (errorRefresh) {
      // Si el refresh también falla → sesión muerta → al login
      procesarCola(errorRefresh)
      cerrarSesionYRedirigir()
      return Promise.reject(errorRefresh)
    } finally {
      estaRefrescando = false
    }
  }
)


// ════════════════════════════════════════════════════════════════════
// HELPER: cerrar sesión y redirigir al login
// ════════════════════════════════════════════════════════════════════

function cerrarSesionYRedirigir() {
  // Limpiar storage
  localStorage.removeItem('token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('usuario')

  // Redirigir solo si NO estamos ya en el login
  if (window.location.pathname !== '/') {
    window.location.href = '/'
  }
}


// ════════════════════════════════════════════════════════════════════
// LOGIN
// ════════════════════════════════════════════════════════════════════

/**
 * Inicia sesión con email y contraseña.
 * Guarda access + refresh tokens y los datos del usuario.
 */
export async function login(email, password) {
  const respuesta = await api.post(API_ENDPOINTS.AUTH.LOGIN, {
    email,
    password
  })

  // Guardar AMBOS tokens
  localStorage.setItem('token', respuesta.data.access)
  localStorage.setItem('refresh_token', respuesta.data.refresh)

  // Guardar usuario en Pinia store
  const authStore = useAuthStore()
  authStore.guardarUsuario(respuesta.data.usuario)

  return respuesta.data
}


// ════════════════════════════════════════════════════════════════════
// LOGOUT
// ════════════════════════════════════════════════════════════════════

export function logout() {
  const authStore = useAuthStore()
  authStore.cerrarSesion()
}


export default api