"""
Configuración de rutas (URLs) del proyecto.

Este archivo es la entrada principal de todas las rutas de la API.
Aquí incluyo las rutas de la app 'tasks' bajo el prefijo /api/

Las rutas finales serán:
- /api/auth/register/: Registro de usuario
- /api/auth/token/: Login con JWT
- /api/auth/token/refresh/: Renovar token
- /api/tasks/: Listar y crear tareas
- /api/tasks/{id}/: Detalle, editar, eliminar tarea
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Panel administrativo de Django (http://localhost:8000/admin/)
    path('admin/', admin.site.urls),
    
    # Rutas de autenticación y tareas bajo /api/
    # La app 'tasks' contiene todos los endpoints de la API
    path('api/auth/', include('tasks.urls')),  # Autenticación (register, token, etc.)
    path('api/', include('tasks.urls')),        # Tareas (CRUD)
]
