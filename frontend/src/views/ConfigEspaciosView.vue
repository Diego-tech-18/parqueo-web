<template>
  <div class="layout">


    <SidebarNav :abierto="sidebarAbierto" @toggle="sidebarAbierto = !sidebarAbierto" />


    <div class="main">

      <!-- ── Topbar ── -->
      <header class="topbar">
        <h1 class="topbar-titulo">Gestión de Espacios</h1>
        <div class="topbar-avatar">👤</div>
      </header>

      <!-- ── Cuerpo ── -->
      <section class="contenido">

        <!-- ── Pestañas ── -->
        <div class="tabs">
          <button 
            :class="['tab', { activo: tabActiva === 'secciones' }]"
            @click="tabActiva = 'secciones'"
          >
            📂 Secciones
          </button>
          <button 
            :class="['tab', { activo: tabActiva === 'espacios' }]"
            @click="tabActiva = 'espacios'"
          >
            🅿️ Espacios
          </button>
        </div>

        <!-- TAB: SECCIONES -->
       
        <div v-if="tabActiva === 'secciones'">

          <!-- Loading -->
          <div class="loading-wrapper" v-if="cargandoSecciones">
            <div class="spinner"></div>
            <p>Cargando secciones...</p>
          </div>

          <!-- Error -->
          <div class="error-wrapper" v-else-if="errorSecciones">
            <p>⚠️ {{ errorSecciones }}</p>
            <button class="btn-reintentar" @click="cargarSecciones">
              🔄 Reintentar
            </button>
          </div>

          <!-- Grid de secciones -->
          <div class="secciones-grid" v-else>
            
            <!-- Sin secciones -->
            <div v-if="secciones.length === 0" class="sin-datos">
              <h3>No hay secciones creadas</h3>
              <p>Haz click en el botón + para crear la primera sección</p>
            </div>

            <!-- Cards de secciones -->
            <!-- Cards de secciones -->
            <div 
              v-for="seccion in secciones" 
              :key="seccion.id"
              :class="['seccion-card-admin', 'clickable', seccion.tipo.toLowerCase()]"
              @click="verEspaciosSeccion(seccion.id)"
            >
              <div class="seccion-card-header">
                <div>
                  <h3 class="seccion-card-titulo">Sección {{ seccion.nombre }}</h3>
                  <p class="seccion-card-tipo">{{ seccion.tipo }}</p>
                </div>
                <div class="seccion-card-acciones">
                  <button 
                    class="btn-icon" 
                    @click.stop="abrirModalSeccion(seccion)"
                    title="Editar"
                  >
                    ✏️
                  </button>
                  <button 
                    class="btn-icon" 
                    @click.stop="eliminarSeccion(seccion.id)"
                    title="Eliminar"
                  >
                    🗑️
                  </button>
                </div>
              </div>

              <p v-if="seccion.descripcion" style="color: #64748b; font-size: 0.9rem; margin-bottom: 15px;">
                {{ seccion.descripcion }}
              </p>

              <div class="seccion-card-stats">
                <div class="stat-mini">
                  <div class="stat-mini-valor">{{ seccion.total_espacios }}</div>
                  <div class="stat-mini-label">Total</div>
                </div>
                <div class="stat-mini">
                  <div class="stat-mini-valor" style="color: #10b981;">{{ seccion.espacios_libres }}</div>
                  <div class="stat-mini-label">Libres</div>
                </div>
                <div class="stat-mini">
                  <div class="stat-mini-valor" style="color: #ef4444;">{{ seccion.espacios_ocupados }}</div>
                  <div class="stat-mini-label">Ocupados</div>
                </div>
              </div>

              <!-- Botón "Ver Espacios" -->
              <button class="btn-ver-espacios" @click.stop="verEspaciosSeccion(seccion.id)">
                Ver Espacios →
              </button>
            </div>

          </div>

          <!-- Botón flotante para crear sección -->
          <button class="btn-flotante" @click="abrirModalSeccion()" title="Crear sección">
            +
          </button>

        </div>

       
        <!-- TAB: ESPACIOS -->
      
        <div v-if="tabActiva === 'espacios'">

          <!-- Filtros -->
          <div class="filtros">
            <!-- Filtro por sección -->
            <div class="filtro-grupo">
              <label class="filtro-label">Sección:</label>
              <select v-model="filtroSeccion" class="filtro-select">
                <option :value="null">Todas las secciones</option>
                <option 
                  v-for="seccion in secciones" 
                  :key="seccion.id"
                  :value="seccion.id"
                >
                  Sección {{ seccion.nombre }}
                </option>
              </select>
            </div>

            <!-- Filtro por estado -->
            <div class="filtro-grupo">
              <label class="filtro-label">Estado:</label>
              <select v-model="filtroEstado" class="filtro-select">
                <option :value="null">Todos los estados</option>
                <option value="LIBRE">Libre</option>
                <option value="OCUPADO">Ocupado</option>
                <option value="FUERA_SERVICIO">Fuera de Servicio</option>
              </select>
            </div>

            <!-- Buscador -->
            <div class="filtro-grupo" style="flex: 1;">
              <label class="filtro-label">Buscar:</label>
              <input 
                v-model="busqueda" 
                placeholder="Buscar por número..."
                class="filtro-select"
                style="width: 100%;"
              />
            </div>
          </div>

          <!-- Loading -->
          <div class="loading-wrapper" v-if="cargando">
            <div class="spinner"></div>
            <p>Cargando espacios...</p>
          </div>

          <!-- Error -->
          <div class="error-wrapper" v-else-if="errorCarga">
            <p>⚠️ {{ errorCarga }}</p>
            <button class="btn-reintentar" @click="cargarEspacios">
              🔄 Reintentar
            </button>
          </div>

          <!-- Tabla de espacios -->
          <div class="tabla-wrapper" v-else>
            <table>
              <thead>
                <tr>
                  <th>N°</th>
                  <th>Número</th>
                  <th>Sección</th>
                  <th>Estado</th>
                  <th>Posición</th>
                  <th>Activo</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                <!-- Sin resultados -->
                <tr v-if="espaciosFiltrados.length === 0">
                  <td colspan="7" class="vacio">
                    {{ busqueda || filtroSeccion || filtroEstado 
                      ? 'No se encontraron espacios con esos filtros' 
                      : 'No hay espacios registrados' }}
                  </td>
                </tr>

                <!-- Lista de espacios -->
                <tr v-for="(espacio, index) in espaciosFiltrados" :key="espacio.id">
                  <td>{{ index + 1 }}</td>
                  <td><strong>{{ espacio.numero }}</strong></td>
                  <td>{{ espacio.seccion_nombre }}</td>
                  <td>
                    <span :class="['badge-estado', espacio.estado.toLowerCase().replace('_', '-')]">
                      {{ formatearEstado(espacio.estado) }}
                    </span>
                  </td>
                  <td>F{{ espacio.posicion_fila }}, C{{ espacio.posicion_columna }}</td>
                  <td>{{ espacio.activo ? '✅' : '❌' }}</td>
                  <td class="acciones-td">
                    <button 
                      class="btn-editar" 
                      @click="abrirModalEspacio(espacio)" 
                      title="Editar"
                    >
                      ✏️
                    </button>
                    <button 
                      class="btn-eliminar" 
                      @click="eliminarEspacio(espacio.id)" 
                      title="Eliminar"
                    >
                      🗑️
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Botón flotante para crear espacio -->
          <button class="btn-flotante" @click="abrirModalEspacio()" title="Crear espacio">
            +
          </button>

        </div>

      </section>
    </div>

  
    <!-- MODALES -->

    <!-- Modal de Sección -->
    <SeccionForm
      v-if="modalSeccionAbierto"
      :seccionEditar="seccionSeleccionada"
      @cerrar="cerrarModalSeccion"
      @guardado="handleGuardadoSeccion"
    />

    <!-- Modal de Espacio -->
    <EspacioForm
      v-if="modalEspacioAbierto"
      :espacioEditar="espacioSeleccionado"
      @cerrar="cerrarModalEspacio"
      @guardado="handleGuardadoEspacio"
    />

  </div>
