
import {
  esRequerido,
  validarEmail,
  validarCI,
  validarPlaca,
  validarTelefono,
  validarPassword,
  passwordsCoinciden,
  longitudMinima,
  longitudMaxima,
} from '@/utils/validators'


/**
 * Valida todos los campos del formulario de usuario
 * @param {Object} datos - Objeto con los datos del formulario
 * @returns {Object} { valido: boolean, errores: Object }
 * 
 * USO:
 *   const resultado = validarFormularioUsuario(formulario)
 *   if (!resultado.valido) {
 *     errores.value = resultado.errores
 *   }
 */
export function validarFormularioUsuario(datos) {
  const errores = {}

  // ── Validar nombre ──
  if (!esRequerido(datos.nombre)) {
    errores.nombre = 'El nombre es requerido'
  } else if (!longitudMinima(datos.nombre, 2)) {
    errores.nombre = 'El nombre debe tener al menos 2 caracteres'
  } else if (!longitudMaxima(datos.nombre, 50)) {
    errores.nombre = 'El nombre no puede exceder 50 caracteres'
  }

  // ── Validar apellido ──
  if (!esRequerido(datos.apellido)) {
    errores.apellido = 'El apellido es requerido'
  } else if (!longitudMinima(datos.apellido, 2)) {
    errores.apellido = 'El apellido debe tener al menos 2 caracteres'
  } else if (!longitudMaxima(datos.apellido, 50)) {
    errores.apellido = 'El apellido no puede exceder 50 caracteres'
  }

  // ── Validar CI ──
  if (!esRequerido(datos.ci)) {
    errores.ci = 'El CI es requerido'
  } else if (!validarCI(datos.ci)) {
    errores.ci = 'El CI debe tener entre 6 y 8 dígitos'
  }

  // ── Validar email ──
  if (!esRequerido(datos.email)) {
    errores.email = 'El email es requerido'
  } else if (!validarEmail(datos.email)) {
    errores.email = 'El formato del email es inválido'
  }

  // ── Validar teléfono (opcional) ──
  if (datos.telefono && !validarTelefono(datos.telefono)) {
    errores.telefono = 'El teléfono debe tener 7 u 8 dígitos'
  }

  // ── Validar rol ──
  if (!esRequerido(datos.rol)) {
    errores.rol = 'El rol es requerido'
  }

  // ── Validar contraseña (solo si es usuario nuevo o está cambiando) ──
  if (datos.password) {
    const resultadoPassword = validarPassword(datos.password)
    if (!resultadoPassword.valido) {
      errores.password = resultadoPassword.mensaje
    }

    // Validar confirmación de contraseña
    if (datos.confirmarPassword && !passwordsCoinciden(datos.password, datos.confirmarPassword)) {
      errores.confirmarPassword = 'Las contraseñas no coinciden'
    }
  }

  return {
    valido: Object.keys(errores).length === 0,
    errores
  }
}




















