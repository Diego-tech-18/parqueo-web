/**
 * ════════════════════════════════════════════════════════════════════════
 * FUNCIONES DE FORMATEO - VORTEX
 * ════════════════════════════════════════════════════════════════════════
 * 
 * Funciones helper para formatear datos (fechas, monedas, textos, etc.)
 */

// ══════════════════════════════════════════════════════════════════════════
// FORMATEO DE MONEDA
// ══════════════════════════════════════════════════════════════════════════

/**
 * Formatea un número a moneda boliviana
 * @param {number} monto - Cantidad a formatear
 * @returns {string} - Ej: "Bs. 1,234.50"
 * 
 * USO:
 *   formatearMoneda(1234.5)  // "Bs. 1,234.50"
 */
export function formatearMoneda(monto) {
  if (monto === null || monto === undefined) return 'Bs. 0.00'
  
  const montoFormateado = Number(monto).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')
  return `Bs. ${montoFormateado}`
}


// ══════════════════════════════════════════════════════════════════════════
// FORMATEO DE FECHAS Y HORAS
// ══════════════════════════════════════════════════════════════════════════

/**
 * Formatea una fecha a formato legible en español
 * @param {string|Date} fecha - Fecha en formato ISO o objeto Date
 * @returns {string} - Ej: "15 de Marzo, 2024"
 * 
 * USO:
 *   formatearFecha('2024-03-15')  // "15 de Marzo, 2024"
 */
export function formatearFecha(fecha) {
  if (!fecha) return '-'
  
  const opciones = { year: 'numeric', month: 'long', day: 'numeric' }
  return new Date(fecha).toLocaleDateString('es-BO', opciones)
}

/**
 * Formatea una fecha a formato corto
 * @param {string|Date} fecha 
 * @returns {string} - Ej: "15/03/2024"
 */
export function formatearFechaCorta(fecha) {
  if (!fecha) return '-'
  
  const opciones = { year: 'numeric', month: '2-digit', day: '2-digit' }
  return new Date(fecha).toLocaleDateString('es-BO', opciones)
}

/**
 * Formatea una fecha/hora a solo hora
 * @param {string|Date} fecha 
 * @returns {string} - Ej: "14:30"
 */
export function formatearHora(fecha) {
  if (!fecha) return '-'
  
  return new Date(fecha).toLocaleTimeString('es-BO', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

/**
 * Formatea fecha y hora completa
 * @param {string|Date} fecha 
 * @returns {string} - Ej: "15/03/2024 14:30"
 */
export function formatearFechaHora(fecha) {
  if (!fecha) return '-'
  
  return `${formatearFechaCorta(fecha)} ${formatearHora(fecha)}`
}


// ══════════════════════════════════════════════════════════════════════════
// FORMATEO DE TEXTOS
// ══════════════════════════════════════════════════════════════════════════

/**
 * Capitaliza la primera letra de un texto
 * @param {string} texto 
 * @returns {string} - Ej: "hola mundo" -> "Hola mundo"
 */
export function capitalizar(texto) {
  if (!texto) return ''
  return texto.charAt(0).toUpperCase() + texto.slice(1).toLowerCase()
}

/**
 * Convierte texto a mayúsculas
 * @param {string} texto 
 * @returns {string}
 */
export function mayusculas(texto) {
  if (!texto) return ''
  return texto.toUpperCase()
}

/**
 * Trunca un texto largo y añade puntos suspensivos
 * @param {string} texto 
 * @param {number} max - Caracteres máximos
 * @returns {string} - Ej: "Texto muy largo..." 
 */
export function truncar(texto, max = 50) {
  if (!texto || texto.length <= max) return texto
  return texto.substring(0, max) + '...'
}


// ══════════════════════════════════════════════════════════════════════════
// FORMATEO DE TIEMPO RELATIVO
// ══════════════════════════════════════════════════════════════════════════

/**
 * Convierte una fecha a tiempo relativo
 * @param {string|Date} fecha 
 * @returns {string} - Ej: "hace 5 minutos", "hace 2 horas"
 */
export function tiempoRelativo(fecha) {
  if (!fecha) return '-'
  
  const ahora = new Date()
  const entonces = new Date(fecha)
  const diferencia = ahora - entonces // milisegundos
  
  const segundos = Math.floor(diferencia / 1000)
  const minutos = Math.floor(segundos / 60)
  const horas = Math.floor(minutos / 60)
  const dias = Math.floor(horas / 24)
  
  if (segundos < 60) return 'hace un momento'
  if (minutos < 60) return `hace ${minutos} minuto${minutos !== 1 ? 's' : ''}`
  if (horas < 24) return `hace ${horas} hora${horas !== 1 ? 's' : ''}`
  if (dias < 7) return `hace ${dias} día${dias !== 1 ? 's' : ''}`
  
  return formatearFechaCorta(fecha)
}



/**
 * Formatea una placa de vehículo
 * @param {string} placa 
 * @returns {string} - Ej: "ABC-123" o "1234-XYZ"
 */
export function formatearPlaca(placa) {
  if (!placa) return '-'
  return placa.toUpperCase().trim()
}

/**
 * Formatea un número de CI
 * @param {string} ci 
 * @returns {string}
 */
export function formatearCI(ci) {
  if (!ci) return '-'
  // Quita todo lo que no sea número
  return ci.replace(/\D/g, '')
}