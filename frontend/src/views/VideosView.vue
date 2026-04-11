<template>
  <div class="layout">

    <SidebarNav :abierto="sidebarAbierto" @toggle="sidebarAbierto = !sidebarAbierto" />

    <div class="main">

      <!-- Topbar -->
      <header class="topbar">
        <button class="btn-volver" @click="$router.push('/camaras')">← Volver</button>
        <h1 class="topbar-titulo">Videos</h1>
        <div class="topbar-avatar">{{ authStore.usuario?.nombre?.charAt(0) }}</div>
      </header>

      <!-- Contenido -->
      <section class="contenido">

        <!-- Selector de cámara -->
        <div class="selector-camara">
          <button
            v-for="camara in camaras"
            :key="camara.id"
            :class="['btn-camara', { activo: camaraActiva === camara.id }]"
            @click="seleccionarCamara(camara.id)"
          >
            📷 {{ camara.nombre }}
          </button>
        </div>

        <!-- Tabla de videos -->
        <div class="tabla-wrapper">
          <div class="tabla-header">
            <h2>{{ camaraActualNombre }}</h2>
            <span class="total-videos">{{ videosFiltrados.length }} videos</span>
          </div>

          <table>
            <thead>
              <tr>
                <th>N°</th>
                <th>Nombre</th>
                <th>Fecha Inicio</th>
                <th>Fecha Fin</th>
                <th>Duración</th>
                <th>Tamaño</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="videosFiltrados.length === 0">
                <td colspan="7" class="vacio">No hay videos grabados para esta cámara</td>
              </tr>
              <tr v-for="(video, i) in videosFiltrados" :key="video.id">
                <td>{{ i + 1 }}</td>
                <td class="nombre-video">🎬 {{ video.nombre }}</td>
                <td>{{ video.fechaInicio }}</td>
                <td>{{ video.fechaFin }}</td>
                <td>{{ video.duracion }}</td>
                <td>{{ video.tamanio }}</td>
                <td class="acciones-td">
                  <button class="btn-ver"       @click="verVideo(video)"       title="Ver">▶ VER</button>
                  <button class="btn-descargar" @click="descargarVideo(video)" title="Descargar">⬇</button>
                  <button
                    v-if="authStore.esAdministrador"
                    class="btn-eliminar-video"
                    @click="eliminarVideo(video.id)"
                    title="Eliminar"
                  >🗑️</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </section>
    </div>

    <!-- Reproductor desde components/forms -->
    <VideoPlayer
      v-if="modalVideo"
      :video="videoSeleccionado"
      @cerrar="modalVideo = false"
      @descargar="descargarVideo"
    />

  </div>
</template>

<script setup>
import '@/assets/css/videos.css'
import { ref, computed } from 'vue'
import SidebarNav from '@/components/SidebarNav.vue'
import VideoPlayer from '@/components/forms/VideoPlayer.vue'
import { useAuthStore } from '@/stores/auth.js'

const authStore      = useAuthStore()
const sidebarAbierto = ref(false)
const camaraActiva   = ref(1)
const modalVideo     = ref(false)
const videoSeleccionado = ref(null)

// ── Cámaras ──
const camaras = ref([
  { id: 1, nombre: 'Cámara 1' },
  { id: 2, nombre: 'Cámara 2' },
  { id: 3, nombre: 'Cámara 3' },
  { id: 4, nombre: 'Cámara 4' },
])

// ── Videos vacíos, se llenarán desde Django ──
const videos = ref([])

// ── Filtra videos por cámara activa ──
const videosFiltrados = computed(() =>
  videos.value.filter(v => v.camaraId === camaraActiva.value)
)

// ── Nombre de la cámara activa ──
const camaraActualNombre = computed(() =>
  camaras.value.find(c => c.id === camaraActiva.value)?.nombre || ''
)

function seleccionarCamara(id) {
  camaraActiva.value = id
}

function verVideo(video) {
  videoSeleccionado.value = video
  modalVideo.value        = true
}

function descargarVideo(video) {
  alert(`Descargando: ${video.nombre}`)
}

function eliminarVideo(id) {
  if (!confirm('¿Eliminar este video?')) return
  videos.value = videos.value.filter(v => v.id !== id)
}
</script>