from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Seccion, Espacio, Registro

from .models import Seccion, Espacio
from .serializers import (
    SeccionSerializer, 
    EspacioSerializer, 
    CambiarEstadoSerializer,
    RegistroSerializer,
    RegistrarEntradaSerializer,
    RegistrarSalidaSerializer
)
from usuarios.permissions import SoloAdministrador

# SECCIONES: LISTAR Y CREAR


class SeccionListView(APIView):
    """
    GET  /api/secciones/  → Lista todas las secciones
    POST /api/secciones/  → Crea una nueva sección
    """
    permission_classes = [SoloAdministrador]
    
    def get(self, request):
        """Lista todas las secciones activas con sus estadísticas"""
        secciones = Seccion.objects.filter(activo=True).order_by('nombre')
        serializer = SeccionSerializer(secciones, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Crea una nueva sección"""
        serializer = SeccionSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# SECCIONES: VER, EDITAR Y ELIMINAR

class SeccionDetailView(APIView):
    """
    GET    /api/secciones/{id}/  → Ver una sección
    PUT    /api/secciones/{id}/  → Editar sección
    DELETE /api/secciones/{id}/  → Eliminar sección
    """
    permission_classes = [SoloAdministrador]
    
    def get_object(self, pk):
        """Busca sección por ID"""
        try:
            return Seccion.objects.get(pk=pk)
        except Seccion.DoesNotExist:
            return None
    
    def get(self, request, pk):
        """Obtiene una sección específica"""
        seccion = self.get_object(pk)
        if not seccion:
            return Response(
                {'error': 'Sección no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = SeccionSerializer(seccion)
        return Response(serializer.data)
    
    def put(self, request, pk):
        """Edita una sección"""
        seccion = self.get_object(pk)
        if not seccion:
            return Response(
                {'error': 'Sección no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = SeccionSerializer(seccion, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """Elimina una sección (solo si no tiene espacios)"""
        seccion = self.get_object(pk)
        if not seccion:
            return Response(
                {'error': 'Sección no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar si tiene espacios
        if seccion.espacios.exists():
            return Response(
                {'error': 'No se puede eliminar una sección con espacios asignados'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        seccion.delete()
        return Response(
            {'mensaje': 'Sección eliminada correctamente'},
            status=status.HTTP_204_NO_CONTENT
        )



# ESPACIOS: LISTAR Y CREAR


class EspacioListView(APIView):
    """
    GET  /api/espacios/  → Lista todos los espacios
    POST /api/espacios/  → Crea un nuevo espacio
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Lista todos los espacios
        Puede filtrar por sección: ?seccion=1
        """
        espacios = Espacio.objects.select_related('seccion').all()
        
        # Filtro opcional por sección
        seccion_id = request.query_params.get('seccion', None)
        if seccion_id:
            espacios = espacios.filter(seccion_id=seccion_id)
        
        # Ordenar por sección y número
        espacios = espacios.order_by('seccion__nombre', 'numero')
        
        serializer = EspacioSerializer(espacios, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Crea un nuevo espacio (solo admin)"""
        # Verificar que sea admin
        if request.user.rol != 'Administrador':
            return Response(
                {'error': 'Solo administradores pueden crear espacios'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = EspacioSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# ESPACIOS: VER, EDITAR Y ELIMINAR


class EspacioDetailView(APIView):
    """
    GET    /api/espacios/{id}/  → Ver un espacio
    PUT    /api/espacios/{id}/  → Editar espacio
    DELETE /api/espacios/{id}/  → Eliminar espacio
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        """Busca espacio por ID"""
        try:
            return Espacio.objects.select_related('seccion').get(pk=pk)
        except Espacio.DoesNotExist:
            return None
    
    def get(self, request, pk):
        """Obtiene un espacio específico"""
        espacio = self.get_object(pk)
        if not espacio:
            return Response(
                {'error': 'Espacio no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = EspacioSerializer(espacio)
        return Response(serializer.data)
    
    def put(self, request, pk):
        """Edita un espacio (solo admin)"""
        if request.user.rol != 'Administrador':
            return Response(
                {'error': 'Solo administradores pueden editar espacios'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        espacio = self.get_object(pk)
        if not espacio:
            return Response(
                {'error': 'Espacio no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = EspacioSerializer(espacio, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """Elimina un espacio (solo admin)"""
        if request.user.rol != 'Administrador':
            return Response(
                {'error': 'Solo administradores pueden eliminar espacios'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        espacio = self.get_object(pk)
        if not espacio:
            return Response(
                {'error': 'Espacio no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        espacio.delete()
        return Response(
            {'mensaje': 'Espacio eliminado correctamente'},
            status=status.HTTP_204_NO_CONTENT
        )



# CAMBIAR ESTADO DE ESPACIO


class CambiarEstadoView(APIView):
    """
    POST /api/espacios/{id}/cambiar-estado/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        """Cambia el estado de un espacio - OPTIMIZADO"""
        try:
            espacio = Espacio.objects.select_related('seccion').get(pk=pk)
        except Espacio.DoesNotExist:
            return Response(
                {'error': 'Espacio no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = CambiarEstadoSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Cambiar estado
        nuevo_estado = serializer.validated_data['estado']
        notas = serializer.validated_data.get('notas', '')
        
        espacio.estado = nuevo_estado
        if notas:
            espacio.notas = notas
        espacio.save(update_fields=['estado', 'notas', 'actualizado_en'])
        
        # Retornar solo los datos necesarios (más rápido)
        return Response({
            'id': espacio.id,
            'numero': espacio.numero,
            'estado': espacio.estado,
            'seccion_nombre': espacio.seccion.nombre,
        }, status=status.HTTP_200_OK)


# MAPA DEL PARQUEO (Vista consolidada)


class MapaParqueoView(APIView):
    """
    GET /api/mapa/
    
    Devuelve todas las secciones con sus espacios para mostrar el mapa
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Obtiene el mapa completo del parqueo - OPTIMIZADO"""
        # Prefetch para evitar N+1 queries
        secciones = Seccion.objects.filter(activo=True).prefetch_related(
            'espacios'
        ).order_by('nombre')
        
        data = []
        for seccion in secciones:
            # Calcular estadísticas sin queries adicionales
            espacios_seccion = [e for e in seccion.espacios.all() if e.activo]
            
            seccion_data = {
                'id': seccion.id,
                'nombre': seccion.nombre,
                'tipo': seccion.tipo,
                'descripcion': seccion.descripcion,
                'activo': seccion.activo,
                'total_espacios': len(espacios_seccion),
                'espacios_libres': sum(1 for e in espacios_seccion if e.estado == 'LIBRE'),
                'espacios_ocupados': sum(1 for e in espacios_seccion if e.estado == 'OCUPADO'),
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
                    for e in espacios_seccion
                ]
            }
            data.append(seccion_data)
        
        return Response(data)
    
    # ══════════════════════════════════════════════════════════════════════════
# REGISTRAR ENTRADA
# ══════════════════════════════════════════════════════════════════════════

class RegistrarEntradaView(APIView):
    """
    POST /api/registros/entrada/
    
    Registra la entrada de un vehículo al parqueo
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Registra entrada de vehículo"""
        from .utils import determinar_horario_entrada
        from django.utils import timezone
        
        serializer = RegistrarEntradaSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener datos validados
        placa = serializer.validated_data['placa']
        tipo_vehiculo = serializer.validated_data['tipo_vehiculo']
        espacio_id = serializer.validated_data['espacio']
        notas = serializer.validated_data.get('notas', '')
        
        try:
            # Obtener el espacio
            espacio = Espacio.objects.get(pk=espacio_id)
            
            # Determinar horario de entrada
            fecha_entrada = timezone.now()
            horario = determinar_horario_entrada(fecha_entrada)
            
            # Crear el registro
            registro = Registro.objects.create(
                espacio=espacio,
                placa=placa,
                tipo_vehiculo=tipo_vehiculo,
                horario_entrada=horario,
                estado='EN_CURSO',
                notas=notas
            )
            
            # Marcar el espacio como OCUPADO
            espacio.marcar_ocupado()
            
            # Serializar respuesta
            response_serializer = RegistroSerializer(registro)
            
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
            
        except Espacio.DoesNotExist:
            return Response(
                {'error': 'Espacio no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ══════════════════════════════════════════════════════════════════════════
# REGISTRAR SALIDA
# ══════════════════════════════════════════════════════════════════════════

class RegistrarSalidaView(APIView):
    """
    POST /api/registros/salida/
    
    Registra la salida de un vehículo
    Calcula tiempo y tarifa automáticamente
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Registra salida de vehículo"""
        from .utils import calcular_tarifa
        from django.utils import timezone
        
        serializer = RegistrarSalidaSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        placa = serializer.validated_data.get('placa')
        registro_id = serializer.validated_data.get('registro_id')
        notas_salida = serializer.validated_data.get('notas', '')
        
        try:
            # Buscar el registro activo
            if registro_id:
                registro = Registro.objects.get(pk=registro_id, estado='EN_CURSO')
            elif placa:
                registro = Registro.objects.get(
                    placa__iexact=placa,
                    estado='EN_CURSO'
                )
            else:
                return Response(
                    {'error': 'Debe proporcionar placa o registro_id'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Registrar fecha de salida
            fecha_salida = timezone.now()
            
            # Calcular tarifa y tiempo
            tarifa, tiempo_minutos = calcular_tarifa(
                registro.fecha_entrada,
                fecha_salida
            )
            
            # Actualizar el registro
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
                'actualizado_en'
            ])
            
            # Marcar el espacio como LIBRE
            registro.espacio.marcar_libre()
            
            # Serializar respuesta
            response_serializer = RegistroSerializer(registro)
            
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK
            )
            
        except Registro.DoesNotExist:
            return Response(
                {'error': 'No se encontró un registro activo con esos datos'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ══════════════════════════════════════════════════════════════════════════
# BUSCAR REGISTRO ACTIVO
# ══════════════════════════════════════════════════════════════════════════

class BuscarRegistroActivoView(APIView):
    """
    GET /api/registros/buscar/?placa=ABC123
    GET /api/registros/buscar/?espacio=5
    
    Busca un registro activo por placa o espacio
    Muestra info sin registrar salida (para preview)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Busca registro activo"""
        from .utils import calcular_tarifa_actual
        
        placa = request.query_params.get('placa')
        espacio_id = request.query_params.get('espacio')
        
        if not placa and not espacio_id:
            return Response(
                {'error': 'Debe proporcionar placa o espacio'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Buscar registro activo
            if placa:
                registro = Registro.objects.select_related('espacio', 'espacio__seccion').get(
                    placa__iexact=placa,
                    estado='EN_CURSO'
                )
            else:
                registro = Registro.objects.select_related('espacio', 'espacio__seccion').get(
                    espacio_id=espacio_id,
                    estado='EN_CURSO'
                )
            
            # Calcular tarifa estimada actual
            tarifa_estimada, tiempo_minutos = calcular_tarifa_actual(registro.fecha_entrada)
            
            # Serializar con tarifa estimada
            data = RegistroSerializer(registro).data
            data['tarifa_estimada'] = str(tarifa_estimada)
            data['tiempo_minutos_actual'] = tiempo_minutos
            
            return Response(data, status=status.HTTP_200_OK)
            
        except Registro.DoesNotExist:
            return Response(
                {'error': 'No se encontró un registro activo'},
                status=status.HTTP_404_NOT_FOUND
            )


# ══════════════════════════════════════════════════════════════════════════
# HISTORIAL DE REGISTROS
# ══════════════════════════════════════════════════════════════════════════

class HistorialRegistrosView(APIView):
    """
    GET /api/registros/historial/
    
    Lista todos los registros con filtros opcionales
    Filtros: ?estado=FINALIZADO&fecha_desde=2024-01-01
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Lista registros con filtros"""
        registros = Registro.objects.select_related(
            'espacio',
            'espacio__seccion'
        ).all()
        
        # Filtro por estado
        estado = request.query_params.get('estado')
        if estado:
            registros = registros.filter(estado=estado)
        
        # Filtro por fecha desde
        fecha_desde = request.query_params.get('fecha_desde')
        if fecha_desde:
            registros = registros.filter(fecha_entrada__gte=fecha_desde)
        
        # Filtro por fecha hasta
        fecha_hasta = request.query_params.get('fecha_hasta')
        if fecha_hasta:
            registros = registros.filter(fecha_entrada__lte=fecha_hasta)
        
        # Filtro por placa
        placa = request.query_params.get('placa')
        if placa:
            registros = registros.filter(placa__icontains=placa)
        
        # Ordenar por más reciente
        registros = registros.order_by('-fecha_entrada')
        
        # Serializar
        serializer = RegistroSerializer(registros, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)