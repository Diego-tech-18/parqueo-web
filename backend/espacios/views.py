"""
════════════════════════════════════════════════════════════════════════
VIEWS: ESPACIOS - VORTEX
════════════════════════════════════════════════════════════════════════

Controladores DELGADOS para los 4 dominios de la app:
    1. Secciones (CRUD)
    2. Espacios (CRUD + cambiar estado + mapa)
    3. Registros (entrada / salida / búsqueda activa / historial)

Cada view:
    - Recibe el HTTP request.
    - Valida formato con un serializer.
    - Llama al service correspondiente.
    - Serializa la respuesta y devuelve el código HTTP correcto.

NO contienen lógica de negocio — esa vive en services/.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import (
    SeccionSerializer,
    EspacioSerializer,
    CambiarEstadoSerializer,
    RegistroSerializer,
    RegistrarEntradaSerializer,
    RegistrarSalidaSerializer,
    TarifaSerializer
)

from .services.seccion_service import SeccionService
from .services.espacio_service import EspacioService
from .services.registro_service import RegistroService
from .services.tarifa_service import TarifaService

from usuarios.permissions import SoloAdministrador
from core.http import manejar_excepciones_dominio


# ══════════════════════════════════════════════════════════════════════
# SECCIONES
# ══════════════════════════════════════════════════════════════════════

class SeccionListView(APIView):
    """
    GET  /api/secciones/  → listar
    POST /api/secciones/  → crear
    """
    permission_classes = [SoloAdministrador]

    @manejar_excepciones_dominio
    def get(self, request):
        secciones = SeccionService.listar()
        serializer = SeccionSerializer(secciones, many=True)
        return Response(serializer.data)

    @manejar_excepciones_dominio
    def post(self, request):
        serializer = SeccionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        seccion = SeccionService.crear(serializer.validated_data)

        respuesta = SeccionSerializer(seccion)
        return Response(respuesta.data, status=status.HTTP_201_CREATED)


class SeccionDetailView(APIView):
    """
    GET    /api/secciones/{id}/  → ver
    PUT    /api/secciones/{id}/  → editar
    DELETE /api/secciones/{id}/  → eliminar
    """
    permission_classes = [SoloAdministrador]

    @manejar_excepciones_dominio
    def get(self, request, pk):
        seccion = SeccionService.obtener_por_id(pk)
        return Response(SeccionSerializer(seccion).data)

    @manejar_excepciones_dominio
    def put(self, request, pk):
        # Obtener antes de validar (para validación contextual del serializer)
        seccion_existente = SeccionService.obtener_por_id(pk)

        serializer = SeccionSerializer(seccion_existente, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        seccion = SeccionService.actualizar(pk, serializer.validated_data)

        return Response(SeccionSerializer(seccion).data)

    @manejar_excepciones_dominio
    def delete(self, request, pk):
        seccion = SeccionService.eliminar(pk)
        return Response(
            {'mensaje': f'Sección {seccion.nombre} desactivada correctamente'},
            status=status.HTTP_200_OK,
        )

class ReactivarSeccionView(APIView):
    """
    POST /api/secciones/{id}/reactivar/
    Reactiva una sección que estaba soft-deleted (activo=False).
    """
    permission_classes = [SoloAdministrador]

    @manejar_excepciones_dominio
    def post(self, request, pk):
        seccion = SeccionService.reactivar(pk)
        return Response({
            'mensaje': f'Sección {seccion.nombre} reactivada correctamente',
            'seccion': SeccionSerializer(seccion).data,
        }, status=status.HTTP_200_OK)
# ══════════════════════════════════════════════════════════════════════
# ESPACIOS
# ══════════════════════════════════════════════════════════════════════

class EspacioListView(APIView):
    """
    GET  /api/espacios/?seccion=1  → listar (filtro opcional)
    POST /api/espacios/            → crear (solo admin)
    """
    permission_classes = [IsAuthenticated]

    @manejar_excepciones_dominio
    def get(self, request):
        seccion_id = request.query_params.get('seccion')
        espacios = EspacioService.listar(seccion_id=seccion_id)
        serializer = EspacioSerializer(espacios, many=True)
        return Response(serializer.data)

    @manejar_excepciones_dominio
    def post(self, request):
        # Solo admin puede crear espacios
        if request.user.rol != 'Administrador':
            return Response(
                {'error': 'Solo administradores pueden crear espacios'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = EspacioSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        espacio = EspacioService.crear(serializer.validated_data)

        respuesta = EspacioSerializer(espacio)
        return Response(respuesta.data, status=status.HTTP_201_CREATED)


class EspacioDetailView(APIView):
    """
    GET    /api/espacios/{id}/  → ver
    PUT    /api/espacios/{id}/  → editar (solo admin)
    DELETE /api/espacios/{id}/  → eliminar (solo admin)
    """
    permission_classes = [IsAuthenticated]

    @manejar_excepciones_dominio
    def get(self, request, pk):
        espacio = EspacioService.obtener_por_id(pk)
        return Response(EspacioSerializer(espacio).data)

    @manejar_excepciones_dominio
    def put(self, request, pk):
        if request.user.rol != 'Administrador':
            return Response(
                {'error': 'Solo administradores pueden editar espacios'},
                status=status.HTTP_403_FORBIDDEN,
            )

        espacio_existente = EspacioService.obtener_por_id(pk)

        serializer = EspacioSerializer(espacio_existente, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        espacio = EspacioService.actualizar(pk, serializer.validated_data)

        return Response(EspacioSerializer(espacio).data)

    @manejar_excepciones_dominio
    def delete(self, request, pk):
        if request.user.rol != 'Administrador':
            return Response(
                {'error': 'Solo administradores pueden eliminar espacios'},
                status=status.HTTP_403_FORBIDDEN,
            )

        espacio = EspacioService.eliminar(pk)
        return Response(
            {'mensaje': f'Espacio {espacio.numero} desactivado correctamente'},
            status=status.HTTP_200_OK,
        )


class CambiarEstadoView(APIView):
    """
    POST /api/espacios/{id}/cambiar-estado/
    """
    permission_classes = [IsAuthenticated]

    @manejar_excepciones_dominio
    def post(self, request, pk):
        serializer = CambiarEstadoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        espacio = EspacioService.cambiar_estado(
            espacio_id=pk,
            nuevo_estado=serializer.validated_data['estado'],
            notas=serializer.validated_data.get('notas', ''),
        )

        # Respuesta liviana (solo lo necesario)
        return Response({
            'id': espacio.id,
            'numero': espacio.numero,
            'estado': espacio.estado,
            'seccion_nombre': espacio.seccion.nombre,
        }, status=status.HTTP_200_OK)


class MapaParqueoView(APIView):
    """
    GET /api/mapa/  → mapa consolidado del parqueo
    """
    permission_classes = [IsAuthenticated]

    @manejar_excepciones_dominio
    def get(self, request):
        mapa = EspacioService.obtener_mapa()
        return Response(mapa)
    
class ReactivarEspacioView(APIView):
    """
    POST /api/espacios/{id}/reactivar/
    Reactiva un espacio que estaba soft-deleted (activo=False).
    """
    permission_classes = [IsAuthenticated]

    @manejar_excepciones_dominio
    def post(self, request, pk):
        if request.user.rol != 'Administrador':
            return Response(
                {'error': 'Solo administradores pueden reactivar espacios'},
                status=status.HTTP_403_FORBIDDEN,
            )

        espacio = EspacioService.reactivar(pk)
        return Response({
            'mensaje': f'Espacio {espacio.numero} reactivado correctamente',
            'espacio': EspacioSerializer(espacio).data,
        }, status=status.HTTP_200_OK)


# ══════════════════════════════════════════════════════════════════════
# REGISTROS (ENTRADA / SALIDA / BÚSQUEDA / HISTORIAL)
# ══════════════════════════════════════════════════════════════════════

class RegistrarEntradaView(APIView):
    """
    POST /api/registros/entrada/
    """
    permission_classes = [IsAuthenticated]

    @manejar_excepciones_dominio
    def post(self, request):
        serializer = RegistrarEntradaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        registro = RegistroService.registrar_entrada(serializer.validated_data)

        return Response(
            RegistroSerializer(registro).data,
            status=status.HTTP_201_CREATED,
        )


class RegistrarSalidaView(APIView):
    """
    POST /api/registros/salida/
    """
    permission_classes = [IsAuthenticated]

    @manejar_excepciones_dominio
    def post(self, request):
        serializer = RegistrarSalidaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        registro = RegistroService.registrar_salida(serializer.validated_data)

        return Response(
            RegistroSerializer(registro).data,
            status=status.HTTP_200_OK,
        )


class BuscarRegistroActivoView(APIView):
    """
    GET /api/registros/buscar/?placa=ABC123
    GET /api/registros/buscar/?espacio=5
    """
    permission_classes = [IsAuthenticated]

    @manejar_excepciones_dominio
    def get(self, request):
        resultado = RegistroService.buscar_activo_con_tarifa(
            placa=request.query_params.get('placa'),
            espacio_id=request.query_params.get('espacio'),
        )

        # Serializamos el registro y le agregamos los campos extra calculados
        data = RegistroSerializer(resultado['registro']).data
        data['tarifa_estimada'] = str(resultado['tarifa_estimada'])
        data['tiempo_minutos_actual'] = resultado['tiempo_minutos_actual']

        return Response(data, status=status.HTTP_200_OK)


class HistorialRegistrosView(APIView):
    """
    GET /api/registros/historial/?estado=FINALIZADO&fecha_desde=2024-01-01
    """
    permission_classes = [IsAuthenticated]

    @manejar_excepciones_dominio
    def get(self, request):
        # Recolectar filtros del query string
        filtros = {
            'estado':       request.query_params.get('estado'),
            'fecha_desde':  request.query_params.get('fecha_desde'),
            'fecha_hasta':  request.query_params.get('fecha_hasta'),
            'placa':        request.query_params.get('placa'),
        }

        registros = RegistroService.listar_historial(filtros)
        serializer = RegistroSerializer(registros, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# ══════════════════════════════════════════════════════════════════════
# TARIFAS
# ══════════════════════════════════════════════════════════════════════

class TarifaView(APIView):
    """
    GET  /api/tarifas/  → ver la configuración actual (cualquier autenticado)
    PUT  /api/tarifas/  → actualizar (solo Administrador)
    """

    def get_permissions(self):
        # Leer: cualquier autenticado. Editar: solo admin.
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [SoloAdministrador()]

    @manejar_excepciones_dominio
    def get(self, request):
        tarifa = TarifaService.obtener()
        return Response(TarifaSerializer(tarifa).data)

    @manejar_excepciones_dominio
    def put(self, request):
        # El service valida las reglas de negocio (valores > 0, horas, etc.)
        tarifa = TarifaService.actualizar(request.data)
        return Response(TarifaSerializer(tarifa).data)