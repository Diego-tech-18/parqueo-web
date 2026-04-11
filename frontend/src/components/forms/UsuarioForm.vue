<template>
  <!-- Overlay oscuro detrás del modal -->
  <div class="modal-overlay" @click.self="$emit('cerrar')">
    <div class="modal-container">

      <!-- Cabecera -->
      <div class="modal-header">
        <h2>{{ editando ? 'Editar Usuario' : 'Nuevo Usuario' }}</h2>
        <button class="btn-x" @click="$emit('cerrar')">✕</button>
      </div>

      <!-- Cuerpo del formulario -->
      <div class="modal-body">

        <!-- Fila 1: Nombre y Apellido -->
        <div class="fila">
          <div class="campo">
            <label>Nombre <span class="req">*</span></label>
            <input v-model="form.nombre" placeholder="Ej: Diego" />
            <span class="error-campo" v-if="errores.nombre">{{ errores.nombre }}</span>
          </div>
          <div class="campo">
            <label>Apellido <span class="req">*</span></label>
            <input v-model="form.apellido" placeholder="Ej: Montaño" />
            <span class="error-campo" v-if="errores.apellido">{{ errores.apellido }}</span>
          </div>
        </div>

        <!-- Fila 2: CI y Teléfono -->
        <div class="fila">
          <div class="campo">
            <label>Carnet de Identidad <span class="req">*</span></label>
            <input v-model="form.ci" placeholder="Ej: 12345678" />
            <span class="error-campo" v-if="errores.ci">{{ errores.ci }}</span>
          </div>
          <div class="campo">
            <label>Teléfono</label>
            <input v-model="form.telefono" placeholder="Ej: 70012345" />
          </div>
        </div>

        <!-- Fila 3: Email -->
        <div class="fila">
          <div class="campo full">
            <label>Correo Electrónico <span class="req">*</span></label>
            <input v-model="form.email" type="email" placeholder="Ej: diego@vortex.com" />
            <span class="error-campo" v-if="errores.email">{{ errores.email }}</span>
          </div>
        </div>

        <!-- Fila 4: Contraseña y Confirmar -->
        <div class="fila">
          <div class="campo">
            <label>Contraseña <span class="req" v-if="!editando">*</span></label>
            <div class="input-icon">
             
              <input
                v-model="form.password"
                :type="verPass ? 'text' : 'password'"
                placeholder="Contraseña"
              />
              <span @click="verPass = !verPass">{{ verPass ? '🙈' : '👁️' }}</span>
            </div>
            <span class="error-campo" v-if="errores.password">{{ errores.password }}</span>
          </div>
          <div class="campo">
            <label>Confirmar Contraseña <span class="req" v-if="!editando">*</span></label>
            <div class="input-icon">
              <input
                v-model="form.confirmar"
                :type="verPass ? 'text' : 'password'"
                placeholder="Repite la contraseña"
              />
            </div>
            <span class="error-campo" v-if="errores.confirmar">{{ errores.confirmar }}</span>
          </div>
        </div>

        <!-- Fila 5: Rol y Foto -->
        <div class="fila">
          <div class="campo">
            <label>Asignar Rol <span class="req">*</span></label>
            <select v-model="form.rol">
              <option value="" disabled>Seleccionar rol</option>
              <option value="Administrador">Administrador</option>
              <option value="Empleado">Empleado</option>
            </select>
            <span class="error-campo" v-if="errores.rol">{{ errores.rol }}</span>
          </div>
          <div class="campo">
            <label>Foto de Perfil</label>
            <div class="foto-upload" @click="$refs.inputFoto.click()">
              <img v-if="preview" :src="preview" class="foto-preview" />
              <div v-else class="foto-placeholder">
                <span>📷</span>
                <p>Subir foto</p>
              </div>
            </div>
            <input
              ref="inputFoto"
              type="file"
              accept="image/*"
              style="display:none"
              @change="cargarFoto"
            />
          </div>
        </div>

      </div>

      <!-- Error general -->
      <p class="error-general" v-if="errorGeneral">{{ errorGeneral }}</p>

      <!-- Botones -->
      <div class="modal-footer">
        <button class="btn-cancelar" @click="$emit('cerrar')">Cancelar</button>
        <button class="btn-guardar" @click="guardar" :disabled="cargando">
          {{ cargando ? 'Guardando...' : (editando ? 'Guardar cambios' : 'Agregar Usuario') }}
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import '@/assets/css/forms.css'
import { ref, watch } from 'vue'
import { crearUsuario, editarUsuario } from '@/api/usuarios.js'

