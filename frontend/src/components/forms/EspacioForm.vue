<template>
  <!-- Overlay oscuro detrás del modal -->
  <div class="modal-overlay" @click.self="$emit('cerrar')">
    <div class="modal-container">

      <!-- Cabecera -->
      <div class="modal-header">
        <h2>{{ editando ? 'Editar Espacio' : 'Nuevo Espacio' }}</h2>
        <button class="btn-x" @click="$emit('cerrar')">✕</button>
      </div>

      <!-- Cuerpo del formulario -->
      <div class="modal-body">

        <!-- Fila 1: Número y Sección -->
        <div class="fila">
          <div class="campo">
            <label>Número/Código <span class="req">*</span></label>
            <input 
              v-model="form.numero" 
              placeholder="Ej: A1, B5, VIP-01" 
              maxlength="20"
            />
            <span class="error-campo" v-if="errores.numero">{{ errores.numero }}</span>
          </div>

          <div class="campo">
            <label>Sección <span class="req">*</span></label>
            <select v-model="form.seccion"  :disabled="!!seccionPreseleccionada">
              <option :value="null">Selecciona una sección</option>
              <option 
                v-for="seccion in secciones" 
                :key="seccion.id"
                :value="seccion.id">
                Sección {{ seccion.nombre }}
              </option>
            </select>
            <span class="error-campo" v-if="errores.seccion">{{ errores.seccion }}</span>
          </div>
        </div>

        <!-- Fila 2: Posición en el mapa -->
        <div class="fila">
          <div class="campo">
            <label>Fila en el Mapa</label>
            <input 
              v-model.number="form.posicion_fila" 
              type="number" 
              min="0"
              placeholder="0"
            />
          </div>

          <div class="campo">
            <label>Columna en el Mapa</label>
            <input 
              v-model.number="form.posicion_columna" 
              type="number" 
              min="0"
              placeholder="0"
            />
          </div>
        </div>

        <!-- Fila 3: Estado y Activo -->
        <div class="fila">
          <div class="campo">
            <label>Estado Inicial</label>
            <select v-model="form.estado">
              <option value="LIBRE">Libre</option>
              <option value="OCUPADO">Ocupado</option>
              <option value="FUERA_SERVICIO">Fuera de Servicio</option>
            </select>
          </div>

          <div class="campo">
            <label>
              <input 
                type="checkbox" 
                v-model="form.activo"
                style="width: auto; margin-right: 8px;"
              />
              Espacio activo
            </label>
            <small style="color: #64748b; display: block; margin-top: 5px;">
              Si está desactivado, no se mostrará en el mapa
            </small>
          </div>
        </div>

        <!-- Notas -->
        <div class="campo full">
          <label>Notas (Opcional)</label>
          <textarea 
            v-model="form.notas" 
            placeholder="Notas sobre este espacio..."
            rows="2"
          ></textarea>
        </div>

      </div>

      <!-- Error general -->
      <p class="error-general" v-if="errorGeneral">{{ errorGeneral }}</p>

      <!-- Botones -->
      <div class="modal-footer">
        <button class="btn-cancelar" @click="$emit('cerrar')">Cancelar</button>
        <button class="btn-guardar" @click="guardar" :disabled="cargando">
          {{ cargando ? 'Guardando...' : (editando ? 'Guardar Cambios' : 'Crear Espacio') }}
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
// ════════════════════════════════════════════════════════════════════
// FORMULARIO: ESPACIO (crear y editar) - VORTEX
// ════════════════════════════════════════════════════════════════════
//
// Componente "tonto" — solo presenta el formulario y emite eventos.
// La lógica de negocio (crear, editar, manejar 409 de soft delete,
// notificaciones) vive en el composable useEspacios.

import '@/assets/css/forms.css'
import { ref, watch, onMounted, computed } from 'vue'
import { getSecciones } from '@/api/espacios'
import { useEspacios } from '@/composables/useEspacios'

// ── PROPS Y EVENTOS ──────────────────────────────────────────────────

const props = defineProps({
  espacioEditar: {
    type: Object,
    default: null  // null = modo crear, objeto = modo editar
  },
  seccionPreseleccionada: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['cerrar', 'guardado'])

// ── Composable: lógica de espacios ──────────────────────────────────
const { crear, actualizar } = useEspacios()

// ── ESTADO ──────────────────────────────────────────────────────────

const cargando = ref(false)
const errorGeneral = ref('')
const secciones = ref([])

// Modo (crear / editar) calculado a partir de la prop. Reactivo, sin bug.
const editando = computed(() => props.espacioEditar !== null)

const form = ref({
  numero: '',
  seccion: '',
  estado: 'LIBRE',
  posicion_fila: 0,
  posicion_columna: 0,
  activo: true,
  notas: '',
})

const errores = ref({})

// ── WATCH: cargar datos si cambia el modo (crear ↔ editar) ──────────

watch(() => props.espacioEditar, (nuevoEspacio) => {
  if (nuevoEspacio) {
    // Modo edición: copiar valores del espacio
    form.value = {
      numero: nuevoEspacio.numero,
      seccion: nuevoEspacio.seccion,
      estado: nuevoEspacio.estado,
      posicion_fila: nuevoEspacio.posicion_fila,
      posicion_columna: nuevoEspacio.posicion_columna,
      activo: nuevoEspacio.activo,
      notas: nuevoEspacio.notas || ''
    }
  } else {
    // Modo crear
    form.value = {
      numero: '',
      seccion: props.seccionPreseleccionada || null,
      estado: 'LIBRE',
      posicion_fila: 0,
      posicion_columna: 0,
      activo: true,
      notas: ''
    }
  }
}, { immediate: true })

// ── FUNCIONES ───────────────────────────────────────────────────────

async function cargarSecciones() {
  try {
    const respuesta = await getSecciones()
    secciones.value = respuesta.data
  } catch (error) {
    console.error('Error al cargar secciones:', error)
  }
}

function validar() {
  errores.value = {}

  if (!form.value.numero) {
    errores.value.numero = 'El número es obligatorio'
  }

  if (!form.value.seccion) {
    errores.value.seccion = 'Debes seleccionar una sección'
  }

  return Object.keys(errores.value).length === 0
}

async function guardar() {
  errorGeneral.value = ''

  if (!validar()) return

  cargando.value = true

  const datos = {
    numero: form.value.numero,
    seccion: form.value.seccion,
    estado: form.value.estado,
    posicion_fila: form.value.posicion_fila,
    posicion_columna: form.value.posicion_columna,
    activo: form.value.activo,
    notas: form.value.notas || null,
  }

  try {
    // Llamar al composable (que maneja 409, soft delete, notificaciones)
    const exito = editando.value
      ? await actualizar(props.espacioEditar.id, datos)
      : await crear(datos)

    if (exito) {
      emit('guardado')
      emit('cerrar')
    }
    // Si exito === false, el composable ya mostró la notificación de error.
    // El formulario queda abierto para que el usuario pueda corregir.

  } catch (error) {
    // Solo errores inesperados llegan aquí (los esperados los maneja el composable)
    console.error('Error inesperado al guardar espacio:', error)
    errorGeneral.value = 'Error al guardar el espacio. Intenta de nuevo.'
  } finally {
    cargando.value = false
  }
}

// ── CICLO DE VIDA ───────────────────────────────────────────────────

onMounted(() => {
  cargarSecciones()
})
</script>