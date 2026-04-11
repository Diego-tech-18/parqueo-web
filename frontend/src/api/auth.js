import axios from 'axios'
import { useAuthStore } from '@/stores/auth.js'

// URL base de Django
const api = axios.create({
  baseURL: 'http://localhost:8000/api'
})

// ── Interceptor: agrega token en cada petición automáticamente ──
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ── Login ──
export async function login(email, password) {
  const res = await api.post('/auth/login/', { email, password })
  localStorage.setItem('token', res.data.access)
  // localStorage.setItem('usuario', JSON.stringify(res.data.usuario))
  //return res.data
   // Guarda datos del usuario (incluye rol) en Pinia y localStorage
  const authStore = useAuthStore()
  authStore.guardarUsuario(res.data.usuario)

  return res.data
}

// ── Logout ──
export function logout() {
  //antes
  //localStorage.removeItem('token')
  //localStorage.removeItem('usuario')
  //depues
  const authStore = useAuthStore()
  authStore.cerrarSesion()
  
}

// ── Export default para que otros archivos puedan importarlo ──
export default api  // ← esta línea es la que faltaba