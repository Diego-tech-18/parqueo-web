<template>
  <!-- Overlay oscuro detrás del modal -->
  <div class="modal-overlay" @click.self="$emit('cerrar')">
    <div class="modal-container">

      <!-- Cabecera -->
      <div class="modal-header">
        <h2>{{ editando ? 'Editar Sección' : 'Nueva Sección' }}</h2>
        <button class="btn-x" @click="$emit('cerrar')">✕</button>
      </div>

      <!-- Cuerpo del formulario -->
      <div class="modal-body">

        <!-- Nombre -->
        <div class="campo">
          <label>Nombre de la Sección <span class="req">*</span></label>
          <input 
            v-model="form.nombre" 
            placeholder="Ej: A, B, VIP" 
            maxlength="50"
          />
          <span class="error-campo" v-if="errores.nombre">{{ errores.nombre }}</span>
        </div>

        <!-- Tipo -->
        <div class="campo">
          <label>Tipo <span class="req">*</span></label>
          <select v-model="form.tipo">
            <option value="" disabled>Seleccionar tipo</option>
            <option value="ASIGNADOS">Asignados (para abonados)</option>
            <option value="ROTATIVOS">Rotativos (ocasionales)</option>
          </select>
          <span class="error-campo" v-if="errores.tipo">{{ errores.tipo }}</span>
        </div>
        

        <!-- Descripción -->
        <div class="campo">
          <label>Descripción (Opcional)</label>
          <textarea 
            v-model="form.descripcion" 
            placeholder="Descripción de la sección..."
            rows="3"
          ></textarea>
        </div>

      </div>

      <!-- Error general -->
      <p class="error-general" v-if="errorGeneral">{{ errorGeneral }}</p>

      <!-- Botones -->
      <div class="modal-footer">
        <button class="btn-cancelar" @click="$emit('cerrar')">Cancelar</button>
        <button class="btn-guardar" @click="guardar" :disabled="cargando">
          {{ cargando ? 'Guardando...' : (editando ? 'Guardar Cambios' : 'Crear Sección') }}
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
//  FORMULARIO: SECCIÓN - VORTEX 

import '@/assets/css/forms.css'
import { ref, watch, computed } from 'vue'
import { useSecciones } from '@/composables/useSecciones'


// PROPS Y EVENTOS

const props = defineProps({
  seccionEditar: {
    type: Object,
    default: null  // null = modo crear, objeto = modo editar
  }
})

const emit = defineEmits(['cerrar', 'guardado'])

// Composable: lógica de secciones (incluye 409 + soft delete + reactivar)
const { crear, actualizar } = useSecciones()

// ESTADO

const cargando = ref(false)
const errorGeneral = ref('')

// Modo (crear/editar) calculado desde la prop. Reactivo, sin bug.
const editando = computed(() => props.seccionEditar !== null)

const form = ref({
  nombre: '',
  tipo: '',
  descripcion: '',
})

const errores = ref({})


// WATCH: Cargar datos si es edición

watch(() => props.seccionEditar, (seccion) => {
  if (seccion) {
    // Modo edición: cargar datos
    form.value = {
      nombre: seccion.nombre,
      tipo: seccion.tipo,
      descripcion: seccion.descripcion || '',
    }
  } else {
    // Modo crear: limpiar
    form.value = {
      nombre: '',
      tipo: '',
      descripcion: '',
    }
  }
}, { immediate: true })


// FUNCIONES


/**
 * Valida los campos del formulario
 */
function validar() {
  errores.value = {}

  if (!form.value.nombre) {
    errores.value.nombre = 'El nombre es obligatorio'
  }

  if (!form.value.tipo) {
    errores.value.tipo = 'El tipo es obligatorio'
  }

  return Object.keys(errores.value).length === 0
}

//Guarda la sección (crea o edita)
 
async function guardar() {
  errorGeneral.value = ''

  if (!validar()) return

  cargando.value = true

  const datos = {
    nombre: form.value.nombre,
    tipo: form.value.tipo,
    descripcion: form.value.descripcion || null,
  }

  try {
    // Llamar al composable (que maneja 409, soft delete, notificaciones)
    const exito = editando.value
      ? await actualizar(props.seccionEditar.id, datos)
      : await crear(datos)

    if (exito) {
      emit('guardado')
      emit('cerrar')
    }
    // Si exito === false, el composable ya mostró la notificación.
    // El formulario queda abierto para que el usuario pueda corregir o usar otro nombre.

  } catch (error) {
    // Solo errores inesperados llegan aquí
    console.error('Error inesperado al guardar sección:', error)
    errorGeneral.value = 'Error al guardar la sección. Intenta de nuevo.'
  } finally {
    cargando.value = false
  }
}
</script>