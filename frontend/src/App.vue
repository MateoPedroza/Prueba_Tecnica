<template>
  <div class="container">
    <h1>Gestión de Tareas</h1>
    
    <!-- Sección de Autenticación - visible cuando NO hay token -->
    <div v-if="!token" class="auth-section">
      <!-- Tabs para alternancia entre Login y Registro -->
      <div class="auth-tabs">
        <button 
          :class="['tab', { active: showLoginForm }]"
          @click="showLoginForm = true"
        >
          Iniciar sesión
        </button>
        <button 
          :class="['tab', { active: !showLoginForm }]"
          @click="showLoginForm = false"
        >
          Registrarse
        </button>
      </div>

      <!-- Formulario de Login -->
      <div v-if="showLoginForm" class="auth-form">
        <h2>Iniciar sesión</h2>
        <form @submit.prevent="login">
          <input 
            v-model="loginData.username" 
            placeholder="Usuario" 
            required 
          />
          <!-- Password field con toggle de visibilidad personalizado -->
          <div class="password-field">
            <input 
              v-model="loginData.password" 
              :type="showPassword ? 'text' : 'password'" 
              placeholder="Contraseña" 
              required 
            />
            <button type="button" @click="showPassword = !showPassword" class="toggle-password">
              {{ showPassword ? '🙈' : '👁️' }}
            </button>
          </div>
          <button type="submit" class="btn-primary">Entrar</button>
        </form>
        <!-- Mostrar errores de login si los hay -->
        <div v-if="loginError" class="error">{{ loginError }}</div>
      </div>

      <!-- Formulario de Registro -->
      <div v-else class="auth-form">
        <h2>Crear nueva cuenta</h2>
        <form @submit.prevent="register">
          <input 
            v-model="registerData.username" 
            placeholder="Usuario (nombre único)" 
            required 
          />
          <input 
            v-model="registerData.email" 
            type="email"
            placeholder="Correo electrónico" 
            required 
          />
          <!-- Password field -->
          <div class="password-field">
            <input 
              v-model="registerData.password" 
              :type="showPassword ? 'text' : 'password'" 
              placeholder="Contraseña" 
              required 
            />
            <button type="button" @click="showPassword = !showPassword" class="toggle-password">
              {{ showPassword ? '🙈' : '👁️' }}
            </button>
          </div>
          <!-- Password confirmation field -->
          <div class="password-field">
            <input 
              v-model="registerData.password_confirm" 
              :type="showPassword ? 'text' : 'password'" 
              placeholder="Confirmar contraseña" 
              required 
            />
            <button type="button" @click="showPassword = !showPassword" class="toggle-password">
              {{ showPassword ? '🙈' : '👁️' }}
            </button>
          </div>
          <button type="submit" class="btn-primary">Registrarse</button>
        </form>
        <!-- Mostrar errores de registro si los hay -->
        <div v-if="registerError" class="error">{{ registerError }}</div>
        <div v-if="registerSuccess" class="success">¡Cuenta creada! Ya puedes iniciar sesión.</div>
      </div>
    </div>
    
    <!-- Sección de Tareas - visible cuando HAY token (usuario autenticado) -->
    <div v-else>
      <!-- Header con botón de logout -->
      <div class="header-actions">
        <h2>Mis tareas</h2>
        <button @click="logout" class="btn-logout">Cerrar sesión</button>
      </div>
      
      <!-- Formulario para crear nueva tarea -->
      <form @submit.prevent="addTask" class="task-form">
        <input v-model="newTask.title" placeholder="Título" required />
        <input v-model="newTask.description" placeholder="Descripción (opcional)" />
        <button type="submit">Agregar tarea</button>
      </form>

      <!-- Modal de edición de tarea -->
      <div v-if="editingTaskId" class="modal-overlay" @click.self="cancelEdit">
        <div class="modal">
          <h3>Editar tarea</h3>
          <form @submit.prevent="saveEdit">
            <input v-model="editingTask.title" placeholder="Título" required />
            <textarea v-model="editingTask.description" placeholder="Descripción (opcional)"></textarea>
            <div class="modal-actions">
              <button type="submit" class="btn-save">Guardar</button>
              <button type="button" @click="cancelEdit" class="btn-cancel">Cancelar</button>
            </div>
          </form>
        </div>
      </div>

      <!-- Leyenda cuando no hay tareas -->
      <div v-if="tasks.length === 0" class="no-tasks">
        No tienes tareas aún. ¡Crea una!
      </div>
      
      <!-- Lista de tareas: itero sobre cada tarea y muestro sus acciones -->
      <ul class="task-list">
        <li v-for="task in tasks" :key="task.id" class="task-item" :class="{completed: task.completed}">
          <!-- Sección de contenido de la tarea -->
          <div class="task-content">
            <!-- Checkbox para marcar como completada -->
            <input 
              type="checkbox" 
              v-model="task.completed" 
              @change="updateTaskCompleted(task)" 
              class="task-checkbox" 
            />
            <!-- Título y descripción -->
            <div class="task-text">
              <span class="task-title" :style="{textDecoration: task.completed ? 'line-through' : 'none'}">
                {{ task.title }}
              </span>
              <!-- Mostrar descripción si existe -->
              <p v-if="task.description" class="task-description">{{ task.description }}</p>
            </div>
          </div>
          <!-- Botones de acción -->
          <div class="task-actions">
            <button @click="startEdit(task)" class="btn-edit">Editar</button>
            <button @click="deleteTask(task.id)" class="btn-delete">Eliminar</button>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
