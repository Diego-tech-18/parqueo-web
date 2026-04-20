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
import { ref, watch } from 'vue'
import { crearSeccion, actualizarSeccion } from '@/api/espacios'


// PROPS Y EVENTOS

const props = defineProps({
  seccionEditar: {
    type: Object,
    default: null  // null = modo crear, objeto = modo editar
  }
})

const emit = defineEmits(['cerrar', 'guardado'])

// ESTADO

const cargando = ref(false)
const errorGeneral = ref('')
const editando = ref(false)

const form = ref({
  nombre: '',
  tipo: '',
  descripcion: '',
})

const errores = ref({})


// WATCH: Cargar datos si es edición

watch(() => props.seccionEditar, (seccion) => {
  if (seccion) {
    editando.value = true
    form.value = {
      nombre: seccion.nombre,
      tipo: seccion.tipo,
      descripcion: seccion.descripcion || '',
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

  try {
    const datos = {
      nombre: form.value.nombre,
      tipo: form.value.tipo,
      descripcion: form.value.descripcion || null,
    }

    if (editando.value) {
      await actualizarSeccion(props.seccionEditar.id, datos)
    } else {
      await crearSeccion(datos)
    }

    emit('guardado')
    emit('cerrar')

  } catch (error) {
    console.error('Error al guardar sección:', error)
    
    if (error.response?.data?.nombre) {
      errores.value.nombre = error.response.data.nombre[0]
    } else {
      errorGeneral.value = 'Error al guardar la sección. Intenta de nuevo.'
    }
  } finally {
    cargando.value = false
  }
}
</script>