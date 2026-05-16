<template>
  <div class="layout">
    <!-- Sidebar -->
    <SidebarNav :abierto="sidebarAbierto" @toggle="sidebarAbierto = !sidebarAbierto" />

    <!-- Contenedor principal -->
    <div class="main">
      <!-- Topbar -->
      <header class="topbar">
        <h1 class="topbar-titulo">Gestión de Espacios</h1>
        <div class="topbar-avatar">👤</div>
      </header>

      <!-- Contenido -->
      <section class="contenido">
        
        <!-- Breadcrumbs -->
        <nav class="breadcrumbs">
          <router-link to="/config-espacios" class="breadcrumb-item">
            ← Gestión de Espacios
          </router-link>
          <span class="breadcrumb-separator">/</span>
          <span class="breadcrumb-current">Sección {{ seccion?.nombre }}</span>
        </nav>

        <!-- Header de sección -->
        <div class="seccion-header-detail" v-if="seccion">
          <div class="seccion-info">
            <h2>📂 Sección {{ seccion.nombre }}</h2>
            <span class="seccion-tipo-badge">{{ seccion.tipo }}</span>
            <p v-if="seccion.descripcion" class="seccion-descripcion">{{ seccion.descripcion }}</p>
          </div>

          <!-- Estadísticas -->
          <div class="seccion-stats-row">
            <div class="stat-item">
              <div class="stat-numero">{{ seccion.total_espacios }}</div>
              <div class="stat-label">Total</div>
            </div>
            <div class="stat-item libre">
              <div class="stat-numero">{{ seccion.espacios_libres }}</div>
              <div class="stat-label">Libres</div>
            </div>
            <div class="stat-item ocupado">
              <div class="stat-numero">{{ seccion.espacios_ocupados }}</div>
              <div class="stat-label">Ocupados</div>
            </div>
            <div class="stat-item fuera">
              <div class="stat-numero">{{ espaciosFueraServicio }}</div>
              <div class="stat-label">Fuera Servicio</div>
            </div>
          </div>
        </div>

        <!-- Botón crear espacio -->
        <div class="acciones-seccion">
          <button class="btn-crear-espacio" @click="abrirModalCrear">
            + Crear Espacio en Sección {{ seccion?.nombre }}
          </button>
        </div>

        <!-- Loading -->
        <div class="loading-wrapper" v-if="cargando">
          <div class="spinner"></div>
          <p>Cargando espacios...</p>
        </div>

        <!-- Tabla de espacios -->
        <div class="tabla-wrapper" v-else>
          <table>
            <thead>
              <tr>
                <th>N°</th>
                <th>NÚMERO</th>
                <th>ESTADO</th>
                <th>POSICIÓN</th>
                <th>ACTIVO</th>
                <th>ACCIONES</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="espaciosFiltrados.length === 0">
                <td colspan="6" class="vacio">
                  No hay espacios en esta sección
                </td>
              </tr>

              <tr v-for="(espacio, index) in espaciosFiltrados" :key="espacio.id">
                <td>{{ index + 1 }}</td>
                <td><strong>{{ espacio.numero }}</strong></td>
                <td>
                  <span :class="['badge-estado', espacio.estado.toLowerCase().replace('_', '-')]">
                    {{ formatearEstado(espacio.estado) }}
                  </span>
                </td>
                <td>F{{ espacio.posicion_fila }}, C{{ espacio.posicion_columna }}</td>
                <td>
                  <span :class="['badge-activo', espacio.activo ? 'activo' : 'inactivo']">
                    {{ espacio.activo ? '✓ Activo' : '✗ Inactivo' }}
                  </span>
                </td>
                <td class="acciones-td">
                  <button class="btn-editar" @click="editarEspacio(espacio)" title="Editar">
                    ✏️
                  </button>
                  <button class="btn-eliminar" @click="eliminarEspacio(espacio.id)" title="Eliminar">
                    🗑️
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </section>
    </div>
    
    <!-- Modal único: crear o editar (decide por la prop espacioEditar) -->
    <EspacioForm
      v-if="modalAbierto"
      :espacioEditar="espacioEditar"
      :seccionPreseleccionada="seccion?.id"
      @cerrar="cerrarModal"
      @guardado="handleGuardadoEspacio"
    />
  </div>
</template>

<script setup>
import '@/assets/css/usuarios.css'
import '@/assets/css/mapa.css'
import '@/assets/css/espacios.css'
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SidebarNav from '@/components/SidebarNav.vue'
import EspacioForm from '@/components/forms/EspacioForm.vue'
import { getSeccion } from '@/api/espacios'
import { useEspacios } from '@/composables/useEspacios'
import { useModal } from '@/composables/useModal'


const route = useRoute()
const router = useRouter()
const sidebarAbierto = ref(false)
const cargando = ref(true)
const seccion = ref(null)

// Composable que maneja toda la lógica de espacios (incluye eliminar con soft delete)
const {
  espacios,
  cargarEspacios,
  eliminar: eliminarEspacioComposable,
} = useEspacios()

// Computed 
const espaciosFiltrados = computed(() => {
  // Ordenar por número (A1, A2, A3... A10, A11)
  return espacios.value.sort((a, b) => {
    // Extraer número del string (ej: "A1" -> 1, "A10" -> 10)
    const numA = parseInt(a.numero.replace(/\D/g, '')) || 0
    const numB = parseInt(b.numero.replace(/\D/g, '')) || 0
    return numA - numB
  })
})
// ── Modal de espacio ── ← AGREGAR TODO ESTO
// ── Modal único: sirve para crear y editar ──
const {
  modalAbierto,
  datosModal: espacioEditar,  // si es null → modo crear; si tiene datos → modo editar
  abrirModal,
  cerrarModal,
} = useModal()

const espaciosFueraServicio = computed(() => {
  return espaciosFiltrados.value.filter(e => e.estado === 'FUERA_SERVICIO').length
})

// Funciones
async function cargarDatos() {
  try {
    cargando.value = true
    const seccionId = route.params.id

    // Cargar la sección (datos individuales) y sus espacios en paralelo
    const [respuestaSeccion] = await Promise.all([
      getSeccion(seccionId),
      cargarEspacios(seccionId),  // composable se encarga de espacios
    ])

    seccion.value = respuestaSeccion.data
  } catch (error) {
    console.error('Error al cargar datos de la sección:', error)
  } finally {
    cargando.value = false
  }
}

function formatearEstado(estado) {
  const estados = {
    'LIBRE': 'Libre',
    'OCUPADO': 'Ocupado',
    'FUERA_SERVICIO': 'Fuera de Servicio'
  }
  return estados[estado] || estado
}

function abrirModalCrear() {
  // Abrir modal sin datos = modo crear
  abrirModal(null)
}

function editarEspacio(espacio) {
  // Abrir modal con datos = modo editar
  abrirModal(espacio)
}

async function eliminarEspacio(id) {
  // El composable maneja confirmación, llamada al API y notificaciones
  const exito = await eliminarEspacioComposable(id)
  if (exito) {
    await cargarDatos()  // refrescar
  }
}

async function handleGuardadoEspacio() {
  await cargarDatos()
  cerrarModal()
}

onMounted(() => {
  cargarDatos()
})
</script>

