<template>
  <!-- Overlay oscuro detrás del modal -->
  <div class="modal-overlay" @click.self="$emit('cerrar')">
    <div class="modal-container">

      <!-- Cabecera -->
      <div class="modal-header">
        <h2> Editar Espacio {{ espacio?.numero }}</h2>
        <button class="btn-x" @click="$emit('cerrar')">✕</button>
      </div>

      <!-- Cuerpo del formulario -->
      <div class="modal-body">

        <!-- Info bloqueada -->
        <div class="info-bloqueada">
          <div class="info-item">
            <label>Número:</label>
            <span class="valor">{{ espacio.numero }}</span>
          </div>
          <div class="info-item">
            <label>Sección:</label>
            <span class="valor">{{ espacio.seccion_nombre }}</span>
          </div>
        </div>

        <!-- Fila 1: Posición en el mapa -->
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

        <!-- Estado -->
        <div class="campo">
          <label>Estado</label>
          <select v-model="form.estado">
            <option value="LIBRE">Libre</option>
            <option value="OCUPADO">Ocupado</option>
            <option value="FUERA_SERVICIO">Fuera de Servicio</option>
          </select>
        </div>

        <!-- Activo -->
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

        <!-- Notas -->
        <div class="campo full">
          <label>Notas (Opcional)</label>
          <textarea 
            v-model="form.notas" 
            placeholder="Notas sobre este espacio..."
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
          {{ cargando ? 'Guardando...' : ' Guardar Cambios' }}
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import '@/assets/css/forms.css'
import { ref, onMounted } from 'vue'
import { actualizarEspacio } from '@/api/espacios'

// PROPS Y EVENTOS
const props = defineProps({
  espacio: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['cerrar', 'guardado'])

// ESTADO
const cargando = ref(false)
const errorGeneral = ref('')

const form = ref({
  estado: '',
  posicion_fila: 0,
  posicion_columna: 0,
  activo: true,
  notas: '',
})

// FUNCIONES
function cargarDatos() {
  form.value = {
    estado: props.espacio.estado,
    posicion_fila: props.espacio.posicion_fila,
    posicion_columna: props.espacio.posicion_columna,
    activo: props.espacio.activo,
    notas: props.espacio.notas || '',
  }
}

async function guardar() {
  errorGeneral.value = ''
  cargando.value = true

  try {
    const datos = {
      numero: props.espacio.numero,  // No se cambia pero se envía
      seccion: props.espacio.seccion,  // No se cambia pero se envía
      estado: form.value.estado,
      posicion_fila: form.value.posicion_fila,
      posicion_columna: form.value.posicion_columna,
      activo: form.value.activo,
      notas: form.value.notas || null,
    }

    await actualizarEspacio(props.espacio.id, datos)

    emit('guardado')
    emit('cerrar')

  } catch (error) {
    console.error('Error al actualizar espacio:', error)
    errorGeneral.value = 'Error al guardar cambios. Intenta de nuevo.'
  } finally {
    cargando.value = false
  }
}

onMounted(() => {
  cargarDatos()
})
</script>

<style scoped>
/* Info bloqueada (no editable) */
.info-bloqueada {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
  display: flex;
  gap: 24px;
}

.info-item {
  display: flex;
  gap: 8px;
  align-items: center;
}

.info-item label {
  font-weight: 600;
  color: #64748b;
  font-size: 0.9rem;
}

.info-item .valor {
  font-weight: 700;
  color: #1e293b;
  font-size: 1rem;
}
</style>