from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Task


class UserAuthTests(APITestCase):
    """Pruebas para registro y autenticación de usuarios."""

    def setUp(self):
        self.register_url = '/api/auth/register/'
        self.token_url = '/api/auth/token/'

    def test_register_and_login(self):
        # registro válido
        data = {
            'username': 'tester',
            'email': 'tester@example.com',
            'password': 'pass12345',
            'password_confirm': 'pass12345'
        }
        res = self.client.post(self.register_url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', res.data)

        # login con las mismas credenciales
        login_res = self.client.post(self.token_url, {'username': 'tester', 'password': 'pass12345'}, format='json')
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)
        self.assertIn('access', login_res.data)

    def test_register_duplicate_email(self):
        User.objects.create_user('u1', 'same@example.com', 'abcde123')
        data = {
            'username': 'u2',
            'email': 'same@example.com',
            'password': 'pass6789',
            'password_confirm': 'pass6789'
        }
        res = self.client.post(self.register_url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # la respuesta debe contener error en el campo email
        self.assertIn('email', res.data)

    def test_register_password_mismatch(self):
        data = {
            'username': 'user3',
            'email': 'user3@example.com',
            'password': 'abc',
            'password_confirm': 'xyz'
        }
        res = self.client.post(self.register_url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', res.data)


class TaskCRUDTests(APITestCase):
    """Pruebas para el CRUD de tareas y protección de recursos."""

    def setUp(self):
        # crear dos usuarios
        self.user1 = User.objects.create_user('u1', 'u1@example.com', 'pass123')
        self.user2 = User.objects.create_user('u2', 'u2@example.com', 'pass123')

        # autenticar cliente con user1
        self.client = APIClient()
        token_res = self.client.post('/api/auth/token/', {'username': 'u1', 'password': 'pass123'}, format='json')
        self.token = token_res.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_create_and_list_task(self):
        # al inicio no hay tareas
        res = self.client.get('/api/tasks/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, [])

        # crear una tarea
        task_data = {'title': 'Test task', 'description': 'hola'}
        create_res = self.client.post('/api/tasks/', task_data, format='json')
        self.assertEqual(create_res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_res.data['title'], 'Test task')
        self.assertEqual(create_res.data['owner'], self.user1.id)

        # listar de nuevo
        list_res = self.client.get('/api/tasks/')
        self.assertEqual(len(list_res.data), 1)

    def test_cannot_access_other_users_task(self):
        # crear tarea con user2 directamente en la BD
        other = Task.objects.create(title='otra', owner=self.user2)
        # intento obtenerla con user1
        res = self.client.get(f'/api/tasks/{other.id}/')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

        # intento actualizarla
        patch_res = self.client.patch(f'/api/tasks/{other.id}/', {'title': 'x'}, format='json')
        self.assertEqual(patch_res.status_code, status.HTTP_404_NOT_FOUND)

        # intento eliminarla
        del_res = self.client.delete(f'/api/tasks/{other.id}/')
        self.assertEqual(del_res.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_and_delete_task(self):
        task = Task.objects.create(title='orig', owner=self.user1)
        # actualizar
        upd_res = self.client.patch(f'/api/tasks/{task.id}/', {'completed': True}, format='json')
        self.assertEqual(upd_res.status_code, status.HTTP_200_OK)
        self.assertTrue(upd_res.data['completed'])

        # borrar
        del_res = self.client.delete(f'/api/tasks/{task.id}/')
        self.assertEqual(del_res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=task.id).exists())

