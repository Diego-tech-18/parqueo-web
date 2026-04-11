<template>
  <div class="layout">

    <SidebarNav :abierto="sidebarAbierto" @toggle="sidebarAbierto = !sidebarAbierto" />

    <div class="main">

      <!-- Topbar -->
      <header class="topbar">
        <h1 class="topbar-titulo">Cámaras</h1>
        <div class="topbar-acciones">
          <button class="btn-videos" @click="$router.push('/videos')">🎬 Videos</button>
          <button class="btn-modo" :class="{ activo: modoGrilla }"  @click="modoGrilla = true">⊞</button>
          <button class="btn-modo" :class="{ activo: !modoGrilla }" @click="modoGrilla = false">☰</button>
          <div class="topbar-avatar">{{ authStore.usuario?.nombre?.charAt(0) }}</div>
        </div>
      </header>

      <!-- Contenido -->
      <section class="contenido">

        <!-- Controles -->
        <div class="controles">
          <div class="estado-general">
            <span class="punto verde"></span>
            <span>{{ camarasActivas }} de {{ camaras.length }} cámaras activas</span>
          </div>
          <div class="controles-derecha">
            <button
              v-if="authStore.esAdministrador"
              class="btn-accion btn-escanear"
              @click="escanearRedFn"
              :disabled="escaneando"
            >
              {{ escaneando ? '🔍 Escaneando...' : '🔍 Escanear red' }}
            </button>
            <button
              v-if="authStore.esAdministrador"
              class="btn-accion btn-agregar-cam"
              @click="abrirModalAgregar"
            >
              + Agregar cámara
            </button>
            <button class="btn-accion detener-todo" @click="detenerTodas">
              <span>⏹</span> Detener todas
            </button>
          </div>
        </div>

        <!-- Loading -->
        <div class="loading-wrapper" v-if="cargando">
          <div class="spinner"></div>
          <p>Cargando cámaras...</p>
        </div>

        <!-- Grilla usando CamaraCard -->
        <div v-else :class="['camaras-grid', { lista: !modoGrilla }]">
          <CamaraCard
            v-for="camara in camaras"
            :key="camara.id"
            :camara="camara"
            :esAdministrador="authStore.esAdministrador"
            @expandir="abrirFullscreen"
            @toggleGrabar="toggleGrabar"
            @configurar="abrirConfig"
          />
        </div>

      </section>
    </div>

    <!-- Pantalla completa -->
    <CamaraFullscreen
      v-if="camaraFullscreen"
      :camara="camaraFullscreen"
      :esAdministrador="authStore.esAdministrador"
      @cerrar="camaraFullscreen = null"
      @toggleGrabar="toggleGrabar"
      @configurar="abrirConfig"
    />

    <!-- Modal configurar cámara -->
    <div class="modal-overlay" v-if="modalConfig && camaraSeleccionada" @click.self="modalConfig = false">
      <div class="modal-config">
        <div class="modal-header">
          <h2>⚙️ Configurar — {{ camaraSeleccionada.nombre }}</h2>
          <button class="btn-x" @click="modalConfig = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="campo-config">
            <label>Nombre</label>
            <input v-model="camaraSeleccionada.nombre" />
          </div>
          <div class="campo-config">
            <label>Ubicación</label>
            <input v-model="camaraSeleccionada.ubicacion" />
          </div>
          <div class="campo-config">
            <label>URL Stream (RTSP o nombre webcam)</label>
            <input
              v-model="camaraSeleccionada.url_rtsp"
              placeholder="rtsp://... o 1080P Web Camera"
            />
          </div>
          <div class="campo-config">
            <label>Estado</label>
            <select v-model="camaraSeleccionada.activa">
              <option :value="true">Activa</option>
              <option :value="false">Inactiva</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancelar" @click="modalConfig = false">Cancelar</button>
          <button class="btn-guardar" @click="guardarConfig">Guardar cambios</button>
        </div>
      </div>
    </div>

    <!-- Modal agregar cámara -->
    <div class="modal-overlay" v-if="modalAgregar" @click.self="modalAgregar = false">
      <div class="modal-config">
        <div class="modal-header">
          <h2>+ Agregar Cámara</h2>
          <button class="btn-x" @click="modalAgregar = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="campo-config">
            <label>Nombre</label>
            <input v-model="form.nombre" placeholder="Ej: Cámara 1" />
          </div>
          <div class="campo-config">
            <label>Ubicación</label>
            <input v-model="form.ubicacion" placeholder="Ej: Entrada principal" />
          </div>
          <div class="campo-config">
            <label>URL Stream (RTSP o nombre webcam)</label>
            <input
              v-model="form.url_rtsp"
              placeholder="rtsp://... o 1080P Web Camera"
            />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancelar" @click="modalAgregar = false">Cancelar</button>
          <button class="btn-guardar" @click="guardarCamara">Agregar</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import '@/assets/css/camaras.css'
