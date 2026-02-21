"""
Modelos de la aplicación de tareas.

En este archivo defino el modelo Task que representa una tarea del usuario.
Cada tarea está asociada a un usuario propietario mediante una clave foránea.
"""

from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    """
    Modelo Task - Representa una tarea individual del usuario.
    
    Campos:
    - title: Título de la tarea (requerido)
    - description: Descripción más detallada (opcional)
    - completed: Estado de completitud (por defecto False)
    - created_at: Fecha de creación automática
    - updated_at: Fecha de última actualización
    - owner: Usuario propietario de la tarea (relación 1:N con User)
    
    Aquí implemento la aislamiento de datos: cada usuario solo puede ver
    y modificar sus propias tareas. Esto se valida en las vistas con
    get_queryset() que filtra por self.request.user.
    """
    
    title = models.CharField(
        max_length=255,
        help_text="Título de la tarea (requerido)"
    )
    description = models.TextField(
        blank=True,
        help_text="Descripción opcional de la tarea"
    )
    completed = models.BooleanField(
        default=False,
        help_text="Indica si la tarea está completada"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de creación (automático)"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Fecha y hora de última actualización (automático)"
    )
    owner = models.ForeignKey(
        User,
        related_name='tasks',
        on_delete=models.CASCADE,
        help_text="Usuario propietario de la tarea"
    )

    def __str__(self):
        """Representación en string del modelo, usada en el admin."""
        return self.title

    class Meta:
        """Metadatos del modelo."""
        ordering = ['-created_at']  # Ordeno por creación más reciente primero
        verbose_name = 'Tarea'
        verbose_name_plural = 'Tareas'
