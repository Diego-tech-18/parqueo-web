"""
════════════════════════════════════════════════════════════════════════
SERVICE: TARIFAS - VORTEX
════════════════════════════════════════════════════════════════════════

Lógica de negocio para la configuración de tarifas del parqueo.

Como Tarifa es un singleton (una sola fila), este service expone:
    - obtener(): leer la configuración actual.
    - actualizar(): modificar los valores aplicando validaciones.

Las validaciones de negocio (valores positivos, horarios coherentes)
viven aquí, no en la view ni en el modelo.
"""

from decimal import Decimal, InvalidOperation

from espacios.models import Tarifa
from core.exceptions import DatosInvalidosError


class TarifaService:
    """
    Service de configuración de tarifas.
    Encapsula lectura, actualización y validaciones de negocio.
    """

    # ──────────────────────────────────────────────────────────────────
    # LECTURA
    # ──────────────────────────────────────────────────────────────────

    @staticmethod
    def obtener() -> Tarifa:
        """
        Devuelve la configuración de tarifas actual.
        Si no existe, se crea con valores por defecto (lo maneja el modelo).
        """
        return Tarifa.obtener()

    # ──────────────────────────────────────────────────────────────────
    # ESCRITURA
    # ──────────────────────────────────────────────────────────────────

    @staticmethod
    def actualizar(datos: dict) -> Tarifa:
        """
        Actualiza la configuración de tarifas aplicando validaciones
        de negocio.

        Args:
            datos: dict con cualquiera de estas claves (todas opcionales,
                   solo se actualiza lo que venga):
                - primera_hora_diurno
                - hora_adicional_diurno
                - primera_hora_nocturno
                - hora_adicional_nocturno
                - hora_inicio_diurno
                - hora_fin_diurno

        Reglas de negocio:
            1. Todos los montos de tarifa deben ser > 0.
            2. Las horas deben estar entre 0 y 23.
            3. hora_inicio_diurno debe ser menor que hora_fin_diurno.

        Lanza:
            DatosInvalidosError: si alguna regla no se cumple.
        """
        tarifa = Tarifa.obtener()

        # Campos de tipo monto (deben ser Decimal > 0)
        campos_monto = [
            'primera_hora_diurno',
            'hora_adicional_diurno',
            'primera_hora_nocturno',
            'hora_adicional_nocturno',
        ]

        # Campos de tipo hora (enteros 0-23)
        campos_hora = [
            'hora_inicio_diurno',
            'hora_fin_diurno',
        ]

        # ── Validar y asignar montos ──
        for campo in campos_monto:
            if campo in datos and datos[campo] is not None:
                valor = TarifaService._validar_monto(campo, datos[campo])
                setattr(tarifa, campo, valor)

        # ── Validar y asignar horas ──
        for campo in campos_hora:
            if campo in datos and datos[campo] is not None:
                valor = TarifaService._validar_hora(campo, datos[campo])
                setattr(tarifa, campo, valor)

        # ── Validación cruzada: inicio < fin ──
        if tarifa.hora_inicio_diurno >= tarifa.hora_fin_diurno:
            raise DatosInvalidosError(
                "La hora de inicio diurno debe ser menor que la hora de fin diurno"
            )

        tarifa.save()
        return tarifa

    # ──────────────────────────────────────────────────────────────────
    # HELPERS PRIVADOS DE VALIDACIÓN
    # ──────────────────────────────────────────────────────────────────

    @staticmethod
    def _validar_monto(nombre_campo: str, valor) -> Decimal:
        """Convierte a Decimal y valida que sea > 0."""
        try:
            decimal_valor = Decimal(str(valor))
        except (InvalidOperation, ValueError, TypeError):
            raise DatosInvalidosError(
                f"El valor de '{nombre_campo}' no es un número válido"
            )

        if decimal_valor <= 0:
            raise DatosInvalidosError(
                f"El valor de '{nombre_campo}' debe ser mayor que 0"
            )

        return decimal_valor

    @staticmethod
    def _validar_hora(nombre_campo: str, valor) -> int:
        """Convierte a entero y valida que esté entre 0 y 23."""
        try:
            entero_valor = int(valor)
        except (ValueError, TypeError):
            raise DatosInvalidosError(
                f"El valor de '{nombre_campo}' debe ser un número entero (0-23)"
            )

        if entero_valor < 0 or entero_valor > 23:
            raise DatosInvalidosError(
                f"El valor de '{nombre_campo}' debe estar entre 0 y 23"
            )

        return entero_valor