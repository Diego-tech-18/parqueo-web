<template>
  <div class="layout">

    <SidebarNav :abierto="sidebarAbierto" @toggle="sidebarAbierto = !sidebarAbierto" />

 
    <div class="main">

      <!-- ── Topbar ── -->
      <header class="topbar">
        <h1 class="topbar-titulo">Entradas y Salidas</h1>
        <div class="topbar-avatar">👤</div>
      </header>

      <!-- ── Cuerpo ── -->
      <section class="contenido">

        <!-- ── Pestañas ── -->
        <div class="tabs">
          <button 
            :class="['tab', { activo: tabActiva === 'entrada' }]"
            @click="tabActiva = 'entrada'"
          >
            📥 Entrada
          </button>
          <button 
            :class="['tab', { activo: tabActiva === 'salida' }]"
            @click="tabActiva = 'salida'"
          >
            📤 Salida
          </button>
          <button 
            :class="['tab', { activo: tabActiva === 'historial' }]"
            @click="cambiarAHistorial"
          >
            📋 Historial
          </button>
        </div>

 
        <!-- TAB: ENTRADA -->

        <div v-if="tabActiva === 'entrada'" class="tab-content">
          
          <div class="formulario-entrada">
            
            <h3>Registrar Entrada</h3>

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

            <!-- Selección de espacio -->
            <div class="campo">
              <label>Espacio <span class="req">*</span></label>
              <select v-model="formEntrada.espacio">
                <option value="" disabled>Seleccionar espacio libre</option>
                <option 
                  v-for="espacio in espaciosLibres" 
                  :key="espacio.id"
                  :value="espacio.id"
                >
                  {{ espacio.numero }} - Sección {{ espacio.seccion_nombre }}
                </option>
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

            <!-- Botón -->
            <button 
              class="btn-principal" 
              @click="registrarEntrada"
              :disabled="cargando || !formEntrada.placa || !formEntrada.espacio"
            >
              {{ cargando ? 'Registrando...' : '📥 Registrar Entrada' }}
            </button>

          </div>

          <!-- Espacios disponibles -->
          <div class="espacios-disponibles">
            <h4>Espacios Rotativos Disponibles ({{ espaciosLibres.length }})</h4>
            <div class="espacios-grid-mini">
              <div 
                v-for="espacio in espaciosLibres" 
                :key="espacio.id"
                class="espacio-mini libre"
                @click="formEntrada.espacio = espacio.id"
              >
                {{ espacio.numero }}
              </div>
            </div>
            <p v-if="espaciosLibres.length === 0" class="sin-datos">
              No hay espacios rotativos disponibles
            </p>
          </div>

        </div>

        
        <!-- TAB: SALIDA -->

        <div v-if="tabActiva === 'salida'" class="tab-content">
          
          <div class="formulario-salida">
            
            <h3>Registrar Salida</h3>

            <!-- Buscar por placa -->
            <div class="campo">
              <label>Buscar por Placa <span class="req">*</span></label>
              <div class="input-con-boton">
                <input 
                  v-model="placaBuscar" 
                  placeholder="Ej: ABC-123"
                  maxlength="20"
                  @input="placaBuscar = placaBuscar.toUpperCase()"
                  @keyup.enter="buscar"
                />
                <button @click="buscar" :disabled="!placaBuscar || cargando">
                  🔍 Buscar
                </button>
              </div>
            </div>

            <!-- Error al buscar -->
            <p class="error-general" v-if="errorCarga">{{ errorCarga }}</p>

            <!-- Registro encontrado -->
            <div v-if="registroActual" class="info-salida">
              <h4>Vehículo Encontrado</h4>

              <div class="info-grid">
                <div class="info-item">
                  <span class="info-label">Placa:</span>
                  <span class="info-valor">{{ registroActual.placa }}</span>
                </div>

                <div class="info-item">
                  <span class="info-label">Espacio:</span>
                  <span class="info-valor">{{ registroActual.espacio_numero }}</span>
                </div>

                <div class="info-item">
                  <span class="info-label">Entrada:</span>
                  <span class="info-valor">{{ formatearFecha(registroActual.fecha_entrada) }}</span>
                </div>

                <div class="info-item">
                  <span class="info-label">Tiempo:</span>
                  <span class="info-valor destacado">{{ registroActual.tiempo_transcurrido }}</span>
                </div>

                <div class="info-item">
                  <span class="info-label">Tarifa Estimada:</span>
                  <span class="info-valor tarifa">Bs. {{ registroActual.tarifa_estimada }}</span>
                </div>

                <div class="info-item">
                  <span class="info-label">Horario:</span>
                  <span class="info-valor">{{ registroActual.horario_entrada }}</span>
                </div>
              </div>

              <!-- Notas de salida -->
              <div class="campo" style="margin-top: 20px;">
                <label>Notas de Salida (Opcional)</label>
                <textarea 
                  v-model="notasSalida" 
                  placeholder="Observaciones al salir..."
                  rows="2"
                ></textarea>
              </div>

              <!-- Botón registrar salida -->
              <button 
                class="btn-salida" 
                @click="registrarSalida"
                :disabled="cargando"
              >
                {{ cargando ? 'Registrando...' : '📤 Registrar Salida' }}
              </button>

            </div>

          </div>

        </div>

      
        <!-- TAB: HISTORIAL -->
   
        <div v-if="tabActiva === 'historial'" class="tab-content">

          <!-- Filtros -->
          <div class="filtros">
            
            <div class="filtro-grupo">
              <label class="filtro-label">Estado:</label>
              <select v-model="filtros.estado" class="filtro-select" @change="aplicarFiltros">
                <option :value="null">Todos</option>
                <option value="EN_CURSO">En Curso</option>
                <option value="FINALIZADO">Finalizados</option>
              </select>
            </div>

            <div class="filtro-grupo">
              <label class="filtro-label">Desde:</label>
              <input 
                type="date" 
                v-model="filtros.fecha_desde"
                class="filtro-select"
                @change="aplicarFiltros"
              />
            </div>

            <div class="filtro-grupo">
              <label class="filtro-label">Hasta:</label>
              <input 
                type="date" 
                v-model="filtros.fecha_hasta"
                class="filtro-select"
                @change="aplicarFiltros"
              />
            </div>

            <div class="filtro-grupo" style="flex: 1;">
              <label class="filtro-label">Buscar Placa:</label>
              <input 
                v-model="filtros.placa" 
                placeholder="ABC-123"
                class="filtro-select"
                @input="filtros.placa = filtros.placa.toUpperCase()"
                @keyup.enter="aplicarFiltros"
              />
            </div>

            <button @click="aplicarFiltros" class="btn-filtrar">🔍 Filtrar</button>
            <button @click="limpiar" class="btn-limpiar">🔄 Limpiar</button>

          </div>

          <!-- Loading -->
          <div class="loading-wrapper" v-if="cargando">
            <div class="spinner"></div>
            <p>Cargando registros...</p>
          </div>

          <!-- Tabla de historial -->
          <div class="tabla-wrapper" v-else>
            <table>
              <thead>
                <tr>
                  <th>Placa</th>
                  <th>Espacio</th>
                  <th>Entrada</th>
                  <th>Salida</th>
                  <th>Tiempo</th>
                  <th>Tarifa</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="registros.length === 0">
                  <td colspan="7" class="vacio">No hay registros</td>
                </tr>

                <tr v-for="registro in registros" :key="registro.id">
                  <td><strong>{{ registro.placa }}</strong></td>
                  <td>{{ registro.espacio_numero }}</td>
                  <td>{{ formatearFecha(registro.fecha_entrada) }}</td>
                  <td>{{ registro.fecha_salida ? formatearFecha(registro.fecha_salida) : '-' }}</td>
                  <td>{{ registro.tiempo_transcurrido }}</td>
                  <td>{{ registro.tarifa ? `Bs. ${registro.tarifa}` : '-' }}</td>
                  <td>
                    <span :class="['badge-estado', registro.estado.toLowerCase().replace('_', '-')]">
                      {{ registro.estado === 'EN_CURSO' ? 'En curso' : 'Finalizado' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

        </div>

      </section>
    </div>

  </div>
</template>

<script setup>



import '@/assets/css/usuarios.css'
import '@/assets/css/espacios.css'
import '@/assets/css/registros.css'
import { ref, computed, onMounted } from 'vue'
import SidebarNav from '@/components/SidebarNav.vue'
import { useRegistros } from '@/composables/useRegistros'
import { useEspacios } from '@/composables/useEspacios'


// ESTADO


const sidebarAbierto = ref(false)
const tabActiva = ref('entrada')

// ── Composables ──
const {
  registros,
  registroActual,
  cargando,
  errorCarga,
  filtros,
  entrada,
  buscarVehiculo,
  salida,
  cargarHistorial,
  aplicarFiltros: aplicarFiltrosComposable,
  limpiarFiltros,
  limpiarRegistroActual,
} = useRegistros()

const {
  espacios,
  cargarEspacios,
} = useEspacios()

// ── Formulario de entrada ──
const formEntrada = ref({
  placa: '',
  tipo_vehiculo: 'AUTO',
  espacio: '',
  notas: '',
})

// ── Búsqueda de salida ──
const placaBuscar = ref('')
const notasSalida = ref('')


// COMPUTED


const espaciosLibres = computed(() => {
  return espacios.value.filter(e => 
    e.estado === 'LIBRE' && 
    e.activo && 
    e.seccion_tipo === 'ROTATIVOS'
  )
})


// FUNCIONES - ENTRADA


async function registrarEntrada() {
  const resultado = await entrada(formEntrada.value)
  
  if (resultado.exito) {
    // Limpiar formulario
    formEntrada.value = {
      placa: '',
      tipo_vehiculo: 'AUTO',
      espacio: '',
      notas: '',
    }
    
    // Recargar espacios para actualizar disponibles
    await cargarEspacios()
  }
}


// FUNCIONES - SALIDA


async function buscar() {
  await buscarVehiculo(placaBuscar.value)
}

async function registrarSalida() {
  if (!registroActual.value) return

  const resultado = await salida({
    registro_id: registroActual.value.id,
    notas: notasSalida.value,
  })

  if (resultado.exito) {
    // Limpiar
    placaBuscar.value = ''
    notasSalida.value = ''
    limpiarRegistroActual()
    
    // Recargar espacios
    await cargarEspacios()
  }
}


// FUNCIONES - HISTORIAL


function cambiarAHistorial() {
  tabActiva.value = 'historial'
  cargarHistorial()
}

async function aplicarFiltros() {
  await aplicarFiltrosComposable(filtros.value)
}

async function limpiar() {
  await limpiarFiltros()
}


// UTILIDADES

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


// CICLO DE VIDA


onMounted(() => {
  cargarEspacios()
})
</script>