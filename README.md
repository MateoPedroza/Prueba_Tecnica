# Gestión de Usuarios y Tareas

Aplicación full-stack para gestión de tareas con autenticación JWT, backend Django + DRF y frontend Vue 3.

## 📋 Características

- ✅ Registro e autenticación de usuarios con JWT
- ✅ CRUD completo de tareas (crear, listar, obtener, actualizar, eliminar)
- ✅ Cada usuario solo ve y gestiona sus propias tareas
- ✅ Modal de edición de tareas (UPDATE completo)
- ✅ Validación de permisos en API
- ✅ Interfaz responsiva y amigable
- ✅ Tokens JWT con expiración configurable

---

## 🏗️ Estructura del Proyecto

```
Prueba/
├── backend/                 # Backend Django + DRF
│   ├── core/               # Configuración del proyecto
│   ├── tasks/              # App de tareas
│   ├── manage.py           # Comando de Django
│   ├── requirements.txt     # Dependencias Python
│   └── test_backend.ps1    # Script de pruebas
│
├── frontend/               # Frontend Vue 3
│   ├── src/
│   │   ├── App.vue        # Componente principal
│   │   └── ...
│   ├── package.json
│   └── vite.config.js
│
├── REQUIREMENTS_AND_DESIGN.md  # Documento de diseño
└── README.md              # Este archivo
```

---

## 🚀 Inicio Rápido

### Requisitos Previos

- Python 3.10+
- Node.js 16+ (para frontend)
- PostgreSQL (NEON recomendado)
- Git

### 1. Clonar el Repositorio

```bash
git clone <https://github.com/MateoPedroza/Prueba_Tecnica>
cd Prueba
```

### 2. Configurar Backend

#### 2.1 Crear Entorno Virtual

```bash
python -m venv venv
```

#### 2.2 Activar Entorno Virtual

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

#### 2.3 Instalar Dependencias

```bash
pip install -r requirements.txt
```

Este archivo incluye todas las dependencias necesarias:
- Django 6.0.2
- Django REST Framework 3.16.1
- djangorestframework-simplejwt 5.5.1 (JWT)
- psycopg2-binary 2.9.11 (PostgreSQL driver)
- django-cors-headers 4.9.0 (CORS)
- python-decouple 3.8 (Variables de entorno)

#### 2.4 Configurar Variables de Entorno

En lugar de hardcodear credenciales, uso un archivo `.env` para variables sensibles:

**1. Copiar el archivo de ejemplo:**
```bash
copy .env.example .env
```

**2. Editar `.env` con tus credenciales reales:**
```env
DEBUG=True
SECRET_KEY=tu-clave-secreta-aqui

DB_ENGINE=django.db.backends.postgresql
DB_NAME=neondb
DB_USER=neondb_owner
DB_PASSWORD=tu-password-real
DB_HOST=ep-xxx.neon.tech
DB_PORT=5432

CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

**⚠️ IMPORTANTE:** El archivo `.env` está en `.gitignore` para no exponer credenciales. Solo `.env.example` se commitea.

#### 2.5 Aplicar Migraciones

```bash
python manage.py migrate
```

#### 2.6 Iniciar Servidor Backend

```bash
python manage.py runserver
```

El backend estará disponible en: `http://127.0.0.1:8000/`

---

### 3. Configurar Frontend

#### 3.1 Instalar Dependencias

```bash
cd frontend
npm install
```

#### 3.2 Iniciar Servidor Frontend

```bash
npm run dev
```

El frontend estará disponible en: `http://localhost:5173/`

---

## 🔑 Credenciales de Prueba

---

## 🚢 Despliegue en producción

El backend ya está desplegado en Railway. La URL resultante es
algo como `https://<tu-app>.up.railway.app/`.

Para que el frontend pueda comunicarse con él y quedar accesible
públicamente, se utiliza Vercel:

1. **Configurar base del API en el frontend**
   - Se lee desde la variable `VITE_API_URL`.
   - En desarrollo el valor por defecto es
     `http://127.0.0.1:8000/api`.

2. **Agregar archivo de ejemplo en el frontend**
   - Copia `frontend/.env.example` (creado en el repo) a
     `frontend/.env` y ajusta la URL (`VITE_API_URL`).
   - Nunca subas `.env` al repositorio; está ignorado por
     `.gitignore`.

3. **Configurar variables de entorno del backend**
   - En Railway añade/actualiza `CORS_ALLOWED_ORIGINS` para incluir
     la URL de Vercel (por ejemplo
     `https://your-app.vercel.app`). Puedes usar comas para
     varias orígenes.
   - También actualiza `ALLOWED_HOSTS` si quieres restringir más los
     hosts (aunque `pruebatecnica-production-f2dc.up.railway.app`
     ya está ahí de antes).

3. **Desplegar en Vercel** (pasos detallados más abajo).


## 📡 API REST - Endpoints

El proyecto incluye dos usuarios de prueba preconfigurados:

### Usuario 1
- **Username:** `demo`
- **Password:** `prueba123`
- **Email:** `demo@example.com`

