"""
════════════════════════════════════════════════════════════════════════
SERVICE: SECCIONES - VORTEX
════════════════════════════════════════════════════════════════════════

Lógica de negocio para gestión de secciones del parqueo.

Una sección es una categoría/zona del parqueo (ej: "Autos planta baja",
"Motos", "Camionetas"). Cada sección agrupa espacios de parqueo.

Reglas de negocio:
    - No se puede eliminar una sección que tenga espacios asignados.
"""

from django.db import IntegrityError
from django.db.models import QuerySet

from espacios.models import Seccion
from core.exceptions import (
    SeccionNoEncontradaError,
    SeccionConEspaciosError,
    SeccionInactivaExistenteError,
    DatosInvalidosError,
)


class SeccionService:
    """
    Service de gestión de secciones.
    Encapsula toda la lógica de negocio de secciones.
    """

    # ──────────────────────────────────────────────────────────────────
    # LECTURA
    # ──────────────────────────────────────────────────────────────────

    @staticmethod
   
    def listar() -> QuerySet:
        """Devuelve todas las secciones ACTIVAS ordenadas por nombre."""
        return Seccion.objects.filter(activo=True).order_by('nombre')

    @staticmethod
    def obtener_por_id(seccion_id: int) -> Seccion:
        """
        Busca una sección por ID.

        Lanza:
            SeccionNoEncontradaError: si no existe.
        """
        try:
            return Seccion.objects.get(pk=seccion_id)
        except Seccion.DoesNotExist:
            raise SeccionNoEncontradaError()

    # ──────────────────────────────────────────────────────────────────
    # ESCRITURA
    # ──────────────────────────────────────────────────────────────────

    @staticmethod
    def crear(datos_validados: dict) -> Seccion:
        """
        Crea una nueva sección.

        Lógica especial para soft delete:
            Si ya existe una sección INACTIVA con el mismo nombre, lanza
            SeccionInactivaExistenteError. El frontend ofrecerá reactivarla
            en lugar de crear una nueva, preservando el ID original y los
            vínculos con espacios y registros históricos.

        Lanza:
            SeccionInactivaExistenteError: si hay una sección inactiva con
                                            el mismo nombre.
            DatosInvalidosError: para otros errores de integridad.
        """
        nombre = datos_validados.get('nombre')

        # Verificar si ya existe una sección inactiva con ese mismo nombre
        if nombre:
            existente_inactiva = Seccion.objects.filter(
                nombre=nombre,
                activo=False,
            ).first()

            if existente_inactiva:
                raise SeccionInactivaExistenteError(
                    seccion_id=existente_inactiva.id,
                    nombre=nombre,
                )

        # Crear normalmente
        try:
            return Seccion.objects.create(**datos_validados)
        except IntegrityError:
            raise DatosInvalidosError("Ya existe una sección con ese nombre")

    @staticmethod
    def actualizar(seccion_id: int, datos_validados: dict) -> Seccion:
        """Actualiza una sección existente."""
        seccion = SeccionService.obtener_por_id(seccion_id)

        for campo, valor in datos_validados.items():
            setattr(seccion, campo, valor)

        try:
            seccion.save()
            return seccion
        except IntegrityError:
            raise DatosInvalidosError("Ya existe una sección con ese nombre")

    # ──────────────────────────────────────────────────────────────────
    # ELIMINACIÓN — aquí está la regla de negocio importante
    # ──────────────────────────────────────────────────────────────────

    @staticmethod
    def eliminar(seccion_id: int) -> Seccion:
        """
        Soft delete: marca la sección como inactiva.

        Razón de negocio:
            Las secciones pueden tener espacios y registros históricos asociados.
            Una eliminación física rompería la trazabilidad. Marcando la sección
            como inactiva:
                - Deja de aparecer en el mapa y en los listados.
                - Sus espacios y registros históricos siguen siendo consultables.

        Regla de negocio:
            No se puede desactivar una sección que tenga espacios ACTIVOS asignados.
            Primero hay que desactivar los espacios.

        Lanza:
            SeccionNoEncontradaError
            SeccionConEspaciosError
        """
        seccion = SeccionService.obtener_por_id(seccion_id)

        # Regla: no se puede desactivar si tiene espacios activos
        espacios_activos = seccion.espacios.filter(activo=True).count()
        if espacios_activos > 0:
            raise SeccionConEspaciosError(
                f"No se puede desactivar: la sección tiene {espacios_activos} espacio(s) activo(s). "
                f"Desactiva primero los espacios."
            )

        seccion.activo = False
        seccion.save(update_fields=['activo'])
        return seccion
    
    @staticmethod
    def reactivar(seccion_id: int) -> Seccion:
        """
        Reactiva una sección que había sido soft-deleted.

        Esto preserva el ID original y los vínculos con espacios y
        registros históricos.

        Args:
            seccion_id: ID de la sección inactiva a reactivar.

        Lanza:
            SeccionNoEncontradaError: si la sección no existe.
        """
        seccion = SeccionService.obtener_por_id(seccion_id)

        seccion.activo = True
        seccion.save(update_fields=['activo'])
        return seccion