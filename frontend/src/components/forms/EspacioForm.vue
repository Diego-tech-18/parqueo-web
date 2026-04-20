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
            <select v-model="form.seccion">
              <option value="" disabled>Seleccionar sección</option>
              <option 
                v-for="seccion in secciones" 
                :key="seccion.id"
                :value="seccion.id"
              >
                Sección {{ seccion.nombre }} ({{ seccion.tipo }})
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


// FORMULARIO: ESPACIO - VORTEX


import '@/assets/css/forms.css'
import { ref, watch, onMounted } from 'vue'
import { crearEspacio, actualizarEspacio, getSecciones } from '@/api/espacios'


// PROPS Y EVENTOS


const props = defineProps({
  espacioEditar: {
    type: Object,
    default: null  // null = modo crear, objeto = modo editar
  }
})

const emit = defineEmits(['cerrar', 'guardado'])

// ESTADO


const cargando = ref(false)
const errorGeneral = ref('')
const editando = ref(false)
const secciones = ref([])

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


// WATCH: Cargar datos si es edición


watch(() => props.espacioEditar, (espacio) => {
  if (espacio) {
    editando.value = true
    form.value = {
      numero: espacio.numero,
      seccion: espacio.seccion,
      estado: espacio.estado,
      posicion_fila: espacio.posicion_fila,
      posicion_columna: espacio.posicion_columna,
      activo: espacio.activo,
      notas: espacio.notas || '',
    }
  }
}, { immediate: true })


// FUNCIONES

async function cargarSecciones() {
  try {
    const respuesta = await getSecciones()
    secciones.value = respuesta.data
  } catch (error) {
    console.error('Error al cargar secciones:', error)
  }
}

/**
 * Valida los campos del formulario
 */
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

/**
 * Guarda el espacio (crea o edita)
 */
async function guardar() {
  errorGeneral.value = ''
  
  if (!validar()) return

  cargando.value = true

  try {
    const datos = {
      numero: form.value.numero,
      seccion: form.value.seccion,
      estado: form.value.estado,
      posicion_fila: form.value.posicion_fila,
      posicion_columna: form.value.posicion_columna,
      activo: form.value.activo,
      notas: form.value.notas || null,
    }

    if (editando.value) {
      await actualizarEspacio(props.espacioEditar.id, datos)
    } else {
      await crearEspacio(datos)
    }

    emit('guardado')
    emit('cerrar')

  } catch (error) {
    console.error('Error al guardar espacio:', error)
    
    if (error.response?.data?.numero) {
      errores.value.numero = error.response.data.numero[0]
    } else {
      errorGeneral.value = 'Error al guardar el espacio. Intenta de nuevo.'
    }
  } finally {
    cargando.value = false
  }
}

// CICLO DE VIDA

onMounted(() => {
  cargarSecciones()
})
</script>