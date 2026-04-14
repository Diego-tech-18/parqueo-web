<template>
  <div class="layout">


    <SidebarNav :abierto="sidebarAbierto" @toggle="sidebarAbierto = !sidebarAbierto" />

  
    <div class="main">

      <!-- ── Topbar ── -->
      <header class="topbar">
        <h1 class="topbar-titulo">Mapa de Estacionamientos</h1>
        <div class="topbar-avatar">👤</div>
      </header>

      <!-- ── Cuerpo ── -->
      <section class="contenido">

        <!-- ── Leyenda ── -->
        <div class="leyenda">
          <span class="leyenda-titulo">Estado de Espacios:</span>
          
          <div class="leyenda-item">
            <div class="leyenda-color libre"></div>
            <span class="leyenda-texto">Libre</span>
          </div>
          
          <div class="leyenda-item">
            <div class="leyenda-color ocupado"></div>
            <span class="leyenda-texto">Ocupado</span>
          </div>
          
          <div class="leyenda-item">
            <div class="leyenda-color fuera-servicio"></div>
            <span class="leyenda-texto">Fuera de Servicio</span>
          </div>
        </div>

        <!-- ── Estadísticas Generales ── -->
        <div class="estadisticas">
          <div class="stat-card">
            <div class="stat-label">Total Espacios</div>
            <div class="stat-valor">{{ totalEspacios }}</div>
          </div>
          
          <div class="stat-card libre">
            <div class="stat-label">Libres</div>
            <div class="stat-valor">{{ espaciosLibres }}</div>
            <div class="stat-porcentaje">
              {{ totalEspacios > 0 ? Math.round((espaciosLibres / totalEspacios) * 100) : 0 }}% disponible
            </div>
          </div>
          
          <div class="stat-card ocupado">
            <div class="stat-label">Ocupados</div>
            <div class="stat-valor">{{ espaciosOcupados }}</div>
            <div class="stat-porcentaje">{{ porcentajeOcupacion }}% ocupación</div>
          </div>
          
          <div class="stat-card fuera">
            <div class="stat-label">Fuera de Servicio</div>
            <div class="stat-valor">{{ espaciosFueraServicio }}</div>
          </div>
        </div>

        <!-- ── Estado: Cargando ── -->
        <div class="loading-wrapper" v-if="cargando">
          <div class="spinner"></div>
          <p>Cargando mapa del parqueo...</p>
        </div>

        <!-- ── Estado: Error ── -->
        <div class="error-wrapper" v-else-if="errorCarga">
          <p>⚠️ {{ errorCarga }}</p>
          <button class="btn-reintentar" @click="cargarMapa">
            🔄 Reintentar
          </button>
        </div>

        <!-- ── Sin datos ── -->
        <div class="sin-datos" v-else-if="mapaCompleto.length === 0">
          <h3>No hay secciones configuradas</h3>
          <p>El administrador debe crear las secciones y espacios del parqueo.</p>
        </div>

        <!-- ── Mapa de Secciones ── -->
        <div class="mapa-container" v-else>
          
          <!-- Cada sección -->
          <div 
            v-for="seccion in mapaCompleto" 
            :key="seccion.id"
            class="seccion-card"
          >
            <!-- Header de la sección -->
            <div class="seccion-header">
              <h2 class="seccion-nombre">Sección {{ seccion.nombre }}</h2>
              <p class="seccion-tipo">{{ seccion.tipo }}</p>
              <div class="seccion-stats">
                <span>Total: {{ seccion.total_espacios }}</span>
                <span>Libres: {{ seccion.espacios_libres }}</span>
                <span>Ocupados: {{ seccion.espacios_ocupados }}</span>
              </div>
            </div>

            <!-- Grid de espacios -->
            <div class="espacios-grid" v-if="seccion.espacios && seccion.espacios.length > 0">
              <div 
                v-for="espacio in seccion.espacios"
                :key="espacio.id"
                :class="['espacio-card', espacio.estado.toLowerCase().replace('_', '-')]"
                @click="abrirDetalleEspacio(espacio)"
              >
                <div class="espacio-numero">{{ espacio.numero }}</div>
                <div class="espacio-estado">{{ formatearEstado(espacio.estado) }}</div>
              </div>
            </div>

            <!-- Sin espacios -->
            <div v-else class="sin-datos">
              <p>No hay espacios en esta sección</p>
            </div>

          </div>

        </div>

      </section>
    </div>


    <div v-if="espacioSeleccionado" class="modal-overlay" @click.self="cerrarDetalle">
      <div class="modal-container" style="max-width: 500px;">
        
        <div class="modal-header">
          <h2>Espacio {{ espacioSeleccionado.numero }}</h2>
          <button class="btn-x" @click="cerrarDetalle">✕</button>
        </div>

        <div class="modal-body">
          <p><strong>Sección:</strong> {{ espacioSeleccionado.seccion_nombre }}</p>
          <p><strong>Estado:</strong> {{ formatearEstado(espacioSeleccionado.estado) }}</p>
          <p><strong>Tipo:</strong> {{ espacioSeleccionado.seccion_tipo }}</p>
          
          <div v-if="espacioSeleccionado.notas" style="margin-top: 15px;">
            <strong>Notas:</strong>
            <p style="color: #64748b;">{{ espacioSeleccionado.notas }}</p>
          </div>

          <!-- Botones para cambiar estado (solo si es admin) -->
          <div v-if="authStore.esAdministrador" style="margin-top: 20px;">
            <p style="margin-bottom: 10px;"><strong>Cambiar estado:</strong></p>
            <div style="display: flex; gap: 10px;">
              <button 
                @click="handleCambiarEstado('LIBRE')"
                :disabled="espacioSeleccionado.estado === 'LIBRE'"
                style="flex: 1; padding: 10px; background: #10b981; color: white; border: none; border-radius: 6px; cursor: pointer;"
              >
                Libre
              </button>
              <button 
                @click="handleCambiarEstado('OCUPADO')"
                :disabled="espacioSeleccionado.estado === 'OCUPADO'"
                style="flex: 1; padding: 10px; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer;"
              >
                Ocupado
              </button>
              <button 
                @click="handleCambiarEstado('FUERA_SERVICIO')"
                :disabled="espacioSeleccionado.estado === 'FUERA_SERVICIO'"
                style="flex: 1; padding: 10px; background: #64748b; color: white; border: none; border-radius: 6px; cursor: pointer;"
              >
                Fuera
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>


