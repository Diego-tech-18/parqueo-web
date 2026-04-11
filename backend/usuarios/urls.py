from django.urls import path
from .views import LoginView, UsuarioListView, UsuarioDetailView, PingView

urlpatterns = [

    # ── Login ──
    # POST /api/auth/login/  → recibe email y password, devuelve token
    path('auth/login/', LoginView.as_view(), name='login'),

    path('auth/ping/',  PingView.as_view(),  name='ping'), # ← nuevo

    # ── Usuarios ──
    # GET  /api/usuarios/    → lista todos los usuarios
    # POST /api/usuarios/    → crea un nuevo usuario
    path('usuarios/', UsuarioListView.as_view(), name='usuarios-list'),

    # GET    /api/usuarios/1/ → ver un usuario
    # PUT    /api/usuarios/1/ → editar un usuario
    # DELETE /api/usuarios/1/ → eliminar un usuario
    path('usuarios/<int:pk>/', UsuarioDetailView.as_view(), name='usuarios-detail'),

]