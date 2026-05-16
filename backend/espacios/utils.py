"""
════════════════════════════════════════════════════════════════════════
UTILIDADES: CÁLCULO DE TARIFAS - VORTEX
════════════════════════════════════════════════════════════════════════

FUNCIONES PURAS de cálculo de tarifa.

"Pura" significa: reciben todos los datos como parámetros (incluida la
configuración de tarifas) y no acceden a la base de datos ni a variables
globales. Esto las hace testeables de forma aislada y respeta la
separación de capas (el acceso a datos lo hace el RegistroService).

Reglas de negocio:
- Franja DIURNA  : desde hora_inicio_diurno hasta hora_fin_diurno (inclusive).
                   Ej: 6 a 18 → diurno es 06:00:00 a 18:59:59.
- Franja NOCTURNA: el resto (ej: 19:00:00 a 05:59:59).
- La "primera hora" ocurre UNA sola vez; su precio depende de la franja
  en la que el vehículo ENTRÓ.
- Las horas siguientes son "adicionales"; cada una se cobra según la
  franja en la que transcurre esa hora.
- Las fracciones de hora se cobran de forma PROPORCIONAL (no se redondea
  hacia arriba). Ej: media hora de primera hora diurna = 9 / 2 = 4.50.
"""

from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

# Zona horaria de Bolivia (UTC-4)
ZONA_BOLIVIA = ZoneInfo('America/La_Paz')


# ══════════════════════════════════════════════════════════════════════
# HELPERS DE FRANJA HORARIA
# ══════════════════════════════════════════════════════════════════════

def es_horario_diurno(momento, hora_inicio_diurno, hora_fin_diurno):
    """
    Determina si un datetime cae en franja diurna.

    Diurno = la hora del día está entre hora_inicio_diurno y
    hora_fin_diurno, AMBOS inclusive.
    Ej: inicio=6, fin=18 → diurno si la hora es 6,7,...,18
        (es decir 06:00:00 hasta 18:59:59).

    Args:
        momento: datetime (en hora local).
        hora_inicio_diurno: int 0-23.
        hora_fin_diurno: int 0-23.

    Returns:
        bool: True si es diurno, False si es nocturno.
    """
    hora = momento.hour
    return hora_inicio_diurno <= hora <= hora_fin_diurno


def determinar_horario_entrada(fecha_entrada, hora_inicio_diurno=6, hora_fin_diurno=18):
    """
    Devuelve 'DIURNO' o 'NOCTURNO' según la hora de entrada.
    Se usa para guardar el horario de entrada en el registro.

    Los valores por defecto (6, 18) son solo un fallback; en uso real
    se pasan los valores configurados de la tarifa.
    """
    entrada_local = _a_hora_local(fecha_entrada)
    es_diurno = es_horario_diurno(entrada_local, hora_inicio_diurno, hora_fin_diurno)
    return 'DIURNO' if es_diurno else 'NOCTURNO'


# ══════════════════════════════════════════════════════════════════════
# CÁLCULO PRINCIPAL
# ══════════════════════════════════════════════════════════════════════

def calcular_tarifa(fecha_entrada, fecha_salida, tarifa):
    """
    Calcula la tarifa total de un estacionamiento.

    FUNCIÓN PURA: recibe la configuración de tarifas como parámetro.
    No accede a la base de datos.

    Regla de cobro (bloques de media hora):
        Cada bloque de hora se cobra así:
            - 1 a 30 minutos  → MITAD de la tarifa del bloque
            - 31 a 60 minutos → tarifa COMPLETA del bloque
        Aplica igual a la primera hora y a las horas adicionales.

    Args:
        fecha_entrada: datetime de entrada.
        fecha_salida: datetime de salida.
        tarifa: objeto con atributos primera_hora_diurno,
                hora_adicional_diurno, primera_hora_nocturno,
                hora_adicional_nocturno, hora_inicio_diurno,
                hora_fin_diurno.

    Returns:
        tuple: (tarifa_total: Decimal, minutos_totales: int)
    """
    # 1. Pasar ambas fechas a hora local de Bolivia
    entrada_local = _a_hora_local(fecha_entrada)
    salida_local = _a_hora_local(fecha_salida)

    # 2. Tiempo total real en minutos (esto se guarda en el registro)
    delta = salida_local - entrada_local
    minutos_totales = int(delta.total_seconds() / 60)

    # Mínimo 1 minuto (evita cobros en 0 por dobles clics)
    if minutos_totales < 1:
        minutos_totales = 1

    # 3. Determinar franja de ENTRADA (define el precio de la 1ra hora)
    entro_en_diurno = es_horario_diurno(
        entrada_local,
        tarifa.hora_inicio_diurno,
        tarifa.hora_fin_diurno,
    )
    precio_primera_hora = (
        Decimal(str(tarifa.primera_hora_diurno))
        if entro_en_diurno
        else Decimal(str(tarifa.primera_hora_nocturno))
    )

    # 4. Recorrer el tiempo en bloques de 1 hora (y el bloque final parcial)
    tarifa_total = Decimal('0.00')
    minutos_restantes = minutos_totales
    momento_actual = entrada_local
    es_primera_hora = True

    while minutos_restantes > 0:
        # Minutos que abarca este bloque (máx 60)
        minutos_bloque = min(60, minutos_restantes)

        # ── Factor según regla de media hora ──
        #   1-30 min  → 0.5 (mitad)
        #   31-60 min → 1.0 (completo)
        if minutos_bloque <= 30:
            factor = Decimal('0.5')
        else:
            factor = Decimal('1.0')

        # ── Precio base de este bloque ──
        if es_primera_hora:
            precio_base = precio_primera_hora
            es_primera_hora = False
        else:
            # Hora adicional: precio según la franja donde transcurre
            es_diurno_bloque = es_horario_diurno(
                momento_actual,
                tarifa.hora_inicio_diurno,
                tarifa.hora_fin_diurno,
            )
            if es_diurno_bloque:
                precio_base = Decimal(str(tarifa.hora_adicional_diurno))
            else:
                precio_base = Decimal(str(tarifa.hora_adicional_nocturno))

        tarifa_total += precio_base * factor

        # Avanzar al siguiente bloque
        minutos_restantes -= minutos_bloque
        momento_actual += timedelta(minutes=minutos_bloque)

    # 5. Redondear a 2 decimales
    tarifa_total = tarifa_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    return (tarifa_total, minutos_totales)


def calcular_tarifa_actual(fecha_entrada, tarifa):
    """
    Calcula cuánto se cobraría si el vehículo saliera AHORA.
    Útil para mostrar la tarifa estimada en vivo.

    FUNCIÓN PURA: también recibe la tarifa como parámetro.

    Args:
        fecha_entrada: datetime de entrada.
        tarifa: misma estructura que en calcular_tarifa().

    Returns:
        tuple: (tarifa_estimada: Decimal, minutos_transcurridos: int)
    """
    from django.utils import timezone
    return calcular_tarifa(fecha_entrada, timezone.now(), tarifa)


# ══════════════════════════════════════════════════════════════════════
# HELPER PRIVADO
# ══════════════════════════════════════════════════════════════════════

def _a_hora_local(fecha):
    """
    Convierte un datetime a hora local de Bolivia.
    Si el datetime no tiene zona horaria (naive), se devuelve tal cual.
    """
    if fecha.tzinfo is not None:
        return fecha.astimezone(ZONA_BOLIVIA)
    return fecha