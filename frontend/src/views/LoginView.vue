<template>
  <div class="login-page">

    <!-- Lado izquierdo -->
    <div class="login-left">
      <div class="logo-box">
        <img src="@/assets/img/Logo.jpg" alt="Vortex" />
        <h2>vortex</h2>
      </div>
    </div>

    <!-- Lado derecho -->
    <div class="login-right">
      <h1>Bienvenido</h1>
      <p class="login-subtitulo">Ingresa tus credenciales para continuar</p>

      <div class="campo">
        <label>Email</label>
        <input
          v-model="email"
          type="email"
          placeholder="Ingresa tu Email"
          :disabled="cargando"
          @keyup.enter="iniciarSesion"
        />
      </div>

      <div class="campo">
        <label>
          Contraseña
          <span class="olvidaste">¿Has olvidado tu contraseña?</span>
        </label>
        <input
          v-model="password"
          type="password"
          placeholder="Ingresa tu contraseña"
          :disabled="cargando"
          @keyup.enter="iniciarSesion"
        />
      </div>

      <!-- Error -->
      <div class="error-box" v-if="error">
        <span>⚠️</span> {{ error }}
      </div>

      <!-- Botón con estados -->
      <button
        @click="iniciarSesion"
        :disabled="cargando"
        :class="{ 'btn-cargando': cargando }"
      >
        <span v-if="!cargando">Iniciar Sesión</span>
        <span v-else class="btn-spinner-wrapper">
          <span class="btn-spinner"></span>
          Verificando...
        </span>
      </button>

      <!-- Progreso de conexión -->
      <div class="progreso-wrapper" v-if="cargando">
        <div class="progreso-barra">
          <div class="progreso-fill" :style="{ width: progreso + '%' }"></div>
        </div>
        <p class="progreso-texto">{{ mensajeCarga }}</p>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '@/api/auth.js'
import '@/assets/css/login.css'

const email       = ref('')
const password    = ref('')
const error       = ref('')
const cargando    = ref(false)
const verPassword = ref(false)
const progreso    = ref(0)
const mensajeCarga = ref('')
const router      = useRouter()

// ── Mensajes de progreso ──
const mensajes = [
  'Conectando con el servidor...',
  'Verificando credenciales...',
  'Cargando tu perfil...',
  'Preparando el sistema...',
]

async function iniciarSesion() {
  // Validar campos
  if (!email.value || !password.value) {
    error.value = 'Por favor ingresa tu email y contraseña'
    return
  }

  error.value    = ''
  cargando.value = true
  progreso.value = 0

  // ── Simula progreso visual mientras espera ──
  let paso = 0
  const intervalo = setInterval(() => {
    if (paso < mensajes.length) {
      mensajeCarga.value = mensajes[paso]
      progreso.value     = (paso + 1) * 22
      paso++
    }
  }, 600)

  try {
    await login(email.value, password.value)

    // Completa la barra antes de redirigir
    progreso.value     = 100
    mensajeCarga.value = '¡Bienvenido! Redirigiendo...'

    setTimeout(() => {
      router.push('/usuarios')
    }, 400)

  } catch (e) {
    const status = e.response?.status
    if (status === 401) {
      error.value = 'Email o contraseña incorrectos'
    } else if (status === 403) {
      error.value = 'Tu cuenta está inactiva, contacta al administrador'
    } else {
      error.value = 'Error de conexión, verifica tu internet'
    }
  } finally {
    clearInterval(intervalo)
    cargando.value = false
    progreso.value = 0
  }
}
</script>