import { ref, computed, onMounted } from 'vue'
import { useRouter }             from 'vue-router'
import SidebarNav                from '@/components/SidebarNav.vue'
import CamaraCard                from '@/components/camaras/CamaraCard.vue'
import CamaraFullscreen          from '@/components/camaras/CamaraFullscreen.vue'
import { useAuthStore }          from '@/stores/auth.js'
import {
  getCamaras,
  crearCamara,
  editarCamara,
  eliminarCamara,
  activarCamara,
  desactivarCamara,
  escanearRed,
} from '@/api/camaras.js'

const router             = useRouter()
const authStore          = useAuthStore()
const sidebarAbierto     = ref(false)
const modoGrilla         = ref(true)
const camaraFullscreen   = ref(null)
const modalConfig        = ref(false)
const modalAgregar       = ref(false)
const camaraSeleccionada = ref(null)
const cargando           = ref(false)
const escaneando         = ref(false)
const errorCarga         = ref('')
const camaras            = ref([])

const form = ref({
  nombre   : '',
  ubicacion: '',
  url_rtsp : '',
  activa   : false,
})

const camarasActivas = computed(() =>
  camaras.value.filter(c => c.activa).length
)

async function cargarCamaras() {
  cargando.value   = true
  errorCarga.value = ''
  try {
    const res     = await getCamaras()
    camaras.value = res.data
  } catch (e) {
    errorCarga.value = 'No se pudieron cargar las cámaras'
    camaras.value    = []
  } finally {
    cargando.value = false
  }
}

function abrirFullscreen(camara) {
  camaraFullscreen.value = camara
}

async function toggleGrabar(camara) {
  try {
    if (camara.activa) {
      await desactivarCamara(camara.id)
    } else {
      await activarCamara(camara.id)
    }
    await cargarCamaras()
  } catch (e) {
    console.error('Error al cambiar estado:', e)
  }
}

async function detenerTodas() {
  if (!confirm('¿Detener todas las cámaras?')) return
  try {
    const activas = camaras.value.filter(c => c.activa)
    for (const camara of activas) {
      await desactivarCamara(camara.id)
    }
    await cargarCamaras()
  } catch (e) {
    console.error('Error al detener cámaras:', e)
  }
}

function abrirConfig(camara) {
  camaraSeleccionada.value = { ...camara }
  modalConfig.value        = true
}

async function guardarConfig() {
  try {
    await editarCamara(camaraSeleccionada.value.id, camaraSeleccionada.value)
    await cargarCamaras()
    modalConfig.value = false
  } catch (e) {
    console.error('Error al guardar:', e)
  }
}

function abrirModalAgregar() {
  form.value         = { nombre: '', ubicacion: '', url_rtsp: '', activa: false }
  modalAgregar.value = true
}

async function guardarCamara() {
  try {
    await crearCamara(form.value)
    await cargarCamaras()
    modalAgregar.value = false
  } catch (e) {
    console.error('Error al crear cámara:', e)
  }
}

async function eliminarCamaraFn(id) {
  if (!confirm('¿Eliminar esta cámara?')) return
  try {
    await eliminarCamara(id)
    await cargarCamaras()
  } catch (e) {
    console.error('Error al eliminar:', e)
  }
}

async function escanearRedFn() {
  escaneando.value = true
  try {
    const res = await escanearRed()
    alert(`Se encontraron ${res.data.total} cámaras en la red`)
  } catch (e) {
    console.error('Error al escanear:', e)
  } finally {
    escaneando.value = false
  }
}

onMounted(() => cargarCamaras())
</script>