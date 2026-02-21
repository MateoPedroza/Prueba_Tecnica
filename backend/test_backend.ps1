# Script de pruebas automáticas para el backend Django + DRF
# Ejecuta este script en PowerShell desde la raíz del proyecto

# 1. Registro de usuario
Write-Host "Registrando usuario..."
try {
    $register = Invoke-RestMethod -Uri http://127.0.0.1:8000/api/auth/register/ -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"username": "testuser", "email": "testuser@example.com", "password": "TestPass123", "password_confirm": "TestPass123"}'
    Write-Host "Usuario registrado."
} catch {
    Write-Host "El usuario ya existe o hubo un error en el registro."
}

# 2. Obtener token JWT
Write-Host "Obteniendo token..."
$response = Invoke-RestMethod -Uri http://127.0.0.1:8000/api/auth/token/ -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"username": "testuser", "password": "TestPass123"}'
$token = $response.access
Write-Host "Token obtenido: $token"

# 3. Listar tareas (debe estar vacío)
Write-Host "Listando tareas..."
$tareas = Invoke-RestMethod -Uri http://127.0.0.1:8000/api/tasks/ -Headers @{"Authorization"="Bearer $token"}
Write-Host "Tareas actuales: $($tareas | ConvertTo-Json)"

# 4. Crear una tarea
Write-Host "Creando tarea..."
$nuevaTarea = Invoke-RestMethod -Uri http://127.0.0.1:8000/api/tasks/ -Method POST -Headers @{"Authorization"="Bearer $token"; "Content-Type"="application/json"} -Body '{"title": "Mi primera tarea", "description": "Descripción opcional"}'
Write-Host "Tarea creada: $($nuevaTarea | ConvertTo-Json)"

# 5. Actualizar la tarea (marcar como completada)
Write-Host "Actualizando tarea..."
$idTarea = $nuevaTarea.id
$tareaActualizada = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/tasks/$idTarea/" -Method PATCH -Headers @{"Authorization"="Bearer $token"; "Content-Type"="application/json"} -Body '{"completed": true}'
Write-Host "Tarea actualizada: $($tareaActualizada | ConvertTo-Json)"

# 6. Eliminar la tarea
Write-Host "Eliminando tarea..."
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/tasks/$idTarea/" -Method DELETE -Headers @{"Authorization"="Bearer $token"}
Write-Host "Tarea eliminada."

# 7. Listar tareas nuevamente (debe estar vacío)
$tareasFinal = Invoke-RestMethod -Uri http://127.0.0.1:8000/api/tasks/ -Headers @{"Authorization"="Bearer $token"}
Write-Host "Tareas finales: $($tareasFinal | ConvertTo-Json)"
