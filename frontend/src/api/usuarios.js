import api from './auth.js'

// Obtener todos los usuarios → GET /api/usuarios/
export const getUsuarios     = ()          => api.get('/usuarios/')

// Crear usuario → POST /api/usuarios/
export const crearUsuario    = (datos)     => api.post('/usuarios/', datos)

// Editar usuario → PUT /api/usuarios/:id/
export const editarUsuario   = (id, datos) => api.put(`/usuarios/${id}/`, datos)

// Eliminar usuario → DELETE /api/usuarios/:id/
export const eliminarUsuario = (id)        => api.delete(`/usuarios/${id}/`)