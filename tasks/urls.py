"""
Configuración de rutas (URLs) para la aplicación de tareas.

En este archivo mapeo las URLs a las vistas correspondientes.
Estos patrones se incluyen en core/urls.py bajo el prefijo /api/

Rutas públicas (sin autenticación):
- /api/auth/register/: Registro de usuario
- /api/auth/token/: Obtener tokens JWT
- /api/auth/token/refresh/: Renovar access token

Rutas protegidas (requieren JWT):
- /api/tasks/: Listar y crear tareas
- /api/tasks/{id}/: Obtener, actualizar y eliminar tarea
"""

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,    # Vista para obtener access + refresh tokens
    TokenRefreshView,        # Vista para renovar access token con refresh token
)
from . import views

urlpatterns = [
    # Autenticación
    path('register/', views.RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Tareas
    path('tasks/', views.TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', views.TaskRetrieveUpdateDestroyView.as_view(), name='task-detail'),
]
