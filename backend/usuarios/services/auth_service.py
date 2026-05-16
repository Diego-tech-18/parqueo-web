"""
════════════════════════════════════════════════════════════════════════
SERVICE: AUTENTICACIÓN - VORTEX
════════════════════════════════════════════════════════════════════════

Lógica de negocio relacionada con login y generación de tokens JWT.

Este service NO sabe de HTTP. Recibe datos puros (email, password)
y devuelve datos puros (dict con tokens y usuario) o lanza excepciones
de dominio cuando algo falla.
"""

from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from usuarios.models import Usuario
from core.exceptions import (
    CredencialesInvalidasError,
    UsuarioInactivoError,
)


class AuthService:
    """
    Service de autenticación.
    Métodos estáticos porque no necesita estado interno.
    """

    @staticmethod
    def autenticar_usuario(email: str, password: str) -> Usuario:
        """
        Verifica las credenciales y devuelve el usuario si todo está OK.

        Lanza:
            CredencialesInvalidasError: si email/password son incorrectos.
            UsuarioInactivoError: si el usuario existe pero está desactivado.
        """
        usuario = authenticate(username=email, password=password)

        if not usuario:
            raise CredencialesInvalidasError()

        if not usuario.activo:
            raise UsuarioInactivoError()

        return usuario

    @staticmethod
    def generar_tokens(usuario: Usuario) -> dict:
        """
        Genera los tokens JWT (access + refresh) para un usuario.
        """
        refresh = RefreshToken.for_user(usuario)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }

    @staticmethod
    def login(email: str, password: str) -> dict:
        """
        Caso de uso completo: autentica y devuelve tokens + datos del usuario.

        Returns:
            dict con 'access', 'refresh' y 'usuario' (sin la URL absoluta de la foto;
            la URL la arma la view porque depende del request).
        """
        usuario = AuthService.autenticar_usuario(email, password)
        tokens = AuthService.generar_tokens(usuario)

        return {
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'usuario': usuario,  # la view se encarga de serializarlo
        }