<template>
  <div class="layout">

   
    <SidebarNav :abierto="sidebarAbierto" @toggle="sidebarAbierto = !sidebarAbierto" />


    <div class="main">

      <!-- ── Topbar ── -->
      <header class="topbar">
        <h1 class="topbar-titulo">Usuarios</h1>
        <div class="topbar-avatar">👤</div>
      </header>

      <!-- ── Cuerpo ── -->
      <section class="contenido">

        <!-- ── Barra de acciones ── -->
        <div class="acciones">
          <!-- Buscador -->
          <div class="buscador">
            <span>🔍</span>
            <input 
              v-model="busqueda" 
              placeholder="Buscar usuario..." 
              @input="handleBusqueda"
            />
          </div>

          <!-- Botón agregar -->
          <button class="btn-agregar" @click="handleAgregar">
            + Agregar Usuario
          </button>
        </div>

        <!-- ── Estado: Cargando ── -->
        <div class="loading-wrapper" v-if="cargando">
          <div class="spinner"></div>
          <p>Cargando usuarios...</p>
        </div>

        <!-- ── Estado: Error ── -->
        <div class="error-wrapper" v-else-if="errorCarga">
          <p>⚠️ {{ errorCarga }}</p>
          <button class="btn-reintentar" @click="cargarUsuarios">
            🔄 Reintentar
          </button>
        </div>

        <!-- ── Tabla de usuarios ── -->
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
              <!-- Sin resultados -->
              <tr v-if="usuariosFiltrados.length === 0">
                <td colspan="8" class="vacio">
                  {{ busqueda ? 'No se encontraron usuarios' : 'No hay usuarios registrados' }}
                </td>
              </tr>

              <!-- Lista de usuarios -->
              <tr v-for="(usuario, index) in usuariosFiltrados" :key="usuario.id">
                <td>{{ index + 1 }}</td>
                <td>
                  <img 
                    v-if="usuario.foto" 
                    :src="usuario.foto" 
                    class="foto-tabla" 
                    alt="foto" 
                  />
                  <div v-else class="foto-tabla-placeholder">👤</div>
                </td>
                <td>{{ usuario.nombre }}</td>
                <td>{{ usuario.apellido }}</td>
                <td>{{ usuario.ci }}</td>
                <td>{{ usuario.email }}</td>
                <td>
                  <span :class="['badge', usuario.rol]">{{ usuario.rol }}</span>
                </td>
                <td class="acciones-td">
                  <button 
                    class="btn-editar" 
                    @click="handleEditar(usuario)" 
                    title="Editar"
                  >
                    ✏️
                  </button>
                  <button 
                    class="btn-eliminar" 
                    @click="handleEliminar(usuario.id)" 
                    title="Eliminar"
                  >
                    🗑️
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </section>
    </div>


    <UsuarioForm
      v-if="modalAbierto"
      :usuarioEditar="datosModal"
      @cerrar="handleCerrarModal"
      @guardado="handleGuardado"
    />

  </div>
</template>

<script setup>
import '@/assets/css/usuarios.css'
import { ref, onMounted } from 'vue'
import SidebarNav from '@/components/SidebarNav.vue'
import UsuarioForm from '@/components/forms/UsuarioForm.vue'

// ── Composables ──
import { useUsuarios } from '@/composables/useUsuarios'
import { useModal } from '@/composables/useModal'



// ── Estado local (UI) ──
const sidebarAbierto = ref(false)


//Toda la lógica de usuarios está encapsulada aquí
const {
  usuarios,
  usuariosFiltrados,
  cargando,
  errorCarga,
  busqueda,
  cargarUsuarios,
  eliminar,
} = useUsuarios()

// ── Composable: Control del modal ──
// ✅ Toda la lógica del modal está encapsulada aquí
const {
  modalAbierto,
  datosModal,
  abrirModal,
  cerrarModal,
} = useModal()



 
function handleAgregar() {
  abrirModal() // Sin datos = modo creación
}

/**
 * Abre el modal para editar un usuario existente
 */
function handleEditar(usuario) {
  abrirModal(usuario) // Con datos = modo edición
}

/**
 * Elimina un usuario
 */
async function handleEliminar(id) {
  const confirmado = confirm('¿Estás seguro de desactivar este usuario?')
  if (!confirmado) return
  
  await eliminar(id)
  await cargarUsuarios()  // ← AGREGAR ESTA LÍNEA (recargar lista)
}

/**
 * Cierra el modal
 */
function handleCerrarModal() {
  cerrarModal()
}


async function handleGuardado() {
  await cargarUsuarios()
  cerrarModal()
}


function handleBusqueda() {
 
}



onMounted(() => {
  cargarUsuarios()
})
</script>