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
            <input v-model="form.telefono" placeholder="Ej: 70012345" maxlength="15" />
          </div>
        </div>

        <!-- Fila 3: Email -->
        <div class="fila">
          <div class="campo full">
            <label>Correo Electrónico <span class="req">*</span></label>
            <input v-model="form.email" type="email" placeholder="Ej: diego@vortex.com" autocomplete="off" />
            <span class="error-campo" v-if="errores.email">{{ errores.email }}</span>
          </div>
        </div>

        <!-- Fila 4: Contraseña y Confirmar -->
        <div class="fila">
          <div class="campo">
            <label>
              Contraseña 
              <span class="req" v-if="!editando">*</span>
              <span v-if="editando" style="font-size: 0.8rem; color: #64748b;">(Dejar vacío para mantener)</span>
            </label>
            <div class="input-icon">
              <input
                v-model="form.password"
                :type="verPass ? 'text' : 'password'"
                :placeholder="editando ? 'Nueva contraseña (opcional)' : 'Mínimo 8 caracteres'"
                @input="validarPasswordEnTiempoReal"
                 autocomplete="new-password"
              />
              <span @click="verPass = !verPass" style="cursor: pointer;">
                {{ verPass ? '🙈' : '👁️' }}
              </span>
            </div>
            <span class="error-campo" v-if="errores.password">{{ errores.password }}</span>
            
            <!-- Requisitos de contraseña -->
            <div v-if="form.password && mostrarRequisitos" class="requisitos-password">
              <p style="font-size: 0.85rem; margin: 8px 0 5px 0; font-weight: 500;"></p>
              <ul style="margin: 0; padding-left: 20px; font-size: 0.8rem;">
                <li :class="{ cumplido: requisitos.longitud }">
                  {{ requisitos.longitud ? '✓' : '✗' }} Mínimo 8 caracteres
                </li>
                <li :class="{ cumplido: requisitos.numero }">
                  {{ requisitos.numero ? '✓' : '✗' }} Al menos un número
                </li>
              
              </ul>
            </div>
          </div>
          
          <div class="campo">
            <label>Confirmar Contraseña <span class="req" v-if="!editando || form.password">*</span></label>
            <div class="input-icon">
              <input
                v-model="form.confirmar"
                :type="verPass ? 'text' : 'password'"
                placeholder="Repite la contraseña"
                :disabled="!form.password"
                autocomplete="new-password"
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

        <!-- Fila 6: Estado Activo (solo en edición) -->
        <div class="fila" v-if="editando">
          <div class="campo full">
            <label style="display: flex; align-items: center; gap: 10px; cursor: pointer;">
              <input 
                type="checkbox" 
                v-model="form.activo"
                style="width: 20px; height: 20px; cursor: pointer;"
              />
              <span>Usuario activo (puede iniciar sesión)</span>
            </label>
            <p style="font-size: 0.85rem; color: #64748b; margin-top: 5px;">
              Desmarcar para suspender el acceso sin eliminar el historial
            </p>
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
import { ref, watch, computed } from 'vue'
import { crearUsuario, actualizarUsuario } from '@/api/usuarios.js'

// ══════════════════════════════════════════════════════════════════════════
// PROPS Y EVENTOS
// ══════════════════════════════════════════════════════════════════════════

const props = defineProps({
  usuarioEditar: {
    type: Object,
    default: null  // null = modo crear, objeto = modo editar
  }
})

const emit = defineEmits(['cerrar', 'guardado'])

// ══════════════════════════════════════════════════════════════════════════
// ESTADO
// ══════════════════════════════════════════════════════════════════════════

const cargando = ref(false)
const verPass = ref(false)
const preview = ref(null)
const errorGeneral = ref('')
const archivoFoto = ref(null)
const editando = ref(false)
const usuarioId = ref(null)
const mostrarRequisitos = ref(false)

const form = ref({
  nombre: '',
  apellido: '',
  ci: '',
  telefono: '',
  email: '',
  password: '',
  confirmar: '',
  rol: '',
   activo: true,
})

const errores = ref({})

// ══════════════════════════════════════════════════════════════════════════
// VALIDACIÓN DE CONTRASEÑA EN TIEMPO REAL
// ══════════════════════════════════════════════════════════════════════════

const requisitos = computed(() => {
  const pass = form.value.password
  return {
    longitud: pass.length >= 8,
    mayuscula: /[A-Z]/.test(pass),
    numero: /[0-9]/.test(pass),
    simbolo: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(pass),
  }
})

const passwordValida = computed(() => {
  return requisitos.value.longitud &&
         requisitos.value.mayuscula &&
         requisitos.value.numero &&
         requisitos.value.simbolo
})

