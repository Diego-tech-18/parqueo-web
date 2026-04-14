from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Seccion, Espacio
from .serializers import SeccionSerializer, EspacioSerializer, CambiarEstadoSerializer
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
    
    Body:
    {
        "estado": "LIBRE" | "OCUPADO" | "FUERA_SERVICIO",
        "notas": "opcional"
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        """Cambia el estado de un espacio"""
        try:
            espacio = Espacio.objects.get(pk=pk)
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
        espacio.save()
        
        # Retornar espacio actualizado
        return Response(
            EspacioSerializer(espacio).data,
            status=status.HTTP_200_OK
        )



# MAPA DEL PARQUEO (Vista consolidada)


class MapaParqueoView(APIView):
    """
    GET /api/mapa/
    
    Devuelve todas las secciones con sus espacios para mostrar el mapa
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Obtiene el mapa completo del parqueo"""
        secciones = Seccion.objects.filter(activo=True).prefetch_related('espacios')
        
        # Serializar secciones con espacios incluidos
        data = []
        for seccion in secciones:
            seccion_data = SeccionSerializer(seccion).data
            seccion_data['espacios'] = EspacioSerializer(
                seccion.espacios.filter(activo=True),
                many=True
            ).data
            data.append(seccion_data)
        
        return Response(data)