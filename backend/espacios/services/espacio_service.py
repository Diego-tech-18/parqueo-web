"""
════════════════════════════════════════════════════════════════════════
SERVICE: ESPACIOS - VORTEX
════════════════════════════════════════════════════════════════════════

Lógica de negocio para gestión de espacios individuales del parqueo.

Operaciones:
    - Listar (con filtro opcional por sección)
    - Obtener por ID
    - Crear / Actualizar / Eliminar
    - Cambiar estado (LIBRE / OCUPADO / MANTENIMIENTO)
    - Mapa consolidado (secciones + sus espacios + estadísticas)
"""

from typing import Optional
from django.db import IntegrityError
from django.db.models import QuerySet

from espacios.models import Espacio, Seccion
from core.exceptions import (
    EspacioNoEncontradoError,
    EspacioInactivoExistenteError,
    DatosInvalidosError,
)


class EspacioService:
    """
    Service de gestión de espacios.
    Encapsula toda la lógica de negocio de espacios.
    """

    # ──────────────────────────────────────────────────────────────────
    # LECTURA
    # ──────────────────────────────────────────────────────────────────

    @staticmethod
    @staticmethod
    def listar(seccion_id: Optional[int] = None) -> QuerySet:
        """
        Devuelve todos los espacios ACTIVOS, opcionalmente filtrados por sección.
        Los espacios inactivos (soft-deleted) no aparecen en los listados,
        pero sus registros históricos siguen siendo consultables.
        """
        espacios = Espacio.objects.select_related('seccion').filter(activo=True)

        if seccion_id is not None:
            espacios = espacios.filter(seccion_id=seccion_id)

        return espacios.order_by('seccion__nombre', 'numero')

    @staticmethod
    def obtener_por_id(espacio_id: int) -> Espacio:
        """
        Busca un espacio por ID con su sección precargada.

        Lanza:
            EspacioNoEncontradoError: si no existe.
        """
        try:
            return Espacio.objects.select_related('seccion').get(pk=espacio_id)
        except Espacio.DoesNotExist:
            raise EspacioNoEncontradoError()

    # ──────────────────────────────────────────────────────────────────
    # ESCRITURA
    # ──────────────────────────────────────────────────────────────────
    @staticmethod
    def crear(datos_validados: dict) -> Espacio:
        """
        Crea un nuevo espacio.

        Lógica especial para soft delete:
            Si ya existe un espacio INACTIVO con el mismo número, lanza
            EspacioInactivoExistenteError. El frontend ofrecerá reactivar
            ese espacio en lugar de crear uno nuevo, preservando el ID
            original y los vínculos con registros históricos.

        Lanza:
            EspacioInactivoExistenteError: si hay un espacio inactivo con
                                            el mismo número.
            DatosInvalidosError: para otros errores de integridad.
        """
        numero = datos_validados.get('numero')

        # Verificar si ya existe un espacio inactivo con ese mismo número
        if numero:
            existente_inactivo = Espacio.objects.filter(
                numero=numero,
                activo=False,
            ).first()

            if existente_inactivo:
                raise EspacioInactivoExistenteError(
                    espacio_id=existente_inactivo.id,
                    numero=numero,
                )

        # Crear normalmente
        try:
            return Espacio.objects.create(**datos_validados)
        except IntegrityError as e:
            raise DatosInvalidosError(f"No se puede crear el espacio: {str(e)}")

   
    @staticmethod
    def actualizar(espacio_id: int, datos_validados: dict) -> Espacio:
        """Actualiza un espacio existente."""
        espacio = EspacioService.obtener_por_id(espacio_id)

        for campo, valor in datos_validados.items():
            setattr(espacio, campo, valor)

        try:
            espacio.save()
            return espacio
        except IntegrityError as e:
            raise DatosInvalidosError(f"No se puede actualizar el espacio: {str(e)}")
        

    @staticmethod
    def eliminar(espacio_id: int) -> Espacio:
        """
        Soft delete: marca el espacio como inactivo en lugar de eliminarlo
        físicamente.

        Razón de negocio:
            Los espacios pueden tener registros históricos (entradas/salidas)
            asociados. Una eliminación física rompería la trazabilidad de
            operaciones pasadas. Marcando el espacio como inactivo:
                - Deja de aparecer en el mapa y en los listados.
                - No se puede asignar a nuevas entradas.
                - Sus registros históricos siguen siendo consultables.

        Lanza:
            EspacioNoEncontradoError
        """
        espacio = EspacioService.obtener_por_id(espacio_id)

        espacio.activo = False
        espacio.save(update_fields=['activo'])
        return espacio

    @staticmethod
    def reactivar(espacio_id: int) -> Espacio:
        """
        Reactiva un espacio que había sido soft-deleted.

        Esto preserva el ID original y los vínculos con registros
        históricos. El espacio vuelve al mapa con estado LIBRE.

        Args:
            espacio_id: ID del espacio inactivo a reactivar.

        Lanza:
            EspacioNoEncontradoError: si el espacio no existe.
        """
        espacio = EspacioService.obtener_por_id(espacio_id)

        espacio.activo = True
        espacio.estado = 'LIBRE'  # se reactiva siempre disponible
        espacio.save(update_fields=['activo', 'estado'])
        return espacio
    # ──────────────────────────────────────────────────────────────────
    # CAMBIAR ESTADO
    # ──────────────────────────────────────────────────────────────────

    @staticmethod
    def cambiar_estado(espacio_id: int, nuevo_estado: str, notas: str = '') -> Espacio:
        """
        Cambia el estado de un espacio (LIBRE / OCUPADO / MANTENIMIENTO).

        Args:
            espacio_id: ID del espacio.
            nuevo_estado: nuevo estado (ya validado por el serializer).
            notas: notas opcionales sobre el cambio.

        Lanza:
            EspacioNoEncontradoError
        """
        espacio = EspacioService.obtener_por_id(espacio_id)

        espacio.estado = nuevo_estado
        if notas:
            espacio.notas = notas

        espacio.save(update_fields=['estado', 'notas'])
        return espacio

    # ──────────────────────────────────────────────────────────────────
    # MAPA DEL PARQUEO
    # ──────────────────────────────────────────────────────────────────

    @staticmethod
    def obtener_mapa() -> list:
        """
        Devuelve la estructura completa del mapa del parqueo:
        todas las secciones activas con sus espacios activos y estadísticas.

        Usa prefetch_related para evitar consultas N+1.

        Returns:
            Lista de dicts. Cada dict representa una sección con:
                - datos de la sección
                - estadísticas (total, libres, ocupados)
                - lista de sus espacios
        """
        secciones = (
            Seccion.objects
            .filter(activo=True)
            .prefetch_related('espacios')
            .order_by('nombre')
        )

        return [
            EspacioService._serializar_seccion_para_mapa(seccion)
            for seccion in secciones
        ]

    @staticmethod
    def _serializar_seccion_para_mapa(seccion: Seccion) -> dict:
        """
        Helper privado: arma el dict de una sección para el mapa.
        El guion bajo al inicio indica que es uso interno del service.
        """
        espacios_activos = [e for e in seccion.espacios.all() if e.activo]

        return {
            'id': seccion.id,
            'nombre': seccion.nombre,
            'tipo': seccion.tipo,
            'descripcion': seccion.descripcion,
            'activo': seccion.activo,
            'total_espacios': len(espacios_activos),
            'espacios_libres': sum(1 for e in espacios_activos if e.estado == 'LIBRE'),
            'espacios_ocupados': sum(1 for e in espacios_activos if e.estado == 'OCUPADO'),
            'creado_en': seccion.creado_en,
            'actualizado_en': seccion.actualizado_en,
            'espacios': [
                {
                    'id': e.id,
                    'numero': e.numero,
                    'seccion': e.seccion_id,
                    'seccion_nombre': seccion.nombre,
                    'seccion_tipo': seccion.tipo,
                    'estado': e.estado,
                    'posicion_fila': e.posicion_fila,
                    'posicion_columna': e.posicion_columna,
                    'activo': e.activo,
                    'notas': e.notas,
                    'esta_libre': e.estado == 'LIBRE' and e.activo,
                    'esta_ocupado': e.estado == 'OCUPADO',
                    'creado_en': e.creado_en,
                    'actualizado_en': e.actualizado_en,
                }
                for e in espacios_activos
            ],
        }