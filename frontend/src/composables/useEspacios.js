import { ref, computed } from 'vue'
import { 
  getEspacios, 
  getMapaCompleto, 
  crearEspacio, 
  actualizarEspacio, 
  eliminarEspacio,
  cambiarEstadoEspacio,
  reactivarEspacio
} from '@/api/espacios'
import { useNotificaciones } from './useNotificaciones'
import { useDebounce } from './useDebounce'




export function useEspacios() {

  // ── Notificaciones ──
  const { mostrarExito, mostrarError } = useNotificaciones()

  const espacios = ref([])
  const mapaCompleto = ref([]) // Secciones con espacios anidados
  const cargando = ref(false)
  const errorCarga = ref('')

  // El usuario escribe en `busqueda`. El filtrado usa `busquedaDebounced`,
  // que se actualiza solo cuando el usuario deja de escribir 300ms.
  // Esto evita re-filtrar listas grandes en cada tecla.
  const busqueda = ref('')
  const busquedaDebounced = useDebounce(busqueda, 300)

  const filtroSeccion = ref(null) // null = todas las secciones
  const filtroEstado = ref(null)  // null = todos los estados

  // ── Computed: Espacios filtrados ──
  const espaciosFiltrados = computed(() => {
    let resultado = espacios.value

    // Filtrar por sección
    if (filtroSeccion.value) {
      resultado = resultado.filter(e => e.seccion === filtroSeccion.value)
    }

    // Filtrar por estado
    if (filtroEstado.value) {
      resultado = resultado.filter(e => e.estado === filtroEstado.value)
    }

    // Filtrar por búsqueda (usando el valor con debounce)
    if (busquedaDebounced.value) {
      const textoBusqueda = busquedaDebounced.value.toLowerCase()
      resultado = resultado.filter(espacio => {
        const textoCompleto = `${espacio.numero} ${espacio.seccion_nombre || ''}`.toLowerCase()
        return textoCompleto.includes(textoBusqueda)
      })
    }

    return resultado
  })

  // ── Computed: Estadísticas ──
  const totalEspacios = computed(() => espacios.value.length)
  
  const espaciosLibres = computed(() => 
    espacios.value.filter(e => e.estado === 'LIBRE' && e.activo).length
  )
  
  const espaciosOcupados = computed(() => 
    espacios.value.filter(e => e.estado === 'OCUPADO').length
  )
  
  const espaciosFueraServicio = computed(() => 
    espacios.value.filter(e => e.estado === 'FUERA_SERVICIO').length
  )

  const porcentajeOcupacion = computed(() => {
    if (totalEspacios.value === 0) return 0
    return Math.round((espaciosOcupados.value / totalEspacios.value) * 100)
  })

  // FUNCIONES
 

  async function cargarEspacios(seccionId = null) {
    cargando.value = true
    errorCarga.value = ''

    try {
      const respuesta = await getEspacios(seccionId)
      espacios.value = respuesta.data
    } catch (error) {
      console.error('Error al cargar espacios:', error)
      errorCarga.value = 'No se pudo cargar los espacios. Verifica tu conexión.'
      espacios.value = []
    } finally {
      cargando.value = false
    }
  }

  
 async function cargarMapa() {
  cargando.value = true
  errorCarga.value = ''

  try {
    const respuesta = await getMapaCompleto()
    
    // Ordenar espacios de cada sección por número
    mapaCompleto.value = respuesta.data.map(seccion => ({
      ...seccion,
      espacios: seccion.espacios ? seccion.espacios.sort((a, b) => {
        const numA = parseInt(a.numero.replace(/\D/g, '')) || 0
        const numB = parseInt(b.numero.replace(/\D/g, '')) || 0
        return numA - numB
      }) : []
    }))
    
  } catch (error) {
    console.error('Error al cargar mapa:', error)
    errorCarga.value = 'No se pudo cargar el mapa del parqueo.'
    mapaCompleto.value = []
  } finally {
    cargando.value = false
  }
}
 
  async function crear(datosEspacio) {
    try {
      await crearEspacio(datosEspacio)
      await cargarEspacios() // Recargar la lista
      mostrarExito('Espacio creado exitosamente')
      return true
    } catch (error) {
      // ── CASO ESPECIAL: 409 + espacio_id ──
      // El backend detectó un espacio INACTIVO con el mismo número.
      // Ofrecemos reactivarlo en lugar de crear uno nuevo.
      // (No es un error real, así que no lo loggeamos como error.)
      if (error.response?.status === 409 && error.response?.data?.espacio_id) {
        const { error: mensajeError, espacio_id } = error.response.data

        const quiereReactivar = confirm(
          `${mensajeError}\n\nPresiona OK para reactivar el espacio existente, ` +
          `o Cancelar para usar otro número.`
        )

        if (quiereReactivar) {
          return await reactivar(espacio_id)
        }
        return false
      }

      // Errores reales sí se loggean
      console.error('Error al crear espacio:', error)

      if (error.response?.status === 400) {
        const errores = error.response.data
        if (errores.numero) {
          mostrarError(errores.numero[0])
        } else {
          mostrarError('Error en los datos enviados')
        }
      } else {
        mostrarError('No se pudo crear el espacio')
      }

      return false
    }
  }

/**
 * Reactiva un espacio que había sido soft-deleted.
 * Se llama automáticamente desde crear() cuando hay conflicto con
 * un espacio inactivo del mismo número.
 */
async function reactivar(id) {
  try {
    await reactivarEspacio(id)
    await cargarEspacios() // Recargar la lista
    mostrarExito('Espacio reactivado exitosamente')
    return true
  } catch (error) {
    console.error('Error al reactivar espacio:', error)
    mostrarError('No se pudo reactivar el espacio')
    return false
  }
}


  async function actualizar(id, datosEspacio) {
    try {
      await actualizarEspacio(id, datosEspacio)
      await cargarEspacios() // Recargar la lista
      mostrarExito('Espacio actualizado exitosamente')
      return true
    } catch (error) {
      console.error('Error al actualizar espacio:', error)
      mostrarError('No se pudo actualizar el espacio')
      return false
    }
  }


  async function eliminar(id) {
    if (!confirm('¿Estás seguro de eliminar este espacio?')) {
      return false
    }

    try {
      await eliminarEspacio(id)
      await cargarEspacios() // Recargar la lista
      mostrarExito('Espacio eliminado exitosamente')
      return true
    } catch (error) {
      console.error('Error al eliminar espacio:', error)
      mostrarError('No se pudo eliminar el espacio')
      return false
    }
  }


  async function cambiarEstado(id, nuevoEstado, notas = '') {
  try {
    await cambiarEstadoEspacio(id, {
      estado: nuevoEstado,
      notas: notas
    })
    
    // Actualizar en el estado local sin recargar todo
    const espacio = espacios.value.find(e => e.id === id)
    if (espacio) {
      espacio.estado = nuevoEstado
      if (notas) espacio.notas = notas
    }
    
    // También actualizar en el mapa si está cargado
    mapaCompleto.value.forEach(seccion => {
      const espacioEnMapa = seccion.espacios?.find(e => e.id === id)
      if (espacioEnMapa) {
        espacioEnMapa.estado = nuevoEstado
        if (notas) espacioEnMapa.notas = notas
      }
    })
    
    mostrarExito('Estado actualizado')
    return true
  } catch (error) {
    console.error('Error al cambiar estado:', error)
    mostrarError('No se pudo cambiar el estado')
    return false
  }
}


  function buscarPorId(id) {
    return espacios.value.find(e => e.id === id) || null
  }


  function limpiarFiltros() {
    busqueda.value = ''
    filtroSeccion.value = null
    filtroEstado.value = null
  }


  // ── Retornar todo ──
  return {
    // Estado
    espacios,
    mapaCompleto,
    espaciosFiltrados,
    cargando,
    errorCarga,
    busqueda,
    filtroSeccion,
    filtroEstado,
    
    // Estadísticas
    totalEspacios,
    espaciosLibres,
    espaciosOcupados,
    espaciosFueraServicio,
    porcentajeOcupacion,

    // Funciones
    // Funciones
    cargarEspacios,
    cargarMapa,
    crear,
    reactivar,
    actualizar,
    eliminar,
    cambiarEstado,
    buscarPorId,
    limpiarFiltros,
  }
}