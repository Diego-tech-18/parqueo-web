import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'

const routes = [
  { path: '/', component: LoginView },
  { path: '/home',     component: () => import('@/views/HomeView.vue'),     meta: { requiresAuth: true } },
  { path: '/usuarios', component: () => import('@/views/UsuariosView.vue'), meta: { requiresAuth: true, soloAdmin: true } },
  { path: '/camaras', component: () => import('@/views/CamarasView.vue'),   meta: { requiresAuth: true } },
  { path: '/videos', component: () => import('@/views/VideosView.vue'),     meta: { requiresAuth: true }},
  { path: '/mapa',     component: () => import('@/views/MapaParqueoView.vue'), meta: { requiresAuth: true } },
  { path: '/config-espacios', component: () => import('@/views/ConfigEspaciosView.vue'), meta: { requiresAuth: true, soloAdmin: true } },
  { path: '/config-espacios/seccion/:id', component: () => import('@/views/EspaciosSeccionView.vue'), meta: { requiresAuth: true, soloAdmin: true } },
  { path: '/entradas-salidas', component: () => import('@/views/EntradasSalidasView.vue'), meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// ── Guard: revisa si el usuario está logueado antes de cada ruta ──

router.beforeEach((to, from) => {
  const token   = localStorage.getItem('token')
  const usuario = JSON.parse(localStorage.getItem('usuario') || 'null')

  if (to.meta.requiresAuth && !token) {
    return '/'
  }

  if (to.path === '/' && token) {
    return '/home'
  }

  if (to.meta.soloAdmin && usuario?.rol !== 'Administrador') {
    return '/home'
  }

  return true
})

export default router



