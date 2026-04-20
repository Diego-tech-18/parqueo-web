import { ref, computed } from 'vue'
import { 
  registrarEntrada, 
  registrarSalida, 
  buscarPorPlaca,
  buscarPorEspacio,
  getHistorial 
} from '@/api/registros'
import { useNotificaciones } from './useNotificaciones'


export function useRegistros() {

  // ── Notificaciones ──
  const { mostrarExito, mostrarError } = useNotificaciones()

  // ── Estado ──
  const registros = ref([])
  const registroActual = ref(null)
  const cargando = ref(false)
  const errorCarga = ref('')

  // ── Filtros para historial ──
  const filtros = ref({
    estado: null,
    fecha_desde: null,
    fecha_hasta: null,
    placa: '',
  })


  // COMPUTED


  const registrosActivos = computed(() => 
    registros.value.filter(r => r.estado === 'EN_CURSO')
  )

  const registrosFinalizados = computed(() => 
    registros.value.filter(r => r.estado === 'FINALIZADO')
  )

  const totalRegistros = computed(() => registros.value.length)


  // FUNCIONES - ENTRADA


  /**
   * Registra entrada de vehículo
   */
  async function entrada(datos) {
    try {
      const respuesta = await registrarEntrada(datos)
      mostrarExito(`Entrada registrada: ${datos.placa}`)
      return { exito: true, data: respuesta.data }
    } catch (error) {
      console.error('Error al registrar entrada:', error)
      
      if (error.response?.data) {
        const errores = error.response.data
        
        if (errores.placa) {
          mostrarError(`Placa: ${errores.placa[0]}`)
        } else if (errores.espacio) {
          mostrarError(`Espacio: ${errores.espacio[0]}`)
        } else {
          mostrarError('Error al registrar entrada')
        }
      } else {
        mostrarError('No se pudo registrar la entrada')
      }
      
      return { exito: false, error }
    }
  }

 
  // FUNCIONES - SALIDA
 

  /**
   * Busca vehículo por placa (para salida)
   */
  async function buscarVehiculo(placa) {
    cargando.value = true
    errorCarga.value = ''
    registroActual.value = null

    try {
      const respuesta = await buscarPorPlaca(placa)
      registroActual.value = respuesta.data
      return { exito: true, data: respuesta.data }
    } catch (error) {
      console.error('Error al buscar vehículo:', error)
      
      if (error.response?.status === 404) {
        errorCarga.value = 'No se encontró un vehículo con esa placa'
      } else {
        errorCarga.value = 'Error al buscar el vehículo'
      }
      
      return { exito: false, error }
    } finally {
      cargando.value = false
    }
  }

  /**
   * Busca registro por espacio (para click en mapa)
   */
  async function buscarPorEspacioId(espacioId) {
    cargando.value = true
    errorCarga.value = ''

    try {
      const respuesta = await buscarPorEspacio(espacioId)
      return { exito: true, data: respuesta.data }
    } catch (error) {
      console.error('Error al buscar por espacio:', error)
      return { exito: false, error }
    } finally {
      cargando.value = false
    }
  }

  /**
   * Registra salida de vehículo
   */
  async function salida(datos) {
    try {
      const respuesta = await registrarSalida(datos)
      mostrarExito(`Salida registrada. Tarifa: Bs. ${respuesta.data.tarifa}`)
      registroActual.value = null
      return { exito: true, data: respuesta.data }
    } catch (error) {
      console.error('Error al registrar salida:', error)
      
      if (error.response?.status === 404) {
        mostrarError('No se encontró un registro activo')
      } else {
        mostrarError('Error al registrar la salida')
      }
      
      return { exito: false, error }
    }
  }

 
  // FUNCIONES - HISTORIAL
  

  /**
   * Carga historial de registros
   */
  async function cargarHistorial() {
    cargando.value = true
    errorCarga.value = ''

    try {
      const respuesta = await getHistorial(filtros.value)
      registros.value = respuesta.data
    } catch (error) {
      console.error('Error al cargar historial:', error)
      errorCarga.value = 'No se pudo cargar el historial'
      registros.value = []
    } finally {
      cargando.value = false
    }
  }

  /**
   * Aplica filtros y recarga historial
   */
  async function aplicarFiltros(nuevosFiltros) {
    filtros.value = { ...filtros.value, ...nuevosFiltros }
    await cargarHistorial()
  }

  /**
   * Limpia filtros
   */
  async function limpiarFiltros() {
    filtros.value = {
      estado: null,
      fecha_desde: null,
      fecha_hasta: null,
      placa: '',
    }
    await cargarHistorial()
  }

  // UTILIDADES

  /**
   * Limpia el registro actual
   */
  function limpiarRegistroActual() {
    registroActual.value = null
    errorCarga.value = ''
  }

  /**
   * Formatea tiempo transcurrido
   */
  function formatearTiempo(minutos) {
    const horas = Math.floor(minutos / 60)
    const mins = minutos % 60
    return `${horas}h ${mins}min`
  }

 
  // RETORNAR


  return {
    // Estado
    registros,
    registroActual,
    cargando,
    errorCarga,
    filtros,

    // Computed
    registrosActivos,
    registrosFinalizados,
    totalRegistros,

    // Funciones entrada
    entrada,

    // Funciones salida
    buscarVehiculo,
    buscarPorEspacioId,
    salida,

    // Funciones historial
    cargarHistorial,
    aplicarFiltros,
    limpiarFiltros,

    // Utilidades
    limpiarRegistroActual,
    formatearTiempo,
  }
}