### Usuario 2
- **Username:** `usuario2`
- **Password:** `prueba123`
- **Email:** `usuario2@example.com`

### Crear Nuevos Usuarios

Opción 1: Usar la interfaz de registro en el frontend
```
http://localhost:5173/
```

Opción 2: Crear desde Django shell
```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
user = User.objects.create_user('username', 'email@example.com', 'password123')
print(f'Usuario creado: {user.username}')
```

---

## 📡 API REST - Endpoints

### Autenticación (Public)

```
POST /api/auth/register/
```
Registrar nuevo usuario

```
POST /api/auth/token/
```
Obtener tokens JWT

```
POST /api/auth/token/refresh/
```
Renovar access token

### Tareas (Protected - Requiere JWT)

```
GET /api/tasks/
```
Listar tareas propias

```
POST /api/tasks/
```
Crear nueva tarea

```
GET /api/tasks/{id}/
```
Obtener tarea por ID

```
PATCH /api/tasks/{id}/
```
Actualizar tarea (parcial)

```
DELETE /api/tasks/{id}/
```
Eliminar tarea

Documentación detallada: Ver `REQUIREMENTS_AND_DESIGN.md`

---

## 🧪 Testing - Script de Pruebas Automatizadas

El proyecto incluye un script para probar todos los endpoints:

```powershell
.\backend\test_backend.ps1
```

Este script:
1. Registra un usuario
2. Obtiene el token JWT
3. Crea varias tareas
4. Actualiza una tarea
5. Elimina una tarea
6. Lista tareas finales

---

## 🔒 Seguridad

- ✅ Autenticación JWT requerida para endpoints protegidos
- ✅ Validación de propiedad: Cada usuario solo accede a sus tareas
- ✅ Contraseñas hasheadas con Django User model
- ✅ CORS configurado para frontend
- ✅ HTTP 403 Forbidden para acceso no autorizado
- ✅ Limpeza de credenciales al logout

---

## 📚 Documentación

- **REQUIREMENTS_AND_DESIGN.md:** Especificación completa del proyecto
  - Requerimientos funcionales y no funcionales
  - Modelo de datos (ERD)
  - Listado de endpoints
  - Decisiones de diseño
  - Seguridad implementada

- **requirements.txt:** Dependencias Python (instalar con `pip install -r requirements.txt`)
- **.env.example:** Plantilla de variables de entorno (copiar a `.env`)
- **.gitignore:** Archivos ignorados en git (incluye `.env`, `venv/`, `node_modules/`)

---

## 🔐 Seguridad y Variables de Entorno

El proyecto usa `python-decouple` para manejar variables de entorno de forma segura.

**Flujo:**
1. Creas un archivo `.env` basado en `.env.example`
2. Las credenciales se cargan desde `.env` (nunca se commiten)
3. En producción, usas variables de entorno del servidor (Railway, Render, etc.)

**Credenciales sensibles protegidas:**
- ✅ `SECRET_KEY` de Django
- ✅ Contraseña de base de datos
- ✅ Host de base de datos
- ✅ Token CORS

---

## 🛠️ Desarrollo

### Estructura del Código

**Backend:**
```
backend/
├── core/
│   ├── settings.py      # Configuración Django + DRF + JWT
│   ├── urls.py          # Rutas del proyecto
│   └── wsgi.py          # WSGI app
├── tasks/
│   ├── models.py        # Modelo Task
│   ├── serializers.py   # Serializers DRF
│   ├── views.py         # Vistas (APIViews)
│   ├── urls.py          # Rutas de tareas
│   └── permissions.py   # Permisos personalizados
```

**Frontend:**
```
frontend/src/
├── App.vue              # Componente principal (CRUD + Auth)
├── main.js              # Punto de entrada
└── ...
```

---

## 📝 Notas de Desarrollo

- **JWT Tokens:** Access token válido 60 minutos, Refresh token 1 día
- **Base de Datos:** PostgreSQL NEON (gratuito, conexión SSL requerida)
- **CORS:** Configurado para localhost:5173 (desarrollo)
- **Frontend:** Fetch API nativa (sin dependencias externas de HTTP)

---

## 📄 Licencia

Proyecto de prueba técnica. Todos los derechos reservados.

---

## 👥 Autor

Mateo Pedroza Bedoya.

---

## 💡 Preguntas Frecuentes

### ¿Cómo obtener un nuevo token?
```
POST /api/auth/token/
{
  "username": "demo",
  "password": "prueba123"
}
```

### ¿Por qué no veo las tareas de otro usuario?
Por diseño, cada usuario solo ve sus propias tareas. Esto es una medida de seguridad.

### ¿Dónde almacena el token el frontend?
En `localStorage` del navegador. Se limpia automáticamente al cerrar sesión.

### ¿Qué hacer si el token expira?
El frontend usa el refresh token automáticamente. Si ambos expiran, tu sesión se cierra.

---

**Última actualización:** Febrero 2026  
**Versión:** 1.0
