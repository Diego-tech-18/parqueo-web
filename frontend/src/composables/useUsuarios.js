
import { ref, computed } from 'vue'
import { getUsuarios, crearUsuario, actualizarUsuario, eliminarUsuario } from '@/api/usuarios'
import { useNotificaciones } from './useNotificaciones'



export function useUsuarios() {

  // ── Notificaciones ──
  const { mostrarExito, mostrarError } = useNotificaciones()

  // ── Estado ──
  const usuarios = ref([])
  const cargando = ref(false)
  const errorCarga = ref('')
  const busqueda = ref('')

  
   // Filtra usuarios por nombre, apellido, email o CI
   
  const usuariosFiltrados = computed(() => {
    if (!busqueda.value) return usuarios.value

    const textoBusqueda = busqueda.value.toLowerCase()
    
    return usuarios.value.filter(usuario => {
      const textoCompleto = `${usuario.nombre} ${usuario.apellido} ${usuario.email} ${usuario.ci}`.toLowerCase()
      return textoCompleto.includes(textoBusqueda)
    })
  })


 
   // Carga todos los usuarios desde el backend
 
  
  async function cargarUsuarios() {
    cargando.value = true
    errorCarga.value = ''

    try {
      const respuesta = await getUsuarios()
      usuarios.value = respuesta.data
    } catch (error) {
      console.error('Error al cargar usuarios:', error)
      errorCarga.value = 'No se pudo conectar al servidor. Verifica tu conexión.'
      usuarios.value = []
    } finally {
      cargando.value = false
    }
  }

  async function crear(datosUsuario) {
    try {
      await crearUsuario(datosUsuario)
      await cargarUsuarios() // Recargar la lista
      mostrarExito('Usuario creado exitosamente')
      return true
    } catch (error) {
      console.error('Error al crear usuario:', error)
      
      // Manejar errores específicos del backend
      if (error.response?.status === 400) {
        mostrarError('Error en los datos enviados')
      } else if (error.response?.status === 409) {
        mostrarError('El email ya está registrado')
      } else {
        mostrarError('No se pudo crear el usuario')
      }
      
      return false
    }
  }

  
  async function actualizar(id, datosUsuario) {
    try {
      await actualizarUsuario(id, datosUsuario)
      await cargarUsuarios() // Recargar la lista
      mostrarExito('Usuario actualizado exitosamente')
      return true
    } catch (error) {
      console.error('Error al actualizar usuario:', error)
      mostrarError('No se pudo actualizar el usuario')
      return false
    }
  }

  
  async function eliminar(id) {
    // Confirmar antes de eliminar
    if (!confirm('¿Estás seguro de eliminar este usuario?')) {
      return false
    }

    try {
      await eliminarUsuario(id)
      await cargarUsuarios() // Recargar la lista
      mostrarExito('Usuario eliminado exitosamente')
      return true
    } catch (error) {
      console.error('Error al eliminar usuario:', error)
      mostrarError('No se pudo eliminar el usuario')
      return false
    }
  }

 
  function buscarPorId(id) {
    return usuarios.value.find(u => u.id === id) || null
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
    usuarios,
    usuariosFiltrados,
    cargando,
    errorCarga,
    busqueda,

    // Funciones
    cargarUsuarios,
    crear,
    actualizar,
    eliminar,
    buscarPorId,
    limpiarBusqueda,
  }
}