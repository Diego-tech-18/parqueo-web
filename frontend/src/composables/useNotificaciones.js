
import { ref } from 'vue'


// Array de notificaciones activas
const notificaciones = ref([])

// ID único para cada notificación
let notificacionId = 0


export function useNotificaciones() {

  /**
   * Muestra una notificación
   * @param {string} mensaje - Texto a mostrar
   * @param {string} tipo - 'success' | 'error' | 'warning' | 'info'
   * @param {number} duracion - Milisegundos (por defecto 3000)
   * 
   * USO:
   *   const { mostrarExito, mostrarError } = useNotificaciones()
   *   mostrarExito('Usuario creado correctamente')
   */
  function mostrarNotificacion(mensaje, tipo = 'info', duracion = 3000) {
    const id = ++notificacionId

    // Agregar notificación al array
    notificaciones.value.push({
      id,
      mensaje,
      tipo,
      visible: true
    })

    // Auto-cerrar después de la duración
    setTimeout(() => {
      cerrarNotificacion(id)
    }, duracion)
  }


  function cerrarNotificacion(id) {
    const index = notificaciones.value.findIndex(n => n.id === id)
    if (index !== -1) {
      notificaciones.value.splice(index, 1)
    }
  }

 
  function cerrarTodas() {
    notificaciones.value = []
  }

  
  function mostrarExito(mensaje, duracion) {
    mostrarNotificacion(mensaje, 'success', duracion)
  }

  /**
   * Muestra una notificación de error (rojo)
   */
  function mostrarError(mensaje, duracion) {
    mostrarNotificacion(mensaje, 'error', duracion)
  }

  /**
   * Muestra una notificación de advertencia (amarillo)
   */
  function mostrarAdvertencia(mensaje, duracion) {
    mostrarNotificacion(mensaje, 'warning', duracion)
  }

  /**
   * Muestra una notificación informativa (azul)
   */
  function mostrarInfo(mensaje, duracion) {
    mostrarNotificacion(mensaje, 'info', duracion)
  }

  // ── Retornar todo ──
  return {
    // Estado
    notificaciones,

    // Funciones genéricas
    mostrarNotificacion,
    cerrarNotificacion,
    cerrarTodas,

    // Atajos
    mostrarExito,
    mostrarError,
    mostrarAdvertencia,
    mostrarInfo,
  }
}