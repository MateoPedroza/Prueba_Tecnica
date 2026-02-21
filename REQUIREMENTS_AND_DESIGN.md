# REQUIREMENTS_AND_DESIGN.md

## Documento de Diseño y Requerimientos
**Proyecto:** Gestión de Usuarios y Tareas 
**Autor** Mateo Pedroza Bedoya 
**Fecha:** 21 de Febrero 2026  
**Versión:** 1.0  

---

## 1. Requerimientos Funcionales

### 1.1 Autenticación y Registro
- [x] **RF-001:** Registro de usuario (endpoint público)
  - Los usuarios pueden registrarse con usuario, email y contraseña
  - Validación de contraseña (debe confirmarse)
  - Respuesta con información del usuario creado y tokens JWT
  
- [x] **RF-002:** Autenticación mediante JWT
  - Login con usuario y contraseña
  - Respuesta con token de acceso (60 minutos de validez)
  - Respuesta con token de refresco (1 día de validez)
  - Token Bearer para acceso a endpoints protegidos

### 1.2 Gestión de Tareas (CRUD Completo)
- [x] **RF-003:** Crear tarea
  - Usuario autenticado puede crear tareas
  - Campos: título (requerido), descripción (opcional)
  - Asignación automática del propietario (usuario autenticado)
  - Timestamp de creación automático
  
- [x] **RF-004:** Listar tareas propias
  - Usuario autenticado solo ve sus propias tareas
  - No puede ver tareas de otros usuarios
  - Incluye información completa: título, descripción, estado, timestamps
  
- [x] **RF-005:** Obtener tarea por ID
  - Usuario autenticado puede obtener detalles de una tarea específica
  - Validación de propiedad (solo el propietario puede acceder)
  
- [x] **RF-006:** Actualizar tarea (UPDATE completo)
  - Usuario autenticado puede actualizar título y descripción
  - Usuario puede marcar como completada/no completada
  - Validación de propiedad (solo el propietario puede actualizar)
  - Timestamp de actualización automático
  
- [x] **RF-007:** Eliminar tarea
  - Usuario autenticado puede eliminar sus tareas
  - Validación de propiedad (solo el propietario puede eliminar)
  - Eliminación lógica con cascada en la base de datos

---

## 2. Requerimientos No Funcionales

- [x] **RNF-001:** API RESTful
  - Endpoints siguen convenciones REST
  - Métodos HTTP correctos (GET, POST, PUT, PATCH, DELETE)
  - Códigos de estado HTTP apropiados (200, 201, 400, 401, 403, 404, etc.)

- [x] **RNF-002:** Seguridad
  - Autenticación JWT obligatoria para endpoints protegidos
  - Validación de permisos por usuario propietario
  - CORS configurado para frontend (localhost:5173)
  - Validación de dirección de correo único
  - Contraseña hasheada (Django user model)

- [x] **RNF-003:** Base de Datos
  - PostgreSQL NEON como gestor de datos
  - Migraciones automáticas con Django ORM
  - Relaciones de claves foráneas correctamente definidas
  - Timestamps automáticos (created_at, updated_at)

- [x] **RNF-004:** Frontend
  - Consumo de API mediante Fetch API
  - Almacenamiento del token en localStorage
  - Interfaz responsiva y amigable (incluye modal de edición)
  - Validación de entrada en formularios
  - CRUD completo visible en la UI (botones Editar, Eliminar, etc.)

- [x] **RNF-005:** Documentación
  - Código comentado
  - Documento de diseño completo
  - README con instrucciones de ejecución
  - Historial de commits significativo en Git

---

## 3. Supuestos Relevantes

1. **Autenticación a Nivel de Usuario:**
   - Cada usuario solo puede ver y gestionar sus propias tareas
   - No hay concepto de tareas compartidas o públicas
   - La autenticación es obligatoria para todas las operaciones excepto registro y login

2. **Validación de Datos:**
   - El título de una tarea es requerido y no puede estar vacío
   - La descripción es opcional y puede contener texto con saltos de línea
   - El campo "completado" es boolean (verdadero/falso)

3. **Tokens JWT:**
   - Access token válido por 60 minutos
   - Refresh token válido por 1 día
   - El token se almacena en localStorage del navegador
   - Token Bearer requerido en el encabezado Authorization para endpoints protegidos

4. **Timestamps:**
   - created_at se establece automáticamente al crear una tarea
   - updated_at se actualiza automáticamente cada vez que se modifica una tarea
   - Se conservan en la base de datos para auditoría

5. **Eliminación en Cascada:**
   - Cuando un usuario se elimina, todas sus tareas se eliminan automáticamente

6. **CORS:**
   - Solo se permite solicitudes desde localhost:5173 (desarrollo)
   - Las credenciales se incluyen en las solicitudes CORS

---

## 4. Modelo de Datos (ERD)

