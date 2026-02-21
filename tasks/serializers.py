"""
Serializers para la aplicación de tareas.

Los serializers en Django REST Framework transforman objetos Python
en JSON y viceversa. También manejan validación de datos.

En este archivo defino:
- UserSerializer: Para representar usuarios
- RegisterSerializer: Para validación en el registro
- TaskSerializer: Para tareas (CRUD)
"""

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from .models import Task

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo User de Django.
    
    Uso este serializer para devolver información del usuario
    en respuestas de API sin exponer datos sensibles.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        read_only_fields = ('id',)


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer customizado para el registro de usuarios.
    
    - Valida que el email sea único mediante UniqueValidator.
    - Comprueba que password y password_confirm coincidan.
    - Hashea la contraseña usando create_user().
    """
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
        help_text="Correo electrónico único del usuario"
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Contraseña (mínimo 8 caracteres, no visible en respuesta)"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Confirmación de contraseña"
    )
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password_confirm')
        read_only_fields = ('id',)

    def validate(self, data):
        """
        Validación customizada: verifico que password y password_confirm coincidan.
        Si no coinciden, lanzo ValidationError que se devuelve al cliente.
        """
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                "password": "Las contraseñas no coinciden."
            })
        return data

    def create(self, validated_data):
        """
        Creación customizada de usuario.
        
        Aquí hago lo importante:
        - Quito password_confirm (ya no lo necesito)
        - Llamo a create_user() en lugar de create()
          Esto hashea automáticamente la contraseña
        """
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Task.
    
    Serializo todos los campos del modelo Task.
    Los campos read_only_fields se calculan automáticamente:
    - id: Generado por la base de datos
    - owner: Asignado automáticamente en perform_create()
    - created_at, updated_at: Manejados automáticamente por Django ORM
    
    Esto previene que el cliente intente modificar estos valores.
    """
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ('id', 'owner', 'created_at', 'updated_at')
