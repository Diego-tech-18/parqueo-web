<template>
  <div class="notificaciones-contenedor">
    <transition-group name="notif">
      <div
        v-for="notif in notificaciones"
        :key="notif.id"
        :class="['notif', `notif-${notif.tipo}`]"
        @click="cerrarNotificacion(notif.id)"
      >
        <span class="notif-icono">
          {{ iconoPara(notif.tipo) }}
        </span>
        <span class="notif-mensaje">{{ notif.mensaje }}</span>
        <button class="notif-cerrar" @click.stop="cerrarNotificacion(notif.id)">
          ✕
        </button>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { useNotificaciones } from '@/composables/useNotificaciones'

const { notificaciones, cerrarNotificacion } = useNotificaciones()

function iconoPara(tipo) {
  const iconos = {
    success: '✓',
    error: '✕',
    warning: '⚠️',
    info: 'ℹ️',
  }
  return iconos[tipo] || 'ℹ️'
}
</script>

<style scoped>
.notificaciones-contenedor {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 380px;
}

.notif {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 10px;
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.18);
  cursor: pointer;
}

.notif-success { background: #16a34a; }
.notif-error   { background: #dc2626; }
.notif-warning { background: #d97706; }
.notif-info    { background: #2563eb; }

.notif-icono {
  font-size: 16px;
  flex-shrink: 0;
}

.notif-mensaje {
  flex: 1;
  line-height: 1.4;
}

.notif-cerrar {
  background: transparent;
  border: none;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  opacity: 0.8;
  flex-shrink: 0;
}

.notif-cerrar:hover {
  opacity: 1;
}

/* Animación de entrada/salida */
.notif-enter-active,
.notif-leave-active {
  transition: all 0.3s ease;
}

.notif-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.notif-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>