### 4.1 Diagrama de Entidades y Relaciones

```
┌─────────────────────────┐
│       Usuario (User)    │
├─────────────────────────┤
│ id (PK)                 │
│ username (UNIQUE)       │
│ email (UNIQUE)          │
│ password_hash           │
│ date_joined (TIMESTAMP) │
│ last_login (TIMESTAMP)  │
└──────────────┬──────────┘
               │ 1
               │
               │ N (FK)
               │
        ┌──────────────┐
        │     Tarea    │
        ├──────────────┤
        │ id (PK)      │
        │ title        │
        │ description  │
        │ completed    │
        │ created_at   │
        │ updated_at   │
        │ owner_id (FK)│
        └──────────────┘
```

### 4.2 Descripción de Entidades

#### Usuario (Django User Model)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | AutoField (PK) | Identificador único |
| username | CharField(150) | Usuario único |
| email | EmailField | Email único |
| password | CharField | Contraseña hasheada |
| date_joined | DateTimeField | Fecha de registro (auto) |
| is_active | BooleanField | Indica si el usuario está activo |

#### Tarea (Task Model)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | AutoField (PK) | Identificador único |
| title | CharField(255) | Título de la tarea (requerido) |
| description | TextField | Descripción (opcional) |
| completed | BooleanField | Estado (por defecto: False) |
| created_at | DateTimeField | Fecha de creación (auto) |
| updated_at | DateTimeField | Fecha de actualización (auto) |
| owner | ForeignKey (User) | Propietario de la tarea (1:N) |

---

## 5. Endpoints Implementados

### 5.1 Autenticación (Public)

| Método | Ruta | Descripción | Autenticación |
|--------|------|-------------|---|
| POST | /api/auth/register/ | Registro de nuevo usuario | No |
| POST | /api/auth/token/ | Obtener tokens JWT | No |
| POST | /api/auth/token/refresh/ | Renovar access token | No |

### 5.2 Tareas (Protected)

| Método | Ruta | Descripción | Autenticación |
|--------|------|-------------|---|
| GET | /api/tasks/ | Listar tareas propias | JWT |
| POST | /api/tasks/ | Crear nueva tarea | JWT |
| GET | /api/tasks/{id}/ | Obtener tarea por ID | JWT |
| PATCH | /api/tasks/{id}/ | Actualizar tarea (parcial) | JWT |
| PUT | /api/tasks/{id}/ | Actualizar tarea (completa) | JWT |
| DELETE | /api/tasks/{id}/ | Eliminar tarea | JWT |

---

## 6. Stack Tecnológico

### Backend
- **Lenguaje:** Python 3.10+
- **Framework:** Django 6.0.2
- **API REST:** Django REST Framework 3.16.1
- **Autenticación:** djangorestframework-simplejwt 5.5.1
- **Base de Datos:** PostgreSQL (NEON)
- **CORS:** django-cors-headers 4.9.0
- **Driver DB:** psycopg2-binary 2.9.11

### Frontend
- **Framework:** Vue 3
- **Build Tool:** Vite 7.3.1
- **HTTP Client:** Fetch API (nativo)
- **Almacenamiento:** localStorage (tokens)

---

## 7. Decisiones de Diseño

### 7.1 Elección de JWT 
**Justificación:**
- Stateless: No requiere almacenar sesiones en servidor
- Escalable: Funciona en múltiples instancias
- Frontend-friendly: Token se almacena en cliente

### 7.2 Validación de Propiedad
**Decisión:** Validar en cada endpoint que user == task.owner  
**Justificación:**
- Seguridad: Previene acceso no autorizado
- Consistencia: Validación en nivel de API

### 7.3 CRUD Completo en Frontend
**Decisión:** Agregar modal de edición (no solo marcar completada)  
**Justificación:**
- Cumple CRUD completo en UI
- Mejor UX: Editar título y descripción
- Profesionalismo: Modal con validaciones

### 7.4 Confirmación de Contraseña
**Decisión:** Requerir password_confirm en registro  
**Justificación:**
- Previene errores de tipeo
- Good practice: Confirmación explícita

---

## 8. Seguridad Implementada

- ✅ JWT con tokens de corta duración (60 min)
- ✅ Refresh tokens (1 día)
- ✅ Validación de propiedad (user == task.owner)
- ✅ Contraseña hasheada (Django User model)
- ✅ HTTP 403 Forbidden para acceso denegado
- ✅ CORS configurado
- ✅ Limpeza de credenciales al logout

---

## 9. Conclusión

Este diseño cumple todos los requerimientos técnicos:
- ✅ CRUD completo
- ✅ Autenticación JWT
- ✅ PostgreSQL NEON
- ✅ Backend (Django + DRF)
- ✅ Frontend (Vue 3)
- ✅ Documentación
- ✅ Seguridad y validaciones

Proporciona una solución funcional, segura y escalable.
