export const ROLES = {
  ADMINISTRADOR: 'Administrador',
  EMPLEADO: 'Empleado',

}



/**
 * Verifica si un usuario es Administrador
 * @param {Object} usuario - Objeto usuario con propiedad 'rol'
 * @returns {boolean}
 * 
 * USO:
 *   if (esAdministrador(usuario)) {
 *     // Mostrar opciones de admin
 *   }
 */
export function esAdministrador(usuario) {
  return usuario?.rol === ROLES.ADMINISTRADOR
}


 // Verifica si un usuario es Empleado
 
export function esEmpleado(usuario) {
  return usuario?.rol === ROLES.EMPLEADO
}



/**
 * Verifica si un usuario tiene uno de los roles permitidos
 * @param {Object} usuario 
 * @param {Array} rolesPermitidos - Array con roles permitidos
 * @returns {boolean}
 * 
 * USO:
 *   if (tieneRol(usuario, [ROLES.ADMINISTRADOR, ROLES.EMPLEADO])) {
 *     // Permitir acceso
 *   }
 */
export function tieneRol(usuario, rolesPermitidos = []) {
  if (!usuario?.rol) return false
  return rolesPermitidos.includes(usuario.rol)
}