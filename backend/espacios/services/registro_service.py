"""
════════════════════════════════════════════════════════════════════════
SERVICE: REGISTROS - VORTEX
════════════════════════════════════════════════════════════════════════

Lógica de negocio del flujo entrada/salida de vehículos.

Operaciones:
    - Registrar entrada (asigna espacio + crea registro + ocupa espacio)
    - Registrar salida (calcula tarifa + libera espacio)
    - Buscar registro activo (por placa o por espacio)
    - Listar historial con filtros

Reglas de negocio aplicadas:
    - Al registrar entrada, el espacio debe estar disponible.
    - Las operaciones de entrada y salida son ATÓMICAS:
      si algo falla, ningún cambio queda en la BD (transaction.atomic).
    - Al registrar salida, se calcula la tarifa según los horarios
      diurno/nocturno (lógica que vive en utils.py — cálculos puros).
"""

from typing import Optional
from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone
from core.exceptions import DatosInvalidosError

from espacios.models import Espacio, Registro
from espacios.utils import (
    determinar_horario_entrada,
    calcular_tarifa,
    calcular_tarifa_actual,
)

from espacios.services.tarifa_service import TarifaService
from core.exceptions import (
    EspacioNoEncontradoError,
    EspacioNoDisponibleError,
    RegistroNoEncontradoError,
    DatosInvalidosError,
)

class _TarifaCongelada:
    """
    Adaptador: reconstruye la estructura de tarifa a partir de la "foto"
    guardada en un Registro. Permite reusar calcular_tarifa() sin cambios.

    Si el registro es viejo y no tiene foto (campos en None), cae de
    vuelta a la tarifa actual del sistema.
    """
    def __init__(self, registro, tarifa_actual_fallback):
        if registro.tarifa_primera_hora_diurno is not None:
            self.primera_hora_diurno = registro.tarifa_primera_hora_diurno
            self.hora_adicional_diurno = registro.tarifa_hora_adicional_diurno
            self.primera_hora_nocturno = registro.tarifa_primera_hora_nocturno
            self.hora_adicional_nocturno = registro.tarifa_hora_adicional_nocturno
            self.hora_inicio_diurno = registro.tarifa_hora_inicio_diurno
            self.hora_fin_diurno = registro.tarifa_hora_fin_diurno
        else:
            # Registro antiguo sin foto: usar la tarifa actual
            self.primera_hora_diurno = tarifa_actual_fallback.primera_hora_diurno
            self.hora_adicional_diurno = tarifa_actual_fallback.hora_adicional_diurno
            self.primera_hora_nocturno = tarifa_actual_fallback.primera_hora_nocturno
            self.hora_adicional_nocturno = tarifa_actual_fallback.hora_adicional_nocturno
            self.hora_inicio_diurno = tarifa_actual_fallback.hora_inicio_diurno
            self.hora_fin_diurno = tarifa_actual_fallback.hora_fin_diurno