import '@/assets/css/mapa.css'
import '@/assets/css/forms.css' // Para el modal
import { ref, onMounted } from 'vue'
import SidebarNav from '@/components/SidebarNav.vue'
import { useEspacios } from '@/composables/useEspacios'
import { useAuthStore } from '@/stores/auth'


const sidebarAbierto = ref(false)
const authStore = useAuthStore()

// ── Composable de espacios ──
const {
  mapaCompleto,
  cargando,
  errorCarga,
  totalEspacios,
  espaciosLibres,
  espaciosOcupados,
  espaciosFueraServicio,
  porcentajeOcupacion,
  cargarMapa,
  cambiarEstado,
} = useEspacios()

// ── Modal de detalle ──
const espacioSeleccionado = ref(null)


function abrirDetalleEspacio(espacio) {
  espacioSeleccionado.value = espacio
}

/**
 * Cierra el modal de detalle
 */
function cerrarDetalle() {
  espacioSeleccionado.value = null
}

/**
 * Cambia el estado de un espacio
 */
async function handleCambiarEstado(nuevoEstado) {
  if (!espacioSeleccionado.value) return

  const exito = await cambiarEstado(espacioSeleccionado.value.id, nuevoEstado)
  
  if (exito) {
    // Actualizar el espacio seleccionado
    espacioSeleccionado.value.estado = nuevoEstado
    
    // Recargar el mapa para reflejar cambios
    await cargarMapa()
  }
}

/**
 * Formatea el estado para mostrar
 */
function formatearEstado(estado) {
  const estados = {
    'LIBRE': 'Libre',
    'OCUPADO': 'Ocupado',
    'FUERA_SERVICIO': 'Fuera de Servicio'
  }
  return estados[estado] || estado
}



onMounted(() => {
  cargarMapa()
})
</script>

