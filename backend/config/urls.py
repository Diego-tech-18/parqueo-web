"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('admin/', admin.site.urls),

    # Refresh de tokens JWT (proporcionado por SimpleJWT)
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    path('api/', include('usuarios.urls')),
    path('api/', include('espacios.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)