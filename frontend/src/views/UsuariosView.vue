<template>
  <div class="layout">

       <SidebarNav :abierto="sidebarAbierto" @toggle="sidebarAbierto = !sidebarAbierto" />

    <!-- Contenido principal -->
    <div class="main">

      <!-- Topbar -->
      <header class="topbar">
     
        <h1 class="topbar-titulo">Usuarios</h1>
        <div class="topbar-avatar">👤</div>
      </header>

      <!-- Cuerpo -->
      <section class="contenido">

        <!-- Acciones -->
        <div class="acciones">
          <div class="buscador">
            <span>🔍</span>
            <input v-model="busqueda" placeholder="Buscar usuario..." />
          </div>
          <button class="btn-agregar" @click="abrirModal()">+ Agregar Usuario</button>
        </div>

        <!-- Loading -->
        <div class="loading-wrapper" v-if="cargando">
          <div class="spinner"></div>
          <p>Cargando usuarios...</p>
        </div>

        <!-- Error -->
        <div class="error-wrapper" v-else-if="errorCarga">
          <p>⚠️ {{ errorCarga }}</p>
          <button class="btn-reintentar" @click="cargarUsuarios">🔄 Reintentar</button>
        </div>

        <!-- Tabla -->
        <div class="tabla-wrapper" v-else>
          <table>
            <thead>
              <tr>
                <th>N°</th>
                <th>Foto</th>
                <th>Nombre</th>
                <th>Apellido</th>
                <th>CI</th>
                <th>Email</th>
                <th>Rol</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="usuariosFiltrados.length === 0">
                <td colspan="8" class="vacio">No hay usuarios registrados</td>
              </tr>
              <tr v-for="(u, i) in usuariosFiltrados" :key="u.id">
                <td>{{ i + 1 }}</td>
                <td>
                  <img v-if="u.foto" :src="u.foto" class="foto-tabla" alt="foto" />
                  <div v-else class="foto-tabla-placeholder">👤</div>
                </td>
                <td>{{ u.nombre }}</td>
                <td>{{ u.apellido }}</td>
                <td>{{ u.ci }}</td>
                <td>{{ u.email }}</td>
                <td><span :class="['badge', u.rol]">{{ u.rol }}</span></td>
                <td class="acciones-td">
                  <button class="btn-editar"   @click="abrirModal(u)"  title="Editar">✏️</button>
                  <button class="btn-eliminar" @click="eliminar(u.id)" title="Eliminar">🗑️</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </section>
    </div>

    <!-- Formulario como modal -->
    <UsuarioForm
      v-if="modalAbierto"
      :usuarioEditar="usuarioSeleccionado"
      @cerrar="cerrarModal"
      @guardado="cargarUsuarios"
    />

  </div>
</template>

<script setup>
import '@/assets/css/usuarios.css'
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import SidebarNav from '@/components/SidebarNav.vue'
import UsuarioForm from '@/components/forms/UsuarioForm.vue'
import { getUsuarios, eliminarUsuario } from '@/api/usuarios.js'
const cargando   = ref(false)
const errorCarga = ref('')

const router              = useRouter()
const sidebarAbierto      = ref(false)
const busqueda            = ref('')
const modalAbierto        = ref(false)
const usuarioSeleccionado = ref(null)
const usuarios            = ref([])

// ── Filtrar usuarios por búsqueda ──
const usuariosFiltrados = computed(() =>
  usuarios.value.filter(u =>
    `${u.nombre} ${u.apellido} ${u.email} ${u.ci}`
      .toLowerCase()
      .includes(busqueda.value.toLowerCase())
  )
)

// ── Cargar usuarios desde Django ──
async function cargarUsuarios() {
  cargando.value   = true
  errorCarga.value = ''
  try {
    const res = await getUsuarios()
    usuarios.value = res.data
  } catch (e) {
    errorCarga.value = 'No se pudo conectar al servidor. Verifica tu conexión.'
    usuarios.value   = []
  } finally {
    cargando.value = false
  }
}

// ── Abrir modal: null = crear, objeto = editar ──
function abrirModal(usuario = null) {
  usuarioSeleccionado.value = usuario
  modalAbierto.value = true
}

// ── Cerrar modal y limpiar selección ──
function cerrarModal() {
  modalAbierto.value = false
  usuarioSeleccionado.value = null
}

// ── Eliminar usuario ──
async function eliminar(id) {
  if (!confirm('¿Estás seguro de eliminar este usuario?')) return
  try {
    await eliminarUsuario(id)
    await cargarUsuarios()  // recarga la tabla
  } catch (e) {
    console.error('Error al eliminar:', e)
  }
}

// ── Cargar al entrar a la página ──
onMounted(() => cargarUsuarios())
</script>