/**
 * Componente principal de la aplicación de gestión de tareas.
 * 
 * Este componente maneja:
 * - Autenticación del usuario (login/logout)
 * - CRUD completo de tareas (create, read, update, delete)
 * - Almacenamiento de tokens en localStorage
 * - Modal para edición de tareas
 */

import { ref, onMounted } from 'vue'

// URL base de la API del backend
// Se lee desde la variable de entorno VITE_API_URL proporcionada
// por Vercel/ambientes de producción; si no existe, uso localhost.
// Normalizo quitando una posible barra final para evitar '//' en las rutas.
const rawApiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api'
const apiUrl = rawApiUrl.replace(/\/+$/, '')

// =====================
// Estado de autenticación
// =====================
// Token JWT obtenido del backend, almacenado en localStorage
const token = ref(localStorage.getItem('token') || '')

// Control de qué formulario mostrar (login o registro)
const showLoginForm = ref(true)

// Datos del formulario de login
const loginData = ref({ username: '', password: '' })
const loginError = ref('')

// Datos del formulario de registro
const registerData = ref({ username: '', email: '', password: '', password_confirm: '' })
const registerError = ref('')
const registerSuccess = ref(false)

// Toggle de visibilidad de contraseña (ambos formularios lo comparten)
const showPassword = ref(false)

// =====================
// Estado de tareas
// =====================
// Array de tareas del usuario autenticado
const tasks = ref([])
// Datos del formulario para crear nueva tarea
const newTask = ref({ title: '', description: '' })
// Estado del modal de edición
const editingTaskId = ref(null)
const editingTask = ref({ title: '', description: '' })

/**
 * Función de login: Obtiene tokens JWT del backend
 * 
 * Flujo:
 * 1. POST a /api/auth/token/ con username y password
 * 2. Backend devuelve access token (válido 60 min) y refresh token
 * 3. Guardo el access token en localStorage
 * 4. Cargo las tareas del usuario
 * 5. Limpio el formulario de login
 */
