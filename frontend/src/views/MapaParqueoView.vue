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
            <div class="stat-valor">{{ estadisticasGenerales.total }}</div>
          </div>
          
          <div class="stat-card libre">
            <div class="stat-label">Libres</div>
            <div class="stat-valor">{{ estadisticasGenerales.libres }}</div>
            <div class="stat-porcentaje">
              {{ estadisticasGenerales.porcentajeLibre }}% disponible
            </div>
          </div>
          
          <div class="stat-card ocupado">
            <div class="stat-label">Ocupados</div>
            <div class="stat-valor">{{ estadisticasGenerales.ocupados }}</div>
            <div class="stat-porcentaje">{{ estadisticasGenerales.porcentajeOcupado }}% ocupación</div>
          </div>
          
          <div class="stat-card fuera">
            <div class="stat-label">Fuera de Servicio</div>
            <div class="stat-valor">{{ estadisticasGenerales.fueraServicio }}</div>
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
                @click="abrirDetalle(espacio)"
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

    <!-- ══════════════════════════════════════════════════════════════════ -->
    <!-- MODALES DINÁMICOS -->
    <!-- ══════════════════════════════════════════════════════════════════ -->
    <div v-if="espacioSeleccionado" class="modal-overlay" @click.self="cerrarDetalle">
      <div class="modal-container" style="max-width: 500px;">
        
        <!-- ══════════════════════════════════════════════════════════════ -->
        <!-- MODAL TIPO: INFO (Espacios asignados o admin) -->
        <!-- ══════════════════════════════════════════════════════════════ -->
        <div v-if="tipoModal === 'info'">
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

        <!-- ══════════════════════════════════════════════════════════════ -->
        <!-- MODAL TIPO: ENTRADA (Espacio libre rotativo) -->
        <!-- ══════════════════════════════════════════════════════════════ -->
        <div v-else-if="tipoModal === 'entrada'">
          <div class="modal-header">
            <h2>📥 Registrar Entrada</h2>
            <button class="btn-x" @click="cerrarDetalle">✕</button>
          </div>

          <div class="modal-body">
            <p style="margin-bottom: 15px;">
              <strong>Espacio:</strong> {{ espacioSeleccionado.numero }} 
              (Sección {{ espacioSeleccionado.seccion_nombre }})
            </p>

            <!-- Placa -->
            <div class="campo">
              <label>Placa del Vehículo <span class="req">*</span></label>
              <input 
                v-model="formEntrada.placa" 
                placeholder="Ej: ABC-123"
                maxlength="20"
                @input="formEntrada.placa = formEntrada.placa.toUpperCase()"
              />
            </div>

            <!-- Tipo de vehículo -->
            <div class="campo">
              <label>Tipo de Vehículo <span class="req">*</span></label>
              <select v-model="formEntrada.tipo_vehiculo">
                <option value="AUTO">Auto</option>
                <option value="MOTO">Moto</option>
                <option value="CAMIONETA">Camioneta</option>
              </select>
            </div>

            <!-- Notas opcionales -->
            <div class="campo">
              <label>Notas (Opcional)</label>
              <textarea 
                v-model="formEntrada.notas" 
                placeholder="Observaciones..."
                rows="2"
              ></textarea>
            </div>

            
            <!-- Botones del modal -->
            <div class="botones-modal-mapa">
              <button 
                class="btn-principal" 
                @click="registrarEntradaDesdeMap"
                :disabled="!formEntrada.placa || cargandoRegistro"
              >
                {{ cargandoRegistro ? 'Registrando...' : '📥 Registrar Entrada' }}
              </button>
              
              <button 
                class="btn-fuera-servicio" 
                @click="marcarFueraServicio"
                :disabled="cargandoRegistro"
              >
                🔧 Fuera de Servicio
              </button>
            </div>
          </div>
        </div>

        <!-- ══════════════════════════════════════════════════════════════ -->
        <!-- MODAL TIPO: SALIDA (Espacio ocupado rotativo) -->
        <!-- ══════════════════════════════════════════════════════════════ -->
        <div v-else-if="tipoModal === 'salida'">
          <div class="modal-header">
            <h2>📤 Registrar Salida</h2>
            <button class="btn-x" @click="cerrarDetalle">✕</button>
          </div>

          <div class="modal-body">
            
            <!-- Cargando registro -->
            <div v-if="cargandoRegistro" style="text-align: center; padding: 20px;">
              <div class="spinner"></div>
              <p>Buscando registro...</p>
            </div>

            <!-- Registro encontrado -->
            <div v-else-if="registroActual">
              <p style="margin-bottom: 15px;">
                <strong>Espacio:</strong> {{ espacioSeleccionado.numero }}
              </p>

              <div class="info-grid">
                <div class="info-item">
                  <span class="info-label">Placa:</span>
                  <span class="info-valor">{{ registroActual.placa }}</span>
                </div>

                <div class="info-item">
                  <span class="info-label">Tipo:</span>
                  <span class="info-valor">{{ registroActual.tipo_vehiculo }}</span>
                </div>

                <div class="info-item">
                  <span class="info-label">Entrada:</span>
                  <span class="info-valor">{{ formatearFecha(registroActual.fecha_entrada) }}</span>
                </div>

                <div class="info-item">
                  <span class="info-label">Tiempo:</span>
                  <span class="info-valor destacado">{{ registroActual.tiempo_transcurrido }}</span>
                </div>

                <div class="info-item" style="grid-column: 1 / -1;">
                  <span class="info-label">Tarifa Estimada:</span>
                  <span class="info-valor tarifa">Bs. {{ registroActual.tarifa_estimada }}</span>
                </div>
              </div>

              <!-- Notas de salida -->
              <div class="campo" style="margin-top: 20px;">
                <label>Notas de Salida (Opcional)</label>
                <textarea 
                  v-model="notasSalida" 
                  placeholder="Observaciones..."
                  rows="2"
                ></textarea>
              </div>

              <!-- Botón registrar salida -->
              <button 
                class="btn-salida" 
                @click="registrarSalidaDesdeMap"
                :disabled="cargandoRegistro"
                style="width: 100%; margin-top: 10px;"
              >
                {{ cargandoRegistro ? 'Registrando...' : '📤 Registrar Salida' }}
              </button>
            </div>

            <!-- No hay registro -->
            <div v-else>
              <p style="color: #ef4444; text-align: center; padding: 20px;">
                ⚠️ Este espacio está ocupado pero no tiene registro activo.
              </p>
              <p style="color: #64748b; text-align: center; font-size: 0.9rem;">
                Use el cambio de estado manual si es administrador.
              </p>
            </div>

          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>


