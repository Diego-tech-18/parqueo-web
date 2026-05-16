"""
════════════════════════════════════════════════════════════════════════
EXCEPCIONES DE DOMINIO - VORTEX
════════════════════════════════════════════════════════════════════════

Excepciones personalizadas que lanzan los services cuando ocurre un
error de negocio. Las views las capturan y las traducen a códigos HTTP.

Ventajas:
- Los services no dependen de Django REST Framework.
- Los services son testeables sin HTTP.
- Las views quedan delgadas: solo traducen excepción → código HTTP.
"""


# ══════════════════════════════════════════════════════════════════════
# CLASE BASE
# ══════════════════════════════════════════════════════════════════════

class DominioError(Exception):
    """
    Clase base para todas las excepciones de negocio.
    Toda excepción de dominio hereda de aquí.
    """
    mensaje_default = "Ocurrió un error en la operación"

    def __init__(self, mensaje: str = None):
        self.mensaje = mensaje or self.mensaje_default
        super().__init__(self.mensaje)


# ══════════════════════════════════════════════════════════════════════
# ERRORES GENÉRICOS (404, 400, 409)
# ══════════════════════════════════════════════════════════════════════

class RecursoNoEncontradoError(DominioError):
    """El recurso solicitado no existe en la BD. → HTTP 404"""
    mensaje_default = "Recurso no encontrado"


class DatosInvalidosError(DominioError):
    """Los datos enviados no pasan validaciones de negocio. → HTTP 400"""
    mensaje_default = "Datos inválidos"


class ConflictoError(DominioError):
    """La operación viola una regla de negocio. → HTTP 409 o 400"""
    mensaje_default = "La operación no se puede completar"


class NoAutorizadoError(DominioError):
    """El usuario no tiene permisos para esta operación. → HTTP 403"""
    mensaje_default = "No autorizado"


# ══════════════════════════════════════════════════════════════════════
# ERRORES ESPECÍFICOS DE USUARIOS
# ══════════════════════════════════════════════════════════════════════

class UsuarioNoEncontradoError(RecursoNoEncontradoError):
    mensaje_default = "Usuario no encontrado"


class CredencialesInvalidasError(DominioError):
    """Email o contraseña incorrectos. → HTTP 401"""
    mensaje_default = "Email o contraseña incorrectos"


class UsuarioInactivoError(DominioError):
    """El usuario existe pero está desactivado. → HTTP 403"""
    mensaje_default = "Usuario inactivo, contacte al administrador"


class UltimoAdministradorError(ConflictoError):
    """No se puede desactivar al último administrador del sistema."""
    mensaje_default = "No puedes desactivar al último administrador del sistema"


class AutoDesactivacionError(ConflictoError):
    """Un usuario no puede desactivarse a sí mismo."""
    mensaje_default = "No puedes desactivar tu propia cuenta"


# ══════════════════════════════════════════════════════════════════════
# ERRORES ESPECÍFICOS DE ESPACIOS / SECCIONES / REGISTROS
# (los usaremos cuando refactoricemos espacios)
# ══════════════════════════════════════════════════════════════════════

class SeccionNoEncontradaError(RecursoNoEncontradoError):
    mensaje_default = "Sección no encontrada"


class SeccionConEspaciosError(ConflictoError):
    mensaje_default = "No se puede eliminar una sección con espacios asignados"


class EspacioNoEncontradoError(RecursoNoEncontradoError):
    mensaje_default = "Espacio no encontrado"


class EspacioOcupadoError(ConflictoError):
    mensaje_default = "El espacio ya está ocupado"


class EspacioNoDisponibleError(ConflictoError):
    mensaje_default = "El espacio no está disponible"


class RegistroNoEncontradoError(RecursoNoEncontradoError):
    mensaje_default = "No se encontró un registro activo"

class EspacioInactivoExistenteError(ConflictoError):
    """
    Ya existe un espacio inactivo con el mismo número.
    El admin debe decidir si reactivarlo o usar otro número.

    Lleva atributos extra (espacio_id, numero) para que el frontend
    sepa qué espacio reactivar.
    """
    mensaje_default = "Ya existe un espacio inactivo con ese número"

    def __init__(self, espacio_id: int, numero: str):
        self.espacio_id = espacio_id
        self.numero = numero
        mensaje = (
            f"Ya existe un espacio inactivo con el número '{numero}'. "
            f"¿Deseas reactivarlo en lugar de crear uno nuevo?"
        )
        super().__init__(mensaje)

class SeccionInactivaExistenteError(ConflictoError):
    """
    Ya existe una sección inactiva con el mismo nombre.
    El admin debe decidir si reactivarla o usar otro nombre.
    """
    mensaje_default = "Ya existe una sección inactiva con ese nombre"

    def __init__(self, seccion_id: int, nombre: str):
        self.seccion_id = seccion_id
        self.nombre = nombre
        mensaje = (
            f"Ya existe una sección inactiva con el nombre '{nombre}'. "
            f"¿Deseas reactivarla en lugar de crear una nueva?"
        )
        super().__init__(mensaje)