async function login() {
  loginError.value = ''
  try {
    const res = await fetch(`${apiUrl}/auth/token/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(loginData.value)
    })
    if (!res.ok) throw new Error('Credenciales incorrectas')
    const data = await res.json()
    token.value = data.access
    localStorage.setItem('token', token.value)
    await fetchTasks()
    // Limpio el formulario de login (seguridad)
    loginData.value = { username: '', password: '' }
  } catch (e) {
    loginError.value = e.message
  }
}

/**
 * Función de registro: Crea una nueva cuenta de usuario
 * 
 * Flujo:
 * 1. Validar que las contraseñas coincidan (validación local)
 * 2. POST a /api/auth/register/ con username, email, password y password_confirm
 * 3. Backend valida y crea el usuario
 * 4. Mostrar mensaje de éxito
 * 5. Cambiar a tab de login para permitir que el usuario inicie sesión
 */
async function register() {
  registerError.value = ''
  registerSuccess.value = false
  
  // Validación local: verificar que las contraseñas coincidan
  if (registerData.value.password !== registerData.value.password_confirm) {
    registerError.value = 'Las contraseñas no coinciden'
    return
  }
  
  // Validación local: contraseña mínimo 6 caracteres
  if (registerData.value.password.length < 6) {
    registerError.value = 'La contraseña debe tener al menos 6 caracteres'
    return
  }
  
  try {
    const res = await fetch(`${apiUrl}/auth/register/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: registerData.value.username,
        email: registerData.value.email,
        password: registerData.value.password,
        password_confirm: registerData.value.password_confirm
      })
    })
    
    if (!res.ok) {
      const error = await res.json()
      // El backend devuelve errores específicos por campo
      if (error.username) {
        throw new Error('El usuario ya existe')
      } else if (error.email) {
        throw new Error('El email ya está registrado')
      } else {
        throw new Error('Error al registrar el usuario')
      }
    }
    
    // Registro exitoso
    registerSuccess.value = true
    registerData.value = { username: '', email: '', password: '', password_confirm: '' }
    
    // Después de 2 segundos, cambiar a login
    setTimeout(() => {
      showLoginForm.value = true
      registerSuccess.value = false
    }, 2000)
    
  } catch (e) {
    registerError.value = e.message
  }
}

/**
 * Función de logout: Limpia la sesión
 * 
 * Aquí limpio:
 * - Token del estado y localStorage
 * - Array de tareas
 * - Formulario de login (credenciales)
 * - Formulario de registro (credenciales)
 * - Reseteo el flag para mostrar login form nuevamente
 * 
 * Esto asegura que los datos sensibles no queden en el navegador.
 */
function logout() {
  token.value = ''
  localStorage.removeItem('token')
  tasks.value = []
  loginData.value = { username: '', password: '' }
  registerData.value = { username: '', email: '', password: '', password_confirm: '' }
  loginError.value = ''
  registerError.value = ''
  showLoginForm.value = true
}

/**
 * Carga las tareas del usuario autenticado desde el backend
 * 
 * GET /api/tasks/ retorna un array JSON con todas las tareas del usuario
 * (gracias al filtro de backend que filtra por owner=request.user)
 */
async function fetchTasks() {
  if (!token.value) return
  const res = await fetch(`${apiUrl}/tasks/`, {
    headers: { Authorization: `Bearer ${token.value}` }
  })
  if (res.ok) {
    tasks.value = await res.json()
  }
}

/**
 * Crea una nueva tarea en el backend
 * 
 * POST /api/tasks/ con:
 * - title: requerido
 * - description: opcional
 * 
 * El backend asigna automáticamente:
 * - owner = request.user
 * - created_at = ahora
 * - updated_at = ahora
 * - completed = false (por defecto)
 */
async function addTask() {
  const res = await fetch(`${apiUrl}/tasks/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token.value}`
    },
    body: JSON.stringify(newTask.value)
  })
  if (res.ok) {
    newTask.value = { title: '', description: '' }
    await fetchTasks()
  }
}

/**
 * Actualiza el estado de completitud de una tarea
 * 
 * PATCH /api/tasks/{id}/ actualiza parcialmente la tarea
 * (el backend solo actualiza los campos que envío)
 * 
 * Se ejecuta cuando el usuario hace click en el checkbox.
 */
