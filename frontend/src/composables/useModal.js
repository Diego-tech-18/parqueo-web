
import { ref } from 'vue'


// ══════════════════════════════════════════════════════════════════════════
// COMPOSABLE
// ══════════════════════════════════════════════════════════════════════════

export function useModal() {

  // ── Estado del modal ──
  const modalAbierto = ref(false)
  const datosModal = ref(null)


  function abrirModal(datos = null) {
    datosModal.value = datos
    modalAbierto.value = true
  }

  /**
   * Cierra el modal y limpia los datos
   */
  function cerrarModal() {
    modalAbierto.value = false
    datosModal.value = null
  }

  /**
   * Alterna el estado del modal (abre si está cerrado, cierra si está abierto)
   */
  function toggleModal() {
    if (modalAbierto.value) {
      cerrarModal()
    } else {
      abrirModal()
    }
  }

  /**
   * Verifica si el modal está en modo edición
   * @returns {boolean}
   */
  function esEdicion() {
    return datosModal.value !== null
  }

  /**
   * Verifica si el modal está en modo creación
   * @returns {boolean}
   */
  function esCreacion() {
    return datosModal.value === null
  }

  // ── Retornar todo ──
  return {
    // Estado
    modalAbierto,
    datosModal,

    // Funciones
    abrirModal,
    cerrarModal,
    toggleModal,
    esEdicion,
    esCreacion,
  }
}