class RegistroService:
    """
    Service de gestión de registros (entradas y salidas de vehículos).
    Encapsula toda la lógica de negocio del flujo del parqueo.
    """

    # ──────────────────────────────────────────────────────────────────
    # REGISTRAR ENTRADA
    # ──────────────────────────────────────────────────────────────────

    @staticmethod
    @transaction.atomic
    def registrar_entrada(datos_validados: dict) -> Registro:
        """
        Registra la entrada de un vehículo.

        Pasos:
            1. Buscar el espacio.
            2. Validar que el espacio esté libre (regla de negocio).
            3. Determinar el horario (DIURNO / NOCTURNO).
            4. Crear el registro.
            5. Marcar el espacio como OCUPADO.

        El decorador @transaction.atomic garantiza que TODOS los pasos
        ocurran o NINGUNO. Si algo falla a mitad de camino, la BD
        queda como estaba antes.

        Args:
            datos_validados: dict del serializer con placa, tipo_vehiculo,
                             espacio (id), notas (opcional).

        Returns:
            Registro creado.

        Lanza:
            EspacioNoEncontradoError
            EspacioNoDisponibleError
        """
        placa = datos_validados['placa']
        tipo_vehiculo = datos_validados['tipo_vehiculo']
        espacio_id = datos_validados['espacio']
        notas = datos_validados.get('notas', '')

        # 1. Buscar el espacio
        try:
            espacio = Espacio.objects.get(pk=espacio_id)
        except Espacio.DoesNotExist:
            raise EspacioNoEncontradoError()

        # 2. Validar disponibilidad (regla de negocio NUEVA y necesaria)
        if espacio.estado != 'LIBRE':
            raise EspacioNoDisponibleError(
                f"El espacio {espacio.numero} no está disponible (estado: {espacio.estado})"
            )

        # 3. Determinar horario según la hora actual
        fecha_entrada = timezone.now()
        horario = determinar_horario_entrada(fecha_entrada)

        # 4. Crear el registro
       # 4. Obtener la tarifa vigente AHORA y "congelarla" en el registro.
        #    Así, si el admin cambia la tarifa mientras el vehículo está
        #    dentro, este registro conserva la tarifa con la que entró.
        tarifa_actual = TarifaService.obtener()

        registro = Registro.objects.create(
            espacio=espacio,
            placa=placa,
            tipo_vehiculo=tipo_vehiculo,
            horario_entrada=horario,
            estado='EN_CURSO',
            notas=notas,
            # Foto de la tarifa al momento de entrar
            tarifa_primera_hora_diurno=tarifa_actual.primera_hora_diurno,
            tarifa_hora_adicional_diurno=tarifa_actual.hora_adicional_diurno,
            tarifa_primera_hora_nocturno=tarifa_actual.primera_hora_nocturno,
            tarifa_hora_adicional_nocturno=tarifa_actual.hora_adicional_nocturno,
            tarifa_hora_inicio_diurno=tarifa_actual.hora_inicio_diurno,
            tarifa_hora_fin_diurno=tarifa_actual.hora_fin_diurno,
        )
        # 5. Marcar el espacio como ocupado
        espacio.marcar_ocupado()

        return registro

    # ──────────────────────────────────────────────────────────────────
    # REGISTRAR SALIDA
    # ──────────────────────────────────────────────────────────────────

    @staticmethod
    @transaction.atomic
    def registrar_salida(datos_validados: dict) -> Registro:
        """
        Registra la salida de un vehículo.

        Pasos:
            1. Encontrar el registro activo (por placa o por registro_id).
            2. Calcular tarifa y tiempo en parqueo.
            3. Actualizar el registro (fecha_salida, tarifa, estado FINALIZADO).
            4. Liberar el espacio (marcar_libre).

        Args:
            datos_validados: dict del serializer con placa o registro_id,
                             y notas opcional.

        Returns:
            Registro actualizado.

        Lanza:
            DatosInvalidosError: si no se proporciona placa ni registro_id.
            RegistroNoEncontradoError: si no hay registro activo.
        """
        placa = datos_validados.get('placa')
        registro_id = datos_validados.get('registro_id')
        notas_salida = datos_validados.get('notas', '')

        # 1. Buscar el registro activo
        registro = RegistroService._buscar_registro_activo(
            placa=placa,
            registro_id=registro_id,
        )

        # 2. Calcular tarifa
        # 2. Calcular la tarifa
        fecha_salida = timezone.now()

        if registro.tipo_vehiculo == 'MOTO':
            # ── MOTO: cobro MANUAL ──
            # El operador escribe el monto. Viene en datos_validados['monto_manual'].
            monto_manual = datos_validados.get('monto_manual')
            if monto_manual is None:
                raise DatosInvalidosError(
                    "Para una moto debe ingresar el monto a cobrar manualmente"
                )
            try:
                tarifa = Decimal(str(monto_manual))
            except (InvalidOperation, ValueError, TypeError):
                raise DatosInvalidosError("El monto ingresado no es válido")

            if tarifa < 0:
                raise DatosInvalidosError("El monto no puede ser negativo")

            # Tiempo transcurrido (informativo)
            delta = fecha_salida - registro.fecha_entrada
            tiempo_minutos = int(delta.total_seconds() / 60)
        else:
            # ── AUTO (y otros): cálculo AUTOMÁTICO con tarifa congelada ──
            tarifa_actual = TarifaService.obtener()
            tarifa_congelada = _TarifaCongelada(registro, tarifa_actual)
            tarifa, tiempo_minutos = calcular_tarifa(
                registro.fecha_entrada,
                fecha_salida,
                tarifa_congelada,
            )

        # 3. Actualizar el registro
        registro.fecha_salida = fecha_salida
        registro.tarifa = tarifa
        registro.tiempo_minutos = tiempo_minutos
        registro.estado = 'FINALIZADO'

        if notas_salida:
            registro.notas = f"{registro.notas}\nSalida: {notas_salida}"

        registro.save(update_fields=[
            'fecha_salida',
            'tarifa',
            'tiempo_minutos',
            'estado',
            'notas',
            'actualizado_en',
        ])

        # 4. Liberar el espacio
        registro.espacio.marcar_libre()

        return registro

    # ──────────────────────────────────────────────────────────────────
    # BUSCAR REGISTRO ACTIVO (con tarifa estimada en vivo)
    # ──────────────────────────────────────────────────────────────────

    @staticmethod
    def buscar_activo_con_tarifa(
        placa: Optional[str] = None,
        espacio_id: Optional[int] = None,
    ) -> dict:
        """
        Busca un registro activo y devuelve sus datos + tarifa estimada
        al momento actual (sin registrar salida — solo preview).

        Args:
            placa: placa del vehículo (opcional).
            espacio_id: id del espacio (opcional).

        Returns:
            dict con el registro y los campos extra:
                - tarifa_estimada
                - tiempo_minutos_actual

        Lanza:
            DatosInvalidosError: si no se proporciona ni placa ni espacio.
            RegistroNoEncontradoError: si no hay registro activo.
        """
        if not placa and not espacio_id:
            raise DatosInvalidosError("Debe proporcionar placa o espacio")

        # Buscar registro con sus relaciones precargadas
        query = Registro.objects.select_related('espacio', 'espacio__seccion')

        try:
            if placa:
                registro = query.get(placa__iexact=placa, estado='EN_CURSO')
            else:
                registro = query.get(espacio_id=espacio_id, estado='EN_CURSO')
        except Registro.DoesNotExist:
            raise RegistroNoEncontradoError()

        # Calcular tarifa estimada actual
        
        if registro.tipo_vehiculo == 'MOTO':
            # Moto: no se estima, se define a la salida manualmente
            return {
                'registro': registro,
                'tarifa_estimada': None,
                'tarifa_estimada_texto': 'Tarifa manual — se define a la salida',
                'tiempo_minutos_actual': RegistroService._minutos_desde(registro.fecha_entrada),
            }

        tarifa_actual = TarifaService.obtener()
        tarifa_congelada = _TarifaCongelada(registro, tarifa_actual)
        tarifa_estimada, tiempo_minutos = calcular_tarifa_actual(
            registro.fecha_entrada,
            tarifa_congelada,
        )

        return {
            'registro': registro,
            'tarifa_estimada': tarifa_estimada,
            'tarifa_estimada_texto': None,
            'tiempo_minutos_actual': tiempo_minutos,
        }

    # ──────────────────────────────────────────────────────────────────
    # HISTORIAL CON FILTROS
    # ──────────────────────────────────────────────────────────────────

    @staticmethod
    def listar_historial(filtros: dict) -> QuerySet:
        """
        Lista registros con filtros opcionales.

        Args:
            filtros: dict con cualquiera de estas claves (todas opcionales):
                - estado: 'EN_CURSO' | 'FINALIZADO'
                - fecha_desde: fecha mínima de entrada
                - fecha_hasta: fecha máxima de entrada
                - placa: búsqueda parcial (icontains)

        Returns:
            QuerySet de registros ordenado por fecha_entrada descendente.
        """
        registros = Registro.objects.select_related(
            'espacio',
            'espacio__seccion',
        ).all()

        if filtros.get('estado'):
            registros = registros.filter(estado=filtros['estado'])

        if filtros.get('fecha_desde'):
            registros = registros.filter(fecha_entrada__gte=filtros['fecha_desde'])

        if filtros.get('fecha_hasta'):
            registros = registros.filter(fecha_entrada__lte=filtros['fecha_hasta'])

        if filtros.get('placa'):
            registros = registros.filter(placa__icontains=filtros['placa'])

        return registros.order_by('-fecha_entrada')

    # ──────────────────────────────────────────────────────────────────
    # HELPERS PRIVADOS
    # ──────────────────────────────────────────────────────────────────

    @staticmethod
    def _buscar_registro_activo(
        placa: Optional[str] = None,
        registro_id: Optional[int] = None,
    ) -> Registro:
        """
        Helper: busca un registro EN_CURSO por placa o por id.
        Uso interno del service.

        Lanza:
            DatosInvalidosError: si no se proporciona ni placa ni id.
            RegistroNoEncontradoError: si no existe.
        """
        if not placa and not registro_id:
            raise DatosInvalidosError("Debe proporcionar placa o registro_id")

        try:
            if registro_id:
                return Registro.objects.get(pk=registro_id, estado='EN_CURSO')
            return Registro.objects.get(placa__iexact=placa, estado='EN_CURSO')
        except Registro.DoesNotExist:
            raise RegistroNoEncontradoError()
        

    @staticmethod
    def _minutos_desde(fecha_entrada):
        """Minutos transcurridos desde fecha_entrada hasta ahora."""
        delta = timezone.now() - fecha_entrada
        return int(delta.total_seconds() / 60)