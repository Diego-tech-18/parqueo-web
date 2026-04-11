import api from './auth.js'

// ── Llama a Django cada 4 minutos para mantener Supabase despierto ──
export function iniciarKeepAlive() {
  setInterval(async () => {
    try {
      await api.get('/auth/ping/')
    } catch (e) {
      // silencioso, no importa si falla
    }
  }, 4 * 60 * 1000) // cada 4 minutos
}