async function updateTaskCompleted(task) {
  await fetch(`${apiUrl}/tasks/${task.id}/`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token.value}`
    },
    body: JSON.stringify({ completed: task.completed })
  })
  await fetchTasks()
}

/**
 * Abre el modal de edición cargando los datos de la tarea
 */
function startEdit(task) {
  editingTaskId.value = task.id
  editingTask.value = { title: task.title, description: task.description }
}

/**
 * Guarda los cambios en la tarea
 * 
 * PATCH /api/tasks/{id}/ actualiza los campos title y description
 * El backend valida que el usuario autenticado sea el propietario
 */
async function saveEdit() {
  const res = await fetch(`${apiUrl}/tasks/${editingTaskId.value}/`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token.value}`
    },
    body: JSON.stringify(editingTask.value)
  })
  if (res.ok) {
    editingTaskId.value = null
    editingTask.value = { title: '', description: '' }
    await fetchTasks()
  }
}

/**
 * Cierra el modal de edición sin guardar cambios
 */
function cancelEdit() {
  editingTaskId.value = null
  editingTask.value = { title: '', description: '' }
}

/**
 * Elimina una tarea del backend
 * 
 * DELETE /api/tasks/{id}/ elimina la tarea
 * El backend valida que el usuario autenticado sea el propietario
 * Si no es propietario, devuelve 403 Forbidden
 */
