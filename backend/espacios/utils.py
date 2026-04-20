"""
════════════════════════════════════════════════════════════════════════
UTILIDADES: CÁLCULO DE TARIFAS - VORTEX
════════════════════════════════════════════════════════════════════════

Sistema de tarifas:
- DIURNO (06:00 - 18:00): Primera hora Bs. 9, adicionales Bs. 2/hora
- NOCTURNO (19:00 - 05:59): Bs. 5/hora
"""

from datetime import datetime, time, timedelta
from decimal import Decimal
import math


# ══════════════════════════════════════════════════════════════════════════
# CONSTANTES DE TARIFAS
# ══════════════════════════════════════════════════════════════════════════

TARIFA_DIURNA_PRIMERA = Decimal('9.00')    # Primera hora diurna
TARIFA_DIURNA_ADICIONAL = Decimal('2.00')  # Horas adicionales diurnas
TARIFA_NOCTURNA = Decimal('5.00')          # Por hora nocturna

HORA_INICIO_DIURNO = time(6, 0)   # 06:00
HORA_FIN_DIURNO = time(18, 0)     # 18:00


# ══════════════════════════════════════════════════════════════════════════
# FUNCIONES
# ══════════════════════════════════════════════════════════════════════════

def es_horario_diurno(hora_datetime):
    """
    Verifica si una hora está en horario diurno (06:00 - 18:00)
    
    Args:
        hora_datetime: datetime object
    
    Returns:
        bool: True si es horario diurno, False si es nocturno
    """
    hora = hora_datetime.time()
    return HORA_INICIO_DIURNO <= hora < HORA_FIN_DIURNO


def determinar_horario_entrada(fecha_entrada):
    """
    Determina si la entrada fue en horario diurno o nocturno
    
    Returns:
        str: 'DIURNO' o 'NOCTURNO'
    """
    return 'DIURNO' if es_horario_diurno(fecha_entrada) else 'NOCTURNO'

def calcular_tarifa(fecha_entrada, fecha_salida):
    """
    Calcula la tarifa total basada en entrada y salida
    
    Sistema:
    - DIURNO (06:00-18:00): 1ra hora Bs. 9, adicionales Bs. 2/hora
    - NOCTURNO (19:00-05:59): Bs. 5/hora
    """
    from zoneinfo import ZoneInfo
    
    # Convertir UTC a hora local de Bolivia (UTC-4)
    zona_bolivia = ZoneInfo('America/La_Paz')
    
    # Si las fechas vienen en UTC, convertirlas a hora local
    if fecha_entrada.tzinfo is not None:
        entrada_local = fecha_entrada.astimezone(zona_bolivia)
    else:
        entrada_local = fecha_entrada
    
    if fecha_salida.tzinfo is not None:
        salida_local = fecha_salida.astimezone(zona_bolivia)
    else:
        salida_local = fecha_salida
    
    # DEBUG
    print(f"\n=== DEBUG TARIFA ===")
    print(f"Entrada UTC: {fecha_entrada}")
    print(f"Entrada Local (Bolivia): {entrada_local}")
    print(f"Salida UTC: {fecha_salida}")
    print(f"Salida Local (Bolivia): {salida_local}")
    
    # Calcular tiempo total
    delta = salida_local - entrada_local
    minutos_totales = int(delta.total_seconds() / 60)
    
    print(f"Minutos totales: {minutos_totales}")
    
    # Si es menos de 1 minuto, cobrar mínimo de 1 hora
    if minutos_totales < 1:
        minutos_totales = 1
    
    # Convertir minutos a horas (redondeando hacia arriba)
    horas_totales = math.ceil(minutos_totales / 60)
    
    print(f"Horas totales (redondeadas): {horas_totales}")
    
    # Dividir el tiempo en franjas horarias
    horas_diurnas = 0
    horas_nocturnas = 0
    
    # Recorrer hora por hora desde entrada LOCAL
    hora_actual = entrada_local
    
    for i in range(horas_totales):
        es_diurno = es_horario_diurno(hora_actual)
        print(f"Hora {i+1}: {hora_actual.strftime('%H:%M')} - {'DIURNO' if es_diurno else 'NOCTURNO'}")
        
        if es_diurno:
            horas_diurnas += 1
        else:
            horas_nocturnas += 1
        
        # Avanzar 1 hora
        hora_actual += timedelta(hours=1)
    
    print(f"Horas diurnas: {horas_diurnas}")
    print(f"Horas nocturnas: {horas_nocturnas}")
    
    # Calcular tarifa diurna
    if horas_diurnas > 0:
        # Primera hora diurna: Bs. 9
        tarifa_diurna = TARIFA_DIURNA_PRIMERA
        print(f"Tarifa primera hora diurna: {tarifa_diurna}")
        
        # Horas adicionales diurnas: Bs. 2 c/u
        if horas_diurnas > 1:
            adicional = (horas_diurnas - 1) * TARIFA_DIURNA_ADICIONAL
            print(f"Tarifa adicional diurna: {adicional}")
            tarifa_diurna += adicional
    else:
        tarifa_diurna = Decimal('0.00')
    
    # Calcular tarifa nocturna
    tarifa_nocturna = horas_nocturnas * TARIFA_NOCTURNA
    print(f"Tarifa nocturna: {tarifa_nocturna}")
    
    # Tarifa total
    tarifa_total = tarifa_diurna + tarifa_nocturna
    print(f"TARIFA TOTAL: {tarifa_total}")
    print(f"===================\n")
    
    return (tarifa_total, minutos_totales)


def calcular_tarifa_actual(fecha_entrada):
    """
    Calcula la tarifa si el vehículo saliera AHORA
    Útil para mostrar estimado antes de confirmar salida
    
    Args:
        fecha_entrada: datetime - Hora de entrada
    
    Returns:
        tuple: (tarifa_estimada, tiempo_minutos)
    """
    from django.utils import timezone
    fecha_salida_actual = timezone.now()
    return calcular_tarifa(fecha_entrada, fecha_salida_actual)