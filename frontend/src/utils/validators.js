/**
 * ════════════════════════════════════════════════════════════════════════
 * FUNCIONES DE VALIDACIÓN - VORTEX
 * ════════════════════════════════════════════════════════════════════════
 * 
 * Funciones para validar datos de formularios
 */

// ══════════════════════════════════════════════════════════════════════════
// VALIDACIONES DE CAMPOS BÁSICOS
// ══════════════════════════════════════════════════════════════════════════

/**
 * Valida que un campo no esté vacío
 * @param {any} valor 
 * @returns {boolean}
 */
export function esRequerido(valor) {
  if (valor === null || valor === undefined) return false
  if (typeof valor === 'string') return valor.trim().length > 0
  return true
}

/**
 * Valida formato de email
 * @param {string} email 
 * @returns {boolean}
 * 
 * USO:
 *   if (!validarEmail(email)) {
 *     error = 'Email inválido'
 *   }
 */
export function validarEmail(email) {
  if (!email) return false
  
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return regex.test(email)
}

/**
 * Valida longitud mínima de un texto
 * @param {string} texto 
 * @param {number} minimo - Caracteres mínimos
 * @returns {boolean}
 */
export function longitudMinima(texto, minimo = 1) {
  if (!texto) return false
  return texto.trim().length >= minimo
}

/**
 * Valida longitud máxima de un texto
 * @param {string} texto 
 * @param {number} maximo - Caracteres máximos
 * @returns {boolean}
 */
export function longitudMaxima(texto, maximo = 255) {
  if (!texto) return true
  return texto.trim().length <= maximo
}


// ══════════════════════════════════════════════════════════════════════════
// VALIDACIONES ESPECÍFICAS DE BOLIVIA
// ══════════════════════════════════════════════════════════════════════════

/**
 * Valida un número de CI boliviano
 * @param {string} ci 
 * @returns {boolean}
 * 
 * CI boliviano: entre 6 y 8 dígitos
 */
export function validarCI(ci) {
  if (!ci) return false
  
  // Quita espacios y caracteres no numéricos
  const ciLimpio = ci.replace(/\D/g, '')
  
  // CI debe tener entre 6 y 8 dígitos
  return ciLimpio.length >= 6 && ciLimpio.length <= 8
}

/**
 * Valida formato de placa vehicular boliviana
 * @param {string} placa 
 * @returns {boolean}
 * 
 * Formatos válidos:
 * - ABC-123 (3 letras, guión, 3 números)
 * - 1234-XYZ (4 números, guión, 3 letras)
 */
export function validarPlaca(placa) {
  if (!placa) return false
  
  const placaLimpia = placa.toUpperCase().trim()
  
  // Formato: ABC-123
  const formato1 = /^[A-Z]{3}-[0-9]{3}$/
  // Formato: 1234-XYZ
  const formato2 = /^[0-9]{4}-[A-Z]{3}$/
  
  return formato1.test(placaLimpia) || formato2.test(placaLimpia)
}

/**
 * Valida número de teléfono boliviano
 * @param {string} telefono 
 * @returns {boolean}
 * 
 * Formatos válidos: 8 dígitos (móvil) o 7 dígitos (fijo)
 */
export function validarTelefono(telefono) {
  if (!telefono) return false
  
  const telefonoLimpio = telefono.replace(/\D/g, '')
  
  // Móvil: 8 dígitos, Fijo: 7 dígitos
  return telefonoLimpio.length === 7 || telefonoLimpio.length === 8
}


// ══════════════════════════════════════════════════════════════════════════
// VALIDACIONES DE CONTRASEÑA
// ══════════════════════════════════════════════════════════════════════════

/**
 * Valida que una contraseña sea segura
 * @param {string} password 
 * @returns {Object} { valido: boolean, mensaje: string }
 * 
 * USO:
 *   const resultado = validarPassword(password)
 *   if (!resultado.valido) {
 *     alert(resultado.mensaje)
 *   }
 */
export function validarPassword(password) {
  if (!password) {
    return { valido: false, mensaje: 'La contraseña es requerida' }
  }
  
  if (password.length < 8) {
    return { 
      valido: false, 
      mensaje: 'La contraseña debe tener al menos 8 caracteres' 
    }
  }
  
  if (!/[A-Z]/.test(password)) {
    return { 
      valido: false, 
      mensaje: 'Debe tener al menos una mayúscula' 
    }
  }
  
  if (!/[a-z]/.test(password)) {
    return { 
      valido: false, 
      mensaje: 'Debe tener al menos una minúscula' 
    }
  }
  
  if (!/[0-9]/.test(password)) {
    return { 
      valido: false, 
      mensaje: 'Debe tener al menos un número' 
    }
  }
  
  return { valido: true, mensaje: 'Contraseña válida' }
}

/**
 * Valida que dos contraseñas coincidan
 * @param {string} password1 
 * @param {string} password2 
 * @returns {boolean}
 */
export function passwordsCoinciden(password1, password2) {
  return password1 === password2 && password1.length > 0
}


// ══════════════════════════════════════════════════════════════════════════
// VALIDACIONES DE NÚMEROS
// ══════════════════════════════════════════════════════════════════════════

/**
 * Valida que un valor sea un número positivo
 * @param {any} valor 
 * @returns {boolean}
 */
export function esNumeroPositivo(valor) {
  const numero = Number(valor)
  return !isNaN(numero) && numero > 0
}

/**
 * Valida que un número esté en un rango
 * @param {number} valor 
 * @param {number} min 
 * @param {number} max 
 * @returns {boolean}
 */
export function enRango(valor, min, max) {
  const numero = Number(valor)
  if (isNaN(numero)) return false
  return numero >= min && numero <= max
}