function validarPasswordEnTiempoReal() {
  mostrarRequisitos.value = form.value.password.length > 0
  
  // Limpiar error de contraseña si está escribiendo
  if (errores.value.password) {
    delete errores.value.password
  }
}

// ══════════════════════════════════════════════════════════════════════════
// WATCH: Si viene usuarioEditar → modo editar
// ══════════════════════════════════════════════════════════════════════════

watch(() => props.usuarioEditar, (usuario) => {
  if (usuario) {
    editando.value = true
    usuarioId.value = usuario.id
    form.value = {
      nombre: usuario.nombre,
      apellido: usuario.apellido,
      ci: usuario.ci,
      telefono: usuario.telefono || '',
      email: usuario.email,
      password: '',      // ← VACÍO para edición
      confirmar: '',     // ← VACÍO para edición
      rol: usuario.rol,
      activo: usuario.activo !== undefined ? usuario.activo : true,
    }
    preview.value = usuario.foto || null
  }
}, { immediate: true })

// ══════════════════════════════════════════════════════════════════════════
// FUNCIONES
// ══════════════════════════════════════════════════════════════════════════

function cargarFoto(e) {
  const archivo = e.target.files[0]
  if (!archivo) return
  archivoFoto.value = archivo
  preview.value = URL.createObjectURL(archivo)
}

function validar() {
  errores.value = {}

  // Campos obligatorios
  if (!form.value.nombre) errores.value.nombre = 'El nombre es obligatorio'
  if (!form.value.apellido) errores.value.apellido = 'El apellido es obligatorio'
  if (!form.value.ci) errores.value.ci = 'El CI es obligatorio'
  if (!form.value.email) errores.value.email = 'El email es obligatorio'
  if (!form.value.rol) errores.value.rol = 'El rol es obligatorio'

  // Validación de contraseña
  if (!editando.value) {
    // Al crear: contraseña obligatoria
    if (!form.value.password) {
      errores.value.password = 'La contraseña es obligatoria'
    } else if (!passwordValida.value) {
      errores.value.password = 'La contraseña no cumple los requisitos mínimos'
    }
    
    if (form.value.password !== form.value.confirmar) {
      errores.value.confirmar = 'Las contraseñas no coinciden'
    }
  } else {
    // Al editar: solo validar si se ingresó una nueva contraseña
    if (form.value.password) {
      if (!passwordValida.value) {
        errores.value.password = 'La contraseña no cumple los requisitos mínimos'
      }
      
      if (form.value.password !== form.value.confirmar) {
        errores.value.confirmar = 'Las contraseñas no coinciden'
      }
    }
  }

  return Object.keys(errores.value).length === 0
}

async function guardar() {
  errorGeneral.value = ''
  
  if (!validar()) {
    errorGeneral.value = 'Por favor corrige los errores antes de continuar'
    return
  }

  cargando.value = true

  try {
    const datos = new FormData()
    datos.append('nombre', form.value.nombre)
    datos.append('apellido', form.value.apellido)
    datos.append('ci', form.value.ci)
    datos.append('email', form.value.email)
    datos.append('rol', form.value.rol)
    datos.append('activo', form.value.activo)

    if (form.value.telefono)
      datos.append('telefono', form.value.telefono)

    // Solo enviar contraseña si se ingresó una
    if (form.value.password)
      datos.append('password', form.value.password)

    if (archivoFoto.value)
      datos.append('foto', archivoFoto.value)

    if (editando.value) {
      await actualizarUsuario(usuarioId.value, datos)
    } else {
      await crearUsuario(datos)
    }

    emit('guardado')
    emit('cerrar')

  } catch (e) {
    console.error('Error al guardar usuario:', e)
    errorGeneral.value = e.response?.data?.email?.[0]
      || e.response?.data?.ci?.[0]
      || e.response?.data?.password?.[0]
      || 'Error al guardar, intenta de nuevo'
  } finally {
    cargando.value = false
  }
}
</script>

<style scoped>
.requisitos-password {
  margin-top: 8px;
  padding: 10px;
  background: #f8fafc;
  border-radius: 6px;
  border-left: 3px solid #3b82f6;
}

.requisitos-password ul {
  list-style: none;
}

.requisitos-password li {
  color: #64748b;
  margin: 4px 0;
}

.requisitos-password li.cumplido {
  color: #10b981;
  font-weight: 500;
}

.input-icon {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon input {
  flex: 1;
  padding-right: 40px;
}

.input-icon span {
  position: absolute;
  right: 12px;
  font-size: 1.2rem;
}
</style>