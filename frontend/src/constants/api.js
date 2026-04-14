
// URL BASE DEL API


export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export const API_TIMEOUT = 10000  // 10 segundos


// API (Organizados por módulo)


export const API_ENDPOINTS = {
  
  // Autenticación 
  AUTH: {
    LOGIN: '/auth/login/',
    LOGOUT: '/auth/logout/',
    REFRESH: '/auth/refresh/',
    ME: '/auth/me/',
  },

  //  Usuarios 
  USUARIOS: {
    LIST: '/usuarios/',
    CREATE: '/usuarios/',
    DETAIL: (id) => `/usuarios/${id}/`,
    UPDATE: (id) => `/usuarios/${id}/`,
    DELETE: (id) => `/usuarios/${id}/`,
  },

   // ── Espacios ──  
  ESPACIOS: {
    LIST: '/espacios/',
    CREATE: '/espacios/',
    DETAIL: (id) => `/espacios/${id}/`,
    UPDATE: (id) => `/espacios/${id}/`,
    DELETE: (id) => `/espacios/${id}/`,
    CAMBIAR_ESTADO: (id) => `/espacios/${id}/cambiar-estado/`,
  },

  // ── Mapa ── 
  MAPA: {
    COMPLETO: '/mapa/',
  },


}