import '@/assets/css/mapa.css'
import '@/assets/css/forms.css'
import '@/assets/css/registros.css' 
import { ref, onMounted, computed } from 'vue'
import SidebarNav from '@/components/SidebarNav.vue'
import { useEspacios } from '@/composables/useEspacios'
import { useAuthStore } from '@/stores/auth'
import { useRegistros } from '@/composables/useRegistros'
import { cambiarEstadoEspacio } from '@/api/espacios'



const sidebarAbierto = ref(false)
const authStore = useAuthStore()

// ── Composable de espacios ──
const {
  mapaCompleto,
  cargando,
  errorCarga,
  cargarMapa,
  cambiarEstado,
} = useEspacios()

const {
  registroActual,
  cargando: cargandoRegistro,
  entrada,
  buscarPorEspacioId,
  salida,
  limpiarRegistroActual,
} = useRegistros()

// ── Modal de detalle ──
const espacioSeleccionado = ref(null)

const tipoModal = ref('info') // 'info', 'entrada', 'salida'

// Formulario de entrada
const formEntrada = ref({
  placa: '',
  tipo_vehiculo: 'AUTO',
  notas: '',
})

// Notas de salida
const notasSalida = ref('')

// ── Computed: Estadísticas calculadas desde mapaCompleto ──
const estadisticasGenerales = computed(() => {
  let total = 0
  let libres = 0
  let ocupados = 0
  let fueraServicio = 0

  mapaCompleto.value.forEach(seccion => {
    if (seccion.espacios) {
      seccion.espacios.forEach(espacio => {
        total++
        if (espacio.estado === 'LIBRE') libres++
        if (espacio.estado === 'OCUPADO') ocupados++
        if (espacio.estado === 'FUERA_SERVICIO') fueraServicio++
      })
    }
  })

  const porcentajeLibre = total > 0 ? Math.round((libres / total) * 100) : 0
  const porcentajeOcupado = total > 0 ? Math.round((ocupados / total) * 100) : 0

  return {
    total,
    libres,
    ocupados,
    fueraServicio,
    porcentajeLibre,
    porcentajeOcupado
  }
})

function abrirDetalle(espacio) {
  espacioSeleccionado.value = espacio
  
  // Determinar tipo de modal según el espacio
  if (espacio.seccion_tipo === 'ROTATIVOS') {
    // Espacios rotativos
    if (espacio.estado === 'LIBRE') {
      tipoModal.value = 'entrada'
    } else if (espacio.estado === 'OCUPADO') {
      tipoModal.value = 'salida'
      // Buscar el registro activo
      buscarRegistroDelEspacio(espacio.id)
    } else if (espacio.estado === 'FUERA_SERVICIO') {
      // Fuera de servicio: mostrar info
      tipoModal.value = 'info'
    } else {
      // Cualquier otro estado: info
      tipoModal.value = 'info'
    }
  } else {
    // Espacios asignados: solo info y cambio estado
    tipoModal.value = 'info'
  }
}

