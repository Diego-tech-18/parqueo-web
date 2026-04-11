<template>
  <div class="modal-overlay" @click.self="$emit('cerrar')">
    <div class="modal-video">

      <div class="modal-header">
        <h2>▶ {{ video?.nombre }}</h2>
        <button class="btn-x" @click="$emit('cerrar')">✕</button>
      </div>

      <div class="video-player">
        <div class="video-placeholder">
          <span>🎬</span>
          <p>Reproductor de video</p>
          <p class="video-info">{{ video?.fechaInicio }} · {{ video?.duracion }}</p>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-cancelar" @click="$emit('cerrar')">Cerrar</button>
        <button class="btn-guardar" @click="$emit('descargar', video)">⬇ Descargar</button>
      </div>

    </div>
  </div>
</template>

<script setup>
import '@/assets/css/videos.css'

defineProps({
  video: {
    type: Object,
    default: null
  }
})

defineEmits(['cerrar', 'descargar'])
</script>