// ── Props y eventos ──
const props = defineProps({
  usuarioEditar: {
    type: Object,
    default: null  // null = modo crear, objeto = modo editar
  }
})
const emit = defineEmits(['cerrar', 'guardado'])

// ── Estado del formulario ──
const cargando    = ref(false)
const verPass     = ref(false)
const preview     = ref(null)
const errorGeneral = ref('')
const archivoFoto = ref(null)

const form = ref({
  nombre   : '',
  apellido : '',
  ci       : '',
  telefono : '',
  email    : '',
  password : '',
  confirmar: '',
  rol      : '',
})

const errores = ref({})

// ── Si viene usuarioEditar → modo editar, llena el form ──
const editando = ref(false)

watch(() => props.usuarioEditar, (usuario) => {
  if (usuario) {
    editando.value = true
    form.value = {
      nombre   : usuario.nombre,
      apellido : usuario.apellido,
      ci       : usuario.ci,
      telefono : usuario.telefono || '',
      email    : usuario.email,
      password : '',
      confirmar: '',
      rol      : usuario.rol,
    }
    preview.value = usuario.foto || null
  }
}, { immediate: true })

// ── Cargar foto y mostrar preview ──
function cargarFoto(e) {
  const archivo = e.target.files[0]
  if (!archivo) return
  archivoFoto.value = archivo
  preview.value = URL.createObjectURL(archivo)
}

// ── Validar campos obligatorios ──
function validar() {
  errores.value = {}

  if (!form.value.nombre)   errores.value.nombre   = 'El nombre es obligatorio'
  if (!form.value.apellido) errores.value.apellido = 'El apellido es obligatorio'
  if (!form.value.ci)       errores.value.ci       = 'El CI es obligatorio'
  if (!form.value.email)    errores.value.email    = 'El email es obligatorio'
  if (!form.value.rol)      errores.value.rol      = 'El rol es obligatorio'

  // Contraseña solo obligatoria al crear
  if (!editando.value) {
    if (!form.value.password)
      errores.value.password = 'La contraseña es obligatoria'
    if (form.value.password !== form.value.confirmar)
      errores.value.confirmar = 'Las contraseñas no coinciden'
  }

  return Object.keys(errores.value).length === 0
}

// ── Guardar: crea o edita según modo ──
async function guardar() {
  errorGeneral.value = ''
  if (!validar()) return

  cargando.value = true

  try {
    // Usar FormData para enviar foto + datos juntos
    const datos = new FormData()
    datos.append('nombre',   form.value.nombre)
    datos.append('apellido', form.value.apellido)
    datos.append('ci',       form.value.ci)
    datos.append('email',    form.value.email)
    datos.append('rol',      form.value.rol)

    if (form.value.telefono)
      datos.append('telefono', form.value.telefono)

    if (form.value.password)
      datos.append('password', form.value.password)

    if (archivoFoto.value)
      datos.append('foto', archivoFoto.value)

    if (editando.value) {
      // PUT /api/usuarios/:id/
      await editarUsuario(props.usuarioEditar.id, datos)
    } else {
      // POST /api/usuarios/
      await crearUsuario(datos)
    }

    emit('guardado')  // avisa a UsuariosView que recargue la tabla
    emit('cerrar')

  } catch (e) {
    errorGeneral.value = e.response?.data?.email?.[0]
      || e.response?.data?.ci?.[0]
      || 'Error al guardar, intenta de nuevo'
  } finally {
    cargando.value = false
  }
}
</script>