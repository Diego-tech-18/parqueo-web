// ════════════════════════════════════════════════════════════════════
// COMPOSABLE: Tarifas - VORTEX
// ════════════════════════════════════════════════════════════════════
//
// Lógica de lectura y actualización de la configuración de tarifas.
// La vista solo presenta — la lógica vive aquí (arquitectura por capas).

import { ref } from 'vue'
import api from '@/api/auth'
import { API_ENDPOINTS } from '@/constants/api'
import { useNotificaciones } from './useNotificaciones'

export function useTarifas() {
  const { mostrarExito, mostrarError } = useNotificaciones()

  const tarifas = ref(null)
  const cargando = ref(false)
  const errorCarga = ref('')
  const guardando = ref(false)

  async function cargarTarifas() {
    cargando.value = true
    errorCarga.value = ''
    try {
      const respuesta = await api.get(API_ENDPOINTS.TARIFAS.GET)
      tarifas.value = respuesta.data
      return respuesta.data
    } catch (error) {
      console.error('Error al cargar tarifas:', error)
      errorCarga.value = 'No se pudieron cargar las tarifas.'
      return null
    } finally {
      cargando.value = false
    }
  }

  async function guardarTarifas(datos) {
    guardando.value = true
    try {
      const respuesta = await api.put(API_ENDPOINTS.TARIFAS.UPDATE, datos)
      tarifas.value = respuesta.data
      mostrarExito('Tarifas actualizadas correctamente')
      return true
    } catch (error) {
      console.error('Error al guardar tarifas:', error)
      // El backend devuelve el mensaje de validación de negocio
      const msg = error.response?.data?.error || 'No se pudieron guardar las tarifas'
      mostrarError(msg)
      return false
    } finally {
      guardando.value = false
    }
  }

  return {
    tarifas,
    cargando,
    errorCarga,
    guardando,
    cargarTarifas,
    guardarTarifas,
  }
}