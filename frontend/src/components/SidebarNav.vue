<template>
  <aside :class="['sidebar', { abierto: abierto }]">

    <!-- Header con botón ☰ -->
    <div class="sidebar-header">
      <button class="menu-btn" @click="$emit('toggle')">☰</button>
      <span class="sidebar-titulo" v-show="abierto">vortex</span>
    </div>

    <!-- Nav items -->
    <nav class="sidebar-nav">

      <!-- Todos los usuarios -->
      <router-link to="/home" class="nav-item" title="Inicio">
        <span class="icono">🏠</span>
        <span class="nav-texto" v-show="abierto">Inicio</span>
      </router-link>

        <!-- Mapa de Parqueo --> 
      <router-link to="/mapa" class="nav-item" title="Mapa de Parqueo">
        <span class="icono">🅿️</span>
        <span class="nav-texto" v-show="abierto">Mapa Parqueo</span>
      </router-link>

      <!-- Entradas y Salidas -->
      <router-link to="/entradas-salidas" class="nav-item" title="Entradas y Salidas">
        <span class="icono">🚗</span>
        <span class="nav-texto" v-show="abierto">Entradas/Salidas</span>
      </router-link>

  

      <router-link to="/camaras" class="nav-item" title="Cámaras">
        <span class="icono">📷</span>
        <span class="nav-texto" v-show="abierto">Cámaras</span>
      </router-link>

      <!-- Solo Administrador -->
      <router-link
        v-if="authStore.esAdministrador"
        to="/usuarios"
        class="nav-item"
        title="Usuarios"
      >
        <span class="icono">👥</span>
        <span class="nav-texto" v-show="abierto">Usuarios</span>
      </router-link>

      <router-link
        v-if="authStore.esAdministrador"
        to="/config-espacios"
        class="nav-item"
        title="Gestión de Espacios"
      >
        <span class="icono">⚙️</span>
        <span class="nav-texto" v-show="abierto">Config. Espacios</span>
      </router-link>

    </nav>

    <!-- Footer -->
    <div class="sidebar-footer">
      <div class="footer-info" v-show="abierto">
        <p class="footer-label">Usuario</p>
        <p class="footer-email">{{ authStore.nombreUsuario }}</p>
        <p class="footer-rol">{{ authStore.usuario?.rol }}</p>
      </div>
      <button
        class="btn-cerrar"
        @click="cerrarSesion"
        :title="abierto ? '' : 'Cerrar sesión'"
      >
        <span>🚪</span>
        <span class="nav-texto" v-show="abierto">Cerrar Sesión</span>
      </button>
    </div>

  </aside>
</template>

<script setup>
import '@/assets/css/sidebar.css'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'

defineProps({ abierto: Boolean })
defineEmits(['toggle'])

const router    = useRouter()
const authStore = useAuthStore()

function cerrarSesion() {
  authStore.cerrarSesion()
  router.push('/')
}
</script>