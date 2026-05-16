
// URL BASE DEL API


export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export const API_TIMEOUT = 30000// 10 segundos


// API (Organizados por módulo)


export const API_ENDPOINTS = {
  
  // ── Autenticación ──
  AUTH: {
    LOGIN: '/auth/login/',
    LOGOUT: '/auth/logout/',
    REFRESH: '/auth/refresh/',
    ME: '/auth/me/',
  },

  // ── Usuarios ──
  USUARIOS: {
    LIST: '/usuarios/',
    CREATE: '/usuarios/',
    DETAIL: (id) => `/usuarios/${id}/`,
    UPDATE: (id) => `/usuarios/${id}/`,
    DELETE: (id) => `/usuarios/${id}/`,
  },

  // ── Secciones ──  
  SECCIONES: {
    LIST: '/secciones/',
    CREATE: '/secciones/',
    DETAIL: (id) => `/secciones/${id}/`,
    UPDATE: (id) => `/secciones/${id}/`,
    DELETE: (id) => `/secciones/${id}/`,
    REACTIVAR: (id) => `/secciones/${id}/reactivar/`,
  },

  // ── Espacios ──
 ESPACIOS: {
  LIST: '/espacios/',
  CREATE: '/espacios/',
  DETAIL: (id) => `/espacios/${id}/`,
  UPDATE: (id) => `/espacios/${id}/`,
  DELETE: (id) => `/espacios/${id}/`,
  CAMBIAR_ESTADO: (id) => `/espacios/${id}/cambiar-estado/`,
  REACTIVAR: (id) => `/espacios/${id}/reactivar/`,
  },

  // ── Mapa ──
  MAPA: {
    COMPLETO: '/mapa/',
  },

  // ── Registros (Entradas/Salidas) ──
  REGISTROS: {
    ENTRADA: '/registros/entrada/',
    SALIDA: '/registros/salida/',
    BUSCAR: '/registros/buscar/',
    HISTORIAL: '/registros/historial/',
  },

  TARIFAS: {
  GET: '/tarifas/',
  UPDATE: '/tarifas/',
  },
}