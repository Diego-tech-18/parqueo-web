
from django.urls import path
from . import views

urlpatterns = [
    
    
    
    # Listar y crear secciones
    path('secciones/', views.SeccionListView.as_view(), name='seccion-list'),
    
    # Ver, editar y eliminar sección específica
    path('secciones/<int:pk>/', views.SeccionDetailView.as_view(), name='seccion-detail'),
    
  
    # Listar y crear espacios
    path('espacios/', views.EspacioListView.as_view(), name='espacio-list'),
    
    # Ver, editar y eliminar espacio específico
    path('espacios/<int:pk>/', views.EspacioDetailView.as_view(), name='espacio-detail'),
    
    # Cambiar estado de un espacio
    path('espacios/<int:pk>/cambiar-estado/', views.CambiarEstadoView.as_view(), name='espacio-cambiar-estado'),
    
    

    # Obtener mapa completo del parqueo
    path('mapa/', views.MapaParqueoView.as_view(), name='mapa-parqueo'),
]