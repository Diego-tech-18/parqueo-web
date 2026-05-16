
import { ref, computed } from 'vue'
import {getSecciones, crearSeccion, actualizarSeccion, eliminarSeccion, reactivarSeccion} from '@/api/espacios'
import { useNotificaciones } from './useNotificaciones'




export function useSecciones() {

  // ── Notificaciones ──
  const { mostrarExito, mostrarError } = useNotificaciones()

  // ── Estado ──
  const secciones = ref([])
  const cargando = ref(false)
  const errorCarga = ref('')
  const busqueda = ref('')

  // ── Computed: Secciones filtradas ──
  const seccionesFiltradas = computed(() => {
    if (!busqueda.value) return secciones.value

    const textoBusqueda = busqueda.value.toLowerCase()
    
    return secciones.value.filter(seccion => {
      const textoCompleto = `${seccion.nombre} ${seccion.tipo} ${seccion.descripcion || ''}`.toLowerCase()
      return textoCompleto.includes(textoBusqueda)
    })
  })

  // ── Computed: Estadísticas generales ──
  const totalSecciones = computed(() => secciones.value.length)
  
  const seccionesActivas = computed(() => 
    secciones.value.filter(s => s.activo).length
  )

  // FUNCIONES


  async function cargarSecciones() {
    cargando.value = true
    errorCarga.value = ''

    try {
      const respuesta = await getSecciones()
      secciones.value = respuesta.data
    } catch (error) {
      console.error('Error al cargar secciones:', error)
      errorCarga.value = 'No se pudo cargar las secciones. Verifica tu conexión.'
      secciones.value = []
    } finally {
      cargando.value = false
    }
  }

  
  async function crear(datosSeccion) {
    try {
      await crearSeccion(datosSeccion)
      await cargarSecciones() // Recargar la lista
      mostrarExito('Sección creada exitosamente')
      return true
    } catch (error) {
      // ── CASO ESPECIAL: 409 + seccion_id ──
      // El backend detectó una sección INACTIVA con el mismo nombre.
      // Ofrecemos reactivarla en lugar de crear una nueva.
      if (error.response?.status === 409 && error.response?.data?.seccion_id) {
        const { error: mensajeError, seccion_id } = error.response.data

        const quiereReactivar = confirm(
          `${mensajeError}\n\nPresiona OK para reactivar la sección existente, ` +
          `o Cancelar para usar otro nombre.`
        )

        if (quiereReactivar) {
          return await reactivar(seccion_id)
        }
        return false
      }

      // Errores reales sí se loggean
      console.error('Error al crear sección:', error)

      if (error.response?.status === 400) {
        mostrarError('Error en los datos enviados')
      } else {
        mostrarError('No se pudo crear la sección')
      }

      return false
    }
  }

  /**
   * Reactiva una sección que había sido soft-deleted.
   * Se llama automáticamente desde crear() cuando hay conflicto con
   * una sección inactiva del mismo nombre.
   */
  async function reactivar(id) {
    try {
      await reactivarSeccion(id)
      await cargarSecciones() // Recargar la lista
      mostrarExito('Sección reactivada exitosamente')
      return true
    } catch (error) {
      console.error('Error al reactivar sección:', error)
      mostrarError('No se pudo reactivar la sección')
      return false
    }
  }

  async function actualizar(id, datosSeccion) {
    try {
      await actualizarSeccion(id, datosSeccion)
      await cargarSecciones() // Recargar la lista
      mostrarExito('Sección actualizada exitosamente')
      return true
    } catch (error) {
      console.error('Error al actualizar sección:', error)
      mostrarError('No se pudo actualizar la sección')
      return false
    }
  }

  
  async function eliminar(id) {
    // Confirmar antes de eliminar
    if (!confirm('¿Estás seguro de eliminar esta sección? Solo se puede eliminar si no tiene espacios.')) {
      return false
    }

    try {
      await eliminarSeccion(id)
      await cargarSecciones() // Recargar la lista
      mostrarExito('Sección eliminada exitosamente')
      return true
    } catch (error) {
      console.error('Error al eliminar sección:', error)
      
      if (error.response?.status === 400) {
        mostrarError('No se puede eliminar una sección con espacios asignados')
      } else {
        mostrarError('No se pudo eliminar la sección')
      }
      
      return false
    }
  }

  /**
   * Busca una sección por ID
   * @param {number} id 
   * @returns {Object|null}
   */
  function buscarPorId(id) {
    return secciones.value.find(s => s.id === id) || null
  }

  /**
   * Limpia el filtro de búsqueda
   */
  function limpiarBusqueda() {
    busqueda.value = ''
  }


  // ── Retornar todo ──
  return {
    // Estado
    secciones,
    seccionesFiltradas,
    cargando,
    errorCarga,
    busqueda,
    totalSecciones,
    seccionesActivas,

    // Funciones
    cargarSecciones,
    crear,
    reactivar,
    actualizar,
    eliminar,
    buscarPorId,
    limpiarBusqueda,
  }
}