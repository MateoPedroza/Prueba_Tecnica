"""
Vistas de la API REST para autenticación y gestión de tareas.

En este archivo defino:
- RegisterView: Endpoint público para registro de usuarios
- TaskListCreateView: Endpoint para listar y crear tareas (protegido)
- TaskRetrieveUpdateDestroyView: Endpoint para obtener, actualizar y eliminar tareas (protegido)

Todas las operaciones sobre tareas están filtradas por usuario propietario
para garantizar aislamiento de datos.
"""

from rest_framework import generics, permissions
from django.contrib.auth.models import User
from .models import Task
from .serializers import UserSerializer, RegisterSerializer, TaskSerializer
from rest_framework.response import Response
from rest_framework import status


class RegisterView(generics.CreateAPIView):
    """
    Vista de registro de usuario.
    
    Endpoint: POST /api/auth/register/
    
    Características:
    - Público: No requiere autenticación
    - Acepta: username, email, password, password_confirm
    - Devuelve: Usuario creado
    
    El proceso de registro:
    1. Cliente envía datos en JSON
    2. RegisterSerializer valida que las contraseñas coincidan
    3. create_user() hashea la contraseña
    4. Se devuelve el usuario creado
    
    El cliente luego obtiene tokens en el endpoint /api/auth/token/
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]  # Público, sin autenticación requerida


class TaskListCreateView(generics.ListCreateAPIView):
    """
    Vista para listar y crear tareas del usuario autenticado.
    
    Endpoints:
    - GET /api/tasks/: Obtiene todas las tareas del usuario autenticado
    - POST /api/tasks/: Crea una nueva tarea
    
    Seguridad:
    - Requiere autenticación JWT
    - El filtro get_queryset() garantiza que cada usuario solo ve sus tareas
    - El perform_create() asigna automáticamente el propietario (request.user)
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filtro crítico para seguridad:
        Devuelvo solo las tareas del usuario autenticado actual.
        Esto previene que un usuario vea tareas de otros usuarios.
        """
        return Task.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """
        Hook que se ejecuta cuando se crea una tarea.
        
        Aquí asigno automáticamente la tarea al usuario autenticado.
        Esto previene que el cliente intente asignar la tarea a otro usuario.
        """
        serializer.save(owner=self.request.user)


class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vista para obtener, actualizar y eliminar una tarea específica.
    
    Endpoints:
    - GET /api/tasks/{id}/: Obtiene detalle de una tarea
    - PATCH /api/tasks/{id}/: Actualiza parcialmente una tarea
    - PUT /api/tasks/{id}/: Actualiza completamente una tarea
    - DELETE /api/tasks/{id}/: Elimina una tarea
    
    Seguridad:
    - Requiere autenticación JWT
    - El filtro get_queryset() garantiza que solo el propietario puede acceder
    - Si el usuario no es propietario, Django devuelve 404 (como si no existiera)
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filtro de seguridad: Solo devuelvo tareas del usuario autenticado.
        Si un usuario intenta acceder a una tarea ajena, get_object()
        levantará una excepción 404 automáticamente.
        """
        return Task.objects.filter(owner=self.request.user)
