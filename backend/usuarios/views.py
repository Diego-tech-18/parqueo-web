from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import Usuario
from .serializers import UsuarioSerializer, LoginSerializer
from .permissions import SoloAdministrador, AdministradorOEmpleado

# ────────────────────────────────────────────
# LOGIN
# POST /api/auth/login/
# Recibe email y password → devuelve token JWT
# ────────────────────────────────────────────
class LoginView(APIView):
    permission_classes = [AllowAny]  # no requiere estar logueado

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'error': 'Datos inválidos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        email    = serializer.validated_data['email']
        password = serializer.validated_data['password']

        # Verifica email y contraseña en la BD
        usuario = authenticate(request, username=email, password=password)

        if not usuario:
            return Response(
                {'error': 'Email o contraseña incorrectos'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not usuario.activo:
            return Response(
                {'error': 'Usuario inactivo, contacte al administrador'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Genera tokens JWT
        refresh = RefreshToken.for_user(usuario)

        # Devuelve token + datos del usuario al frontend
        return Response({
            'access' : str(refresh.access_token),  # token principal
            'refresh': str(refresh),                # para renovar sesión
            'usuario': {
                'id'      : usuario.id,
                'nombre'  : usuario.nombre,
                'apellido': usuario.apellido,
                'email'   : usuario.email,
                'rol'     : usuario.rol,
                'foto'    : request.build_absolute_uri(usuario.foto.url) if usuario.foto else None,
            }
        }, status=status.HTTP_200_OK)


# ────────────────────────────────────────────
# LISTAR Y CREAR USUARIOS
# GET  /api/usuarios/  → devuelve lista
# POST /api/usuarios/  → crea nuevo usuario
# ────────────────────────────────────────────
class UsuarioListView(APIView):
    permission_classes = [SoloAdministrador]  # requiere token JWT

    def get(self, request):
       #Devuelve solo usuarios activos ordenados por nombre"""
        usuarios = Usuario.objects.filter(activo=True).order_by('nombre')
        serializer = UsuarioSerializer(
            usuarios,
            many=True,
            context={'request': request}  # necesario para URL completa de foto
        )
        return Response(serializer.data)

    def post(self, request):
        """Crea un nuevo usuario"""
        serializer = UsuarioSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ────────────────────────────────────────────
# VER, EDITAR Y ELIMINAR USUARIO POR ID
# GET    /api/usuarios/1/  → ver usuario
# PUT    /api/usuarios/1/  → editar usuario
# DELETE /api/usuarios/1/  → eliminar usuario
# ────────────────────────────────────────────
class UsuarioDetailView(APIView):
    permission_classes = [SoloAdministrador] 

    def get_object(self, pk):
        """Busca usuario por ID, devuelve None si no existe"""
        try:
            return Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return None

    def get(self, request, pk):
        """Devuelve un usuario por su ID"""
        usuario = self.get_object(pk)
        if not usuario:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = UsuarioSerializer(
            usuario,
            context={'request': request}
        )
        return Response(serializer.data)

    def put(self, request, pk):
        """Edita un usuario, solo los campos enviados"""
        usuario = self.get_object(pk)
        if not usuario:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UsuarioSerializer(
            usuario,
            data=request.data,
            partial=True,              # permite editar solo algunos campos
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        #Desactiva un usuario (soft delete) con validaciones de seguridad"""
        usuario = self.get_object(pk)
        if not usuario:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 🚫 PROTECCIÓN 1: No puedes desactivarte a ti mismo
        if usuario.id == request.user.id:
            return Response(
                {'error': 'No puedes desactivar tu propia cuenta'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🚫 PROTECCIÓN 2: Debe quedar al menos 1 admin activo
        if usuario.rol == 'Administrador':
            # Contar admins activos (excluyendo el que se va a desactivar)
            admins_activos = Usuario.objects.filter(
                rol='Administrador',
                activo=True
            ).exclude(id=usuario.id).count()
            
            if admins_activos == 0:
                return Response(
                    {'error': 'No puedes desactivar al último administrador del sistema'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # ✅ Soft delete: solo desactivar, no eliminar
        usuario.activo = False
        usuario.save(update_fields=['activo'])
        
        return Response(
            {'mensaje': f'Usuario {usuario.nombre} desactivado correctamente'},
            status=status.HTTP_200_OK
        )
    
    # ── Ping: solo para mantener Supabase despierto ──
class PingView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'status': 'ok'})
