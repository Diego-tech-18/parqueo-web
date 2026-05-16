"""
════════════════════════════════════════════════════════════════════════
MANEJO HTTP DE EXCEPCIONES DE DOMINIO - VORTEX
════════════════════════════════════════════════════════════════════════

Traduce excepciones de dominio a respuestas HTTP de DRF.
Esto evita repetir try/except en cada view.

USO EN UNA VIEW:

    from core.http import manejar_excepciones_dominio

    class MiView(APIView):
        @manejar_excepciones_dominio
        def post(self, request):
            resultado = mi_service.hacer_algo(request.data)
            return Response(resultado, status=201)

Si el service lanza una excepción de dominio, el decorador la atrapa
y devuelve la respuesta HTTP correcta automáticamente.
"""

from functools import wraps
from rest_framework.response import Response
from rest_framework import status

from .exceptions import (
    DominioError,
    RecursoNoEncontradoError,
    DatosInvalidosError,
    ConflictoError,
    NoAutorizadoError,
    CredencialesInvalidasError,
    UsuarioInactivoError,
)


# ══════════════════════════════════════════════════════════════════════
# MAPEO: EXCEPCIÓN DE DOMINIO → CÓDIGO HTTP
# ══════════════════════════════════════════════════════════════════════

# El orden importa: las más específicas primero.
EXCEPCION_A_HTTP = [
    (CredencialesInvalidasError, status.HTTP_401_UNAUTHORIZED),
    (UsuarioInactivoError,       status.HTTP_403_FORBIDDEN),
    (NoAutorizadoError,          status.HTTP_403_FORBIDDEN),
    (RecursoNoEncontradoError,   status.HTTP_404_NOT_FOUND),
    (ConflictoError,             status.HTTP_409_CONFLICT),
    (DatosInvalidosError,        status.HTTP_400_BAD_REQUEST),
    (DominioError,               status.HTTP_400_BAD_REQUEST),  # fallback
]


def excepcion_a_response(excepcion: DominioError) -> Response:
    """
    Convierte una excepción de dominio en un Response HTTP.

    Si la excepción tiene atributos extra (como `espacio_id`), se
    incluyen en el cuerpo de la respuesta. Esto permite al frontend
    reaccionar de forma inteligente (ej: ofrecer "reactivar" cuando
    el conflicto es por una entidad soft-deleted).
    """
    # Cuerpo base de la respuesta
    cuerpo = {'error': excepcion.mensaje}

    # Atributos extra que algunas excepciones pueden traer
    atributos_extra = ('espacio_id', 'seccion_id', 'usuario_id', 'numero')
    for atributo in atributos_extra:
        if hasattr(excepcion, atributo):
            cuerpo[atributo] = getattr(excepcion, atributo)

    # Buscar el código HTTP correspondiente
    for clase, codigo_http in EXCEPCION_A_HTTP:
        if isinstance(excepcion, clase):
            return Response(cuerpo, status=codigo_http)

    # Por defecto (no debería pasar si todas heredan de DominioError)
    return Response(cuerpo, status=status.HTTP_400_BAD_REQUEST)


# ══════════════════════════════════════════════════════════════════════
# DECORADOR PARA USAR EN MÉTODOS DE VIEWS
# ══════════════════════════════════════════════════════════════════════

def manejar_excepciones_dominio(metodo_view):
    """
    Decorador que envuelve un método de view (get, post, put, delete)
    y traduce excepciones de dominio a respuestas HTTP.
    """
    @wraps(metodo_view)
    def wrapper(self, request, *args, **kwargs):
        try:
            return metodo_view(self, request, *args, **kwargs)
        except DominioError as e:
            return excepcion_a_response(e)
    return wrapper