/**
 * Busca el registro activo de un espacio
 */
async function buscarRegistroDelEspacio(espacioId) {
  const resultado = await buscarPorEspacioId(espacioId)
  
  if (resultado.exito) {
    registroActual.value = resultado.data
  }
}

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
    // Actualizar el espacio en mapaCompleto directamente (sin recargar)
    mapaCompleto.value.forEach(seccion => {
      if (seccion.espacios) {
        const espacio = seccion.espacios.find(e => e.id === espacioSeleccionado.value.id)
        if (espacio) {
          espacio.estado = nuevoEstado
        }
      }
    })
    
    // Cerrar el modal
    cerrarDetalle()
  }
}

/**
 * Registra entrada desde el mapa
 */
async function registrarEntradaDesdeMap() {
  if (!espacioSeleccionado.value) return
  
  const datos = {
    placa: formEntrada.value.placa,
    tipo_vehiculo: formEntrada.value.tipo_vehiculo,
    espacio: espacioSeleccionado.value.id,
    notas: formEntrada.value.notas,
  }
  
  const resultado = await entrada(datos)
  
  if (resultado.exito) {
    // Actualizar estado del espacio en el mapa
    mapaCompleto.value.forEach(seccion => {
      if (seccion.espacios) {
        const espacio = seccion.espacios.find(e => e.id === espacioSeleccionado.value.id)
        if (espacio) {
          espacio.estado = 'OCUPADO'
        }
      }
    })
    
    // Limpiar formulario y cerrar
    formEntrada.value = { placa: '', tipo_vehiculo: 'AUTO', notas: '' }
    cerrarDetalle()
    
    // Recargar mapa para actualizar estadísticas
    await cargarMapa()
  }
}

/**
 * Registra salida desde el mapa
 */
async function registrarSalidaDesdeMap() {
  if (!registroActual.value) return
  
  const resultado = await salida({
    registro_id: registroActual.value.id,
    notas: notasSalida.value,
  })
  
  if (resultado.exito) {
    // Actualizar estado del espacio en el mapa
    mapaCompleto.value.forEach(seccion => {
      if (seccion.espacios) {
        const espacio = seccion.espacios.find(e => e.id === espacioSeleccionado.value.id)
        if (espacio) {
          espacio.estado = 'LIBRE'
        }
      }
    })
    
    // Limpiar y cerrar
    notasSalida.value = ''
    limpiarRegistroActual()
    cerrarDetalle()
    
    // Recargar mapa para actualizar estadísticas
    await cargarMapa()
  }
}

//boton fuera de servicio

async function marcarFueraServicio() {
  if (!espacioSeleccionado.value) return
  
  const confirmado = confirm(
    `¿Marcar espacio ${espacioSeleccionado.value.numero} como FUERA DE SERVICIO?\n\n` +
    'El espacio quedará bloqueado para reparaciones/mantenimiento.'
  )
  
  if (!confirmado) return
  
  cargandoRegistro.value = true
  
  try {
    await cambiarEstadoEspacio(espacioSeleccionado.value.id, {
      estado: 'FUERA_SERVICIO',
      notas: 'Espacio en mantenimiento/reparación'
    })
    
    // Recargar mapa
    await cargarMapa()
    
    // Cerrar modal
    espacioSeleccionado.value = null
    
    // Limpiar formulario
    formEntrada.value = {
      placa: '',
      tipo_vehiculo: 'AUTO',
      notas: ''
    }
    
    alert('✅ Espacio marcado como FUERA DE SERVICIO')
    
  } catch (error) {
    console.error('Error completo:', error)
    alert('❌ Error al marcar espacio: ' + error.message)
  } finally {
    cargandoRegistro.value = false
  }
}
/**
 * Formatea fecha para mostrar
 */
function formatearFecha(fecha) {
  if (!fecha) return '-'
  const d = new Date(fecha)
  const dia = String(d.getDate()).padStart(2, '0')
  const mes = String(d.getMonth() + 1).padStart(2, '0')
  const año = d.getFullYear()
  const horas = String(d.getHours()).padStart(2, '0')
  const minutos = String(d.getMinutes()).padStart(2, '0')
  return `${dia}/${mes}/${año} ${horas}:${minutos}`
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

