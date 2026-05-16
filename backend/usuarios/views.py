"""
════════════════════════════════════════════════════════════════════════
VIEWS: USUARIOS - VORTEX
════════════════════════════════════════════════════════════════════════

Controladores DELGADOS.

Responsabilidad de cada view:
    1. Recibir el HTTP request.
    2. Validar el formato de datos con un serializer.
    3. Llamar al service correspondiente.
    4. Serializar la respuesta y devolverla con el código HTTP correcto.

NO contienen lógica de negocio — esa vive en services/.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .serializers import UsuarioSerializer, LoginSerializer
from .permissions import SoloAdministrador
from .services.auth_service import AuthService
from .services.usuario_service import UsuarioService

from core.http import manejar_excepciones_dominio
from core.exceptions import DatosInvalidosError


# ══════════════════════════════════════════════════════════════════════
# LOGIN
# POST /api/auth/login/
# ══════════════════════════════════════════════════════════════════════

class LoginView(APIView):
    permission_classes = [AllowAny]

    @manejar_excepciones_dominio
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            raise DatosInvalidosError("Email o contraseña con formato inválido")

        # → al service
        resultado = AuthService.login(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
        )

        usuario = resultado['usuario']
        return Response({
            'access':  resultado['access'],
            'refresh': resultado['refresh'],
            'usuario': {
                'id':       usuario.id,
                'nombre':   usuario.nombre,
                'apellido': usuario.apellido,
                'email':    usuario.email,
                'rol':      usuario.rol,
                'foto':     request.build_absolute_uri(usuario.foto.url) if usuario.foto else None,
            },
        }, status=status.HTTP_200_OK)


# ══════════════════════════════════════════════════════════════════════
# LISTAR Y CREAR USUARIOS
# GET  /api/usuarios/
# POST /api/usuarios/
# ══════════════════════════════════════════════════════════════════════

class UsuarioListView(APIView):
    permission_classes = [SoloAdministrador]

    @manejar_excepciones_dominio
    def get(self, request):
        usuarios = UsuarioService.listar_activos()
        serializer = UsuarioSerializer(
            usuarios, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @manejar_excepciones_dominio
    def post(self, request):
        serializer = UsuarioSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # → al service
        usuario = UsuarioService.crear(serializer.validated_data)

        respuesta = UsuarioSerializer(usuario, context={'request': request})
        return Response(respuesta.data, status=status.HTTP_201_CREATED)


# ══════════════════════════════════════════════════════════════════════
# VER, EDITAR Y DESACTIVAR USUARIO POR ID
# GET    /api/usuarios/{id}/
# PUT    /api/usuarios/{id}/
# DELETE /api/usuarios/{id}/   (soft delete)
# ══════════════════════════════════════════════════════════════════════

class UsuarioDetailView(APIView):
    permission_classes = [SoloAdministrador]

    @manejar_excepciones_dominio
    def get(self, request, pk):
        usuario = UsuarioService.obtener_por_id(pk)
        serializer = UsuarioSerializer(usuario, context={'request': request})
        return Response(serializer.data)

    @manejar_excepciones_dominio
    def put(self, request, pk):
        # Obtener el usuario antes de validar (para validación contextual del serializer)
        usuario_existente = UsuarioService.obtener_por_id(pk)

        serializer = UsuarioSerializer(
            usuario_existente,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # → al service
        usuario = UsuarioService.actualizar(pk, serializer.validated_data)

        respuesta = UsuarioSerializer(usuario, context={'request': request})
        return Response(respuesta.data)

    @manejar_excepciones_dominio
    def delete(self, request, pk):
        usuario = UsuarioService.desactivar(
            usuario_id=pk,
            solicitante=request.user,
        )
        return Response(
            {'mensaje': f'Usuario {usuario.nombre} desactivado correctamente'},
            status=status.HTTP_200_OK,
        )


# ══════════════════════════════════════════════════════════════════════
# PING — keep-alive de Supabase
# ══════════════════════════════════════════════════════════════════════

class PingView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'status': 'ok'})