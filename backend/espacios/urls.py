from django.urls import path
from .views import (
    SeccionListView, 
    SeccionDetailView, 
    EspacioListView, 
    EspacioDetailView, 
    CambiarEstadoView, 
    MapaParqueoView,
    RegistrarEntradaView,
    RegistrarSalidaView,
    BuscarRegistroActivoView,
    HistorialRegistrosView
)

urlpatterns = [
    # ── Secciones ──
    path('secciones/', SeccionListView.as_view(), name='seccion-list'),
    path('secciones/<int:pk>/', SeccionDetailView.as_view(), name='seccion-detail'),
    
    # ── Espacios ──
    path('espacios/', EspacioListView.as_view(), name='espacio-list'),
    path('espacios/<int:pk>/', EspacioDetailView.as_view(), name='espacio-detail'),
    path('espacios/<int:pk>/cambiar-estado/', CambiarEstadoView.as_view(), name='cambiar-estado'),
    
    # ── Mapa ──
    path('mapa/', MapaParqueoView.as_view(), name='mapa-parqueo'),
    
    # ── Registros (Entradas/Salidas) ──
    path('registros/entrada/', RegistrarEntradaView.as_view(), name='registrar-entrada'),
    path('registros/salida/', RegistrarSalidaView.as_view(), name='registrar-salida'),
    path('registros/buscar/', BuscarRegistroActivoView.as_view(), name='buscar-registro'),
    path('registros/historial/', HistorialRegistrosView.as_view(), name='historial-registros'),
]