async function deleteTask(id) {
  await fetch(`${apiUrl}/tasks/${id}/`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token.value}` }
  })
  await fetchTasks()
}

/**
 * Hook del ciclo de vida: Se ejecuta cuando el componente se monta
 * Aquí cargo las tareas si el usuario ya tiene token (refresco de página)
 */
onMounted(fetchTasks)
</script>

<style scoped>
/**
 * Estilos de la aplicación de gestión de tareas
 * 
 * Aquí defino el diseño responsivo y las clases CSS
 * scoped: Los estilos solo aplican a este componente
 */

.container {
  max-width: 700px;
  margin: 2rem auto;
  padding: 2rem;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

h1 {
  color: #333;
  text-align: center;
  margin-bottom: 2rem;
}

h2 {
  color: #555;
  margin: 0;
}

/* =====================
   Sección de autenticación
   ===================== */

.auth-section {
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
}

/* Tabs de alternancia entre login y registro */
.auth-tabs {
  display: flex;
  gap: 0;
  margin-bottom: 2rem;
  border-bottom: 2px solid #e0e0e0;
}

.tab {
  flex: 1;
  padding: 1rem;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-size: 1rem;
  color: #666;
  transition: all 0.3s ease;
  font-weight: 500;
}

.tab:hover {
  color: #333;
  background-color: #f0f0f0;
}

.tab.active {
  color: #007bff;
  border-bottom-color: #007bff;
  background: none;
}

.auth-form {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.auth-form h2 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #333;
}

.btn-primary {
  width: 100%;
  padding: 0.75rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background-color: #0056b3;
}

/* Mensaje de éxito en registro */
.success {
  color: #155724;
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
  padding: 1rem;
  border-radius: 4px;
  margin-top: 1rem;
}

.error {
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  padding: 1rem;
  border-radius: 4px;
  margin-top: 1rem;
}

/* Header con título y botón logout */
.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1.5rem;
  margin-bottom: 1.5rem;
}

.btn-logout {
  padding: 0.5rem 1rem;
  background-color: #6c757d;
  font-size: 0.9rem;
}

.btn-logout:hover {
  background-color: #5a6268;
}

/* Formularios */
form {
  display: flex;
  gap: 0.5rem;
  margin: 1.5rem 0;
  flex-wrap: wrap;
}

.task-form {
  display: flex;
  gap: 0.75rem;
  margin: 1.5rem 0;
  flex-wrap: wrap;
}

.task-form input {
  flex: 1;
  min-width: 150px;
}

/* Inputs de texto y área de texto */
input[type="text"],
input[type="password"],
textarea {
  flex: 1;
  min-width: 200px;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  font-family: inherit;
}

textarea {
  min-height: 80px;
  resize: vertical;
}

/* Campo de contraseña personalizado con toggle */
.password-field {
  display: flex;
  gap: 0.5rem;
  flex: 1;
  min-width: 200px;
  align-items: center;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0;
}

.password-field input {
  flex: 1;
  border: none;
  border-radius: 4px 0 0 4px;
  padding: 0.75rem;
  font-size: 1rem;
  outline: none;
}

/* Botón de toggle de visibilidad de contraseña */
.toggle-password {
  background: none;
  border: none;
  padding: 0.75rem 1rem;
  cursor: pointer;
  font-size: 1.2rem;
  color: #666;
  border-radius: 0 4px 4px 0;
  transition: background-color 0.2s;
}

.toggle-password:hover {
  background-color: #f0f0f0;
}

.toggle-password:active {
  background-color: #e0e0e0;
}

/* Botones generales */
button {
  padding: 0.75rem 1.5rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.2s;
}

button:hover {
  background-color: #0056b3;
}

button:active {
  transform: scale(0.98);
}

/* Variantes de botones por tipo de acción */
.btn-delete {
  padding: 0.5rem 0.75rem;
  background-color: #dc3545;
  font-size: 0.85rem;
}

.btn-delete:hover {
  background-color: #c82333;
}

.btn-edit {
  padding: 0.5rem 0.75rem;
  background-color: #28a745;
  font-size: 0.85rem;
}

.btn-edit:hover {
  background-color: #218838;
}

.btn-save {
  padding: 0.75rem 1.5rem;
  background-color: #28a745;
}

.btn-save:hover {
  background-color: #218838;
}

.btn-cancel {
  padding: 0.75rem 1.5rem;
  background-color: #6c757d;
}

.btn-cancel:hover {
  background-color: #5a6268;
}

/* Mensaje de error de login */
.error {
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  padding: 1rem;
  border-radius: 4px;
  margin-top: 1rem;
}

/* Mensaje cuando no hay tareas */
.no-tasks {
  text-align: center;
  color: #999;
  padding: 2rem;
  font-size: 1.1rem;
}

/* Lista de tareas */
.task-list {
  list-style: none;
  padding: 0;
  margin-top: 1.5rem;
}

/* Item individual de tarea */
.task-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem;
  background-color: #f9f9f9;
  border: 1px solid #eee;
  border-radius: 4px;
  margin-bottom: 0.75rem;
  transition: background-color 0.2s;
}

.task-item:hover {
  background-color: #f0f0f0;
}

/* Tarea completada: opacidad reducida */
.task-item.completed {
  opacity: 0.6;
}

/* Contenedor del contenido (checkbox + título + descripción) */
.task-content {
  display: flex;
  gap: 0.75rem;
  flex: 1;
}

/* Checkbox de completitud */
.task-checkbox {
  margin-top: 0.25rem;
  cursor: pointer;
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

/* Sección de texto: título y descripción */
.task-text {
  flex: 1;
}

/* Título de la tarea */
.task-title {
  display: block;
  font-weight: 500;
  color: #333;
  margin: 0;
  word-break: break-word;
}

/* Descripción de la tarea */
.task-description {
  color: #666;
  font-size: 0.9rem;
  margin: 0.5rem 0 0 0;
  white-space: pre-wrap;  /* Preserva saltos de línea */
  word-break: break-word; /* Rompe palabras largas */
}

/* Botones de acción (editar, eliminar) */
.task-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

/* =====================
   Modal de edición
   ===================== */

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background-color: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal h3 {
  color: #333;
  margin-top: 0;
  margin-bottom: 1.5rem;
}

.modal form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.modal input,
.modal textarea {
  width: 100%;
  box-sizing: border-box;
}

.modal-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.modal-actions button {
  flex: 1;
  max-width: 150px;
}
</style>
