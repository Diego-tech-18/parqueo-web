import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {

  // ── Lee el usuario del localStorage al iniciar ──
  const usuarioGuardado = localStorage.getItem('usuario')
  const usuario = ref(
    usuarioGuardado ? JSON.parse(usuarioGuardado) : null
  )

  // ── Getters ──
  const estaLogueado    = computed(() => !!usuario.value && !!localStorage.getItem('token'))
  const esAdministrador = computed(() => usuario.value?.rol === 'Administrador')
  const esEmpleado      = computed(() => usuario.value?.rol === 'Empleado')
  const nombreUsuario   = computed(() =>
    usuario.value ? `${usuario.value.nombre} ${usuario.value.apellido}` : ''
  )

  // ── Guardar usuario después del login ──
  function guardarUsuario(datos) {
    usuario.value = datos
    localStorage.setItem('usuario', JSON.stringify(datos))
  }

  // ── Cerrar sesión ──
  function cerrarSesion() {
    usuario.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')   // ← AGREGADO: también limpiar el refresh
    localStorage.removeItem('usuario')
  }

  return {
    usuario,
    estaLogueado,
    esAdministrador,
    esEmpleado,
    nombreUsuario,
    guardarUsuario,
    cerrarSesion,
  }
})