</template>

<script setup>
import '@/assets/css/usuarios.css'
import '@/assets/css/espacios.css'
import '@/assets/css/mapa.css'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router' 
import SidebarNav from '@/components/SidebarNav.vue'
import SeccionForm from '@/components/forms/SeccionForm.vue'
import EspacioForm from '@/components/forms/EspacioForm.vue'

// Composables
import { useSecciones } from '@/composables/useSecciones'
import { useEspacios } from '@/composables/useEspacios'
import { useModal } from '@/composables/useModal'

// ESTADO

const sidebarAbierto = ref(false)
const tabActiva = ref('secciones')
const router = useRouter()  
// ── Secciones ──
const {
  secciones,
  cargando: cargandoSecciones,
  errorCarga: errorSecciones,
  cargarSecciones,
  eliminar: eliminarSeccionComposable,
} = useSecciones()

// ── Espacios ──
const {
  espaciosFiltrados,
  cargando,
  errorCarga,
  busqueda,
  filtroSeccion,
  filtroEstado,
  cargarEspacios,
  eliminar: eliminarEspacioComposable,
} = useEspacios()

// ── Modales Sección ──
const {
  modalAbierto: modalSeccionAbierto,
  datosModal: seccionSeleccionada,
  abrirModal: abrirModalSeccionBase,
  cerrarModal: cerrarModalSeccion,
} = useModal()

// ── Modales Espacio ──
const {
  modalAbierto: modalEspacioAbierto,
  datosModal: espacioSeleccionado,
  abrirModal: abrirModalEspacioBase,
  cerrarModal: cerrarModalEspacio,
} = useModal()


// FUNCIONES - SECCIONES

function abrirModalSeccion(seccion = null) {
  abrirModalSeccionBase(seccion)
}

async function handleGuardadoSeccion() {
  await cargarSecciones()
  cerrarModalSeccion()
}

async function eliminarSeccion(id) {
  await eliminarSeccionComposable(id)
}




// FUNCIONES - ESPACIOS

function abrirModalEspacio(espacio = null) {
  abrirModalEspacioBase(espacio)
}

async function handleGuardadoEspacio() {
  await cargarEspacios()
  cerrarModalEspacio()
}

async function eliminarEspacio(id) {
  await eliminarEspacioComposable(id)
}

function formatearEstado(estado) {
  const estados = {
    'LIBRE': 'Libre',
    'OCUPADO': 'Ocupado',
    'FUERA_SERVICIO': 'Fuera de Servicio'
  }
  return estados[estado] || estado
}

function verEspaciosSeccion(seccionId) {
  router.push(`/config-espacios/seccion/${seccionId}`)
}



onMounted(() => {
  cargarSecciones()
  cargarEspacios()
})
</script>