// ════════════════════════════════════════════════════════════════════
// COMPOSABLE: Debounce - VORTEX
// ════════════════════════════════════════════════════════════════════
//
// Toma un ref reactivo (típicamente el valor de un input) y devuelve
// otra ref que se actualiza con un retraso. Útil para búsquedas:
// el filtro solo se ejecuta cuando el usuario deja de escribir.
//
// Uso:
//   import { ref } from 'vue'
//   import { useDebounce } from '@/composables/useDebounce'
//
//   const busqueda = ref('')
//   const busquedaConDebounce = useDebounce(busqueda, 300)
//
//   // Usar busquedaConDebounce.value en computeds o watchers
//   // en lugar de busqueda.value.

import { ref, watch, onUnmounted } from 'vue'

export function useDebounce(refOriginal, delayMs = 300) {
  const refConDebounce = ref(refOriginal.value)
  let timeoutId = null

  // Cada vez que cambia el ref original, programar la actualización
  // del ref con debounce. Si llega otro cambio antes de que se ejecute,
  // cancelamos el anterior y reiniciamos.
  watch(refOriginal, (nuevoValor) => {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }
    timeoutId = setTimeout(() => {
      refConDebounce.value = nuevoValor
    }, delayMs)
  })

  // Si el componente se desmonta, cancelar timer pendiente
  onUnmounted(() => {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }
  })

  return refConDebounce
}