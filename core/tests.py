from json import loads
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from uuid import uuid4

from rest_framework.test import APIClient
from rest_framework import status

from core.models import ApiKey

User = get_user_model()

user_data = {
    'email': 'test@testing.com',
    'first_name': 'Test',
    'last_name': 'Testing',
    'password': 'testing123',
    'username': 'test',
}
user_error_data = {
    'email': 'test-error@testing.com',
    'first_name': 'Test',
    'last_name': 'Errors',
    'password': 'testing123',
    'username': 'testerrors',
}
temp = {
    'email': 'test3@testing.com',
    'first_name': 'Test3',
    'last_name': 'Testing3',
    'username': 'test3',
    'password': 'testing123',
}


class UserTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(**user_data)
        user2 = User.objects.create_user(**user_error_data)

    def test_user_can_create(self):
        """User can create"""
        client = APIClient()
        user = user_data.copy()
        user['email'] = 'test2@testing.com'
        user['username'] = 'test2'
        response = client.post(reverse('user-list'), user, format='multipart')
        new_user = loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(new_user.get('email'), user.get('email'))
        self.assertEqual(new_user.get('username'), user.get('username'))
        self.assertEqual(new_user.get('first_name'), user.get('first_name'))
        self.assertEqual(new_user.get('last_name'), user.get('last_name'))

    def test_user_can_retrieve(self):
        """User can retrieve his data"""
        user = User.objects.get(username=user_data.get('username'))
        client = APIClient()
        client.login(
            username=user_data.get('username'),
            password=user_data.get('password'),
        )
        response = client.get(
            reverse('user-detail', args=[user.id]),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        get_user = loads(response.content)
        self.assertEqual(get_user.get('email'), user.email)
        self.assertEqual(get_user.get('username'), user.username)
        self.assertEqual(get_user.get('first_name'), user.first_name)
        self.assertEqual(get_user.get('last_name'), user.last_name)

    def test_user_can_edit(self):
        """User can edit his data"""
        user = User.objects.get(username=user_data.get('username'))
        client = APIClient()
        client.login(
            username=user_data.get('username'),
            password=user_data.get('password'),
        )
        response = client.put(
            reverse('user-detail', args=[user.id]),
            temp,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        edit_user = loads(response.content)
        self.assertNotEqual(edit_user.get('email'), user.email)
        self.assertNotEqual(edit_user.get('username'), user.username)
        self.assertNotEqual(edit_user.get('first_name'), user.first_name)
        self.assertNotEqual(edit_user.get('last_name'), user.last_name)

    def test_user_can_patch(self):
        """User can edit his data"""
        user = User.objects.get(username=user_error_data.get('username'))
        client = APIClient()
        client.login(
            username=user_error_data.get('username'),
            password=user_error_data.get('password'),
        )
        response = client.patch(
            reverse('user-detail', args=[user.id]),
            {'email': 'test3@testing.com'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        patch_user = loads(response.content)
        self.assertNotEqual(patch_user.get('email'), user.email)

    def test_other_user_cannot_edit_user(self):
        """Other user cannot edit user"""
        user = User.objects.get(username=user_data.get('username'))
        user2 = User.objects.get(username=user_error_data.get('username'))
        client = APIClient()
        client.login(
            username=user_error_data.get('username'),
            password=user_error_data.get('password'),
        )
        response = client.put(
            reverse('user-detail', args=[user.id]),
            temp,
        )
        self.assertEqual(response.status_code, 403)

    def test_other_user_cannot_patch_user(self):
        """Other user cannot edit user"""
        user = User.objects.get(username=user_data.get('username'))
        user2 = User.objects.get(username=user_error_data.get('username'))
        client = APIClient()
        client.login(
            username=user_error_data.get('username'),
            password=user_error_data.get('password'),
        )
        response = client.patch(
            reverse('user-detail', args=[user.id]),
            {'email': 'test3@testing.com'},
        )
        self.assertEqual(response.status_code, 403)

    def test_user_cannot_delete(self):
        """User cannot delete his data"""
        user = User.objects.get(username=user_error_data.get('username'))
        client = APIClient()
        client.login(
            username=user_error_data.get('username'),
            password=user_error_data.get('password'),
        )
        response = client.delete(
            reverse('user-detail', args=[user.id]),
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(User.objects.count(), 2)


class ApiKeyTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(**user_data)
        user2 = User.objects.create_user(**user_error_data)
        key = ApiKey.objects.create(
            user=user,
            name='app',
            api_key=str(uuid4()),
        )
        key2 = ApiKey.objects.create(
            user=user2,
            name='app',
            api_key=str(uuid4()),
        )

    def test_user_can_create_api_key(self):
        """User can create api key"""
        client = APIClient()
        client.login(
            username=user_data.get('username'),
            password=user_data.get('password'),
        )
        response = client.post(
            reverse('key-list'),
            {'name': 'test'},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ApiKey.objects.count(), 3)

    def test_user_can_list_api_key(self):
        """User can list api key"""
        user = User.objects.get(username=user_data.get('username'))
        client = APIClient()
        client.login(
            username=user_data.get('username'),
            password=user_data.get('password'),
        )
        response = client.get(
            reverse('key-list'),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        api_keys = loads(response.content)
        self.assertEqual(len(api_keys), 1)

    def test_user_can_retrieve_api_key(self):
        """User can retrieve api key"""
        user = User.objects.get(username=user_data.get('username'))
        key = user.keys.all().first()
        client = APIClient()
        client.login(
            username=user_data.get('username'),
            password=user_data.get('password'),
        )
        url = reverse('key-list')
        response = client.get(
            f'{url}{key.id}/',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data_key = loads(response.content)
        self.assertEqual(data_key.get('name'), key.name)
        self.assertEqual(data_key.get('api_key'), str(key.api_key))

    def test_user_can_delete_api_key(self):
        """User can delete api key"""
        user = User.objects.get(username=user_data.get('username'))
        key = user.keys.all().first()
        client = APIClient()
        client.login(
            username=user_data.get('username'),
            password=user_data.get('password'),
        )
        url = reverse('key-list')
        response = client.delete(
            f'{url}{key.id}/',
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ApiKey.objects.count(), 1)

    def test_user_can_edit_api_key(self):
        """User can edit api key"""
        user = User.objects.get(username=user_data.get('username'))
        key = user.keys.all().first()
        client = APIClient()
        client.login(
            username=user_data.get('username'),
            password=user_data.get('password'),
        )
        url = reverse('key-list')
        response = client.put(
            f'{url}{key.id}/',
            {'name': 'test'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data_key = loads(response.content)
        self.assertEqual(data_key.get('name'), 'test')

    def test_user_can_patch_api_key(self):
        """User can patch api key"""
        user = User.objects.get(username=user_data.get('username'))
        key = user.keys.all().first()
        client = APIClient()
        client.login(
            username=user_data.get('username'),
            password=user_data.get('password'),
        )
        url = reverse('key-list')
        response = client.patch(
            f'{url}{key.id}/',
            {'name': 'test'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data_key = loads(response.content)
        self.assertEqual(data_key.get('name'), 'test')

    def test_user_cannot_edit_api_key(self):
        """User cannot edit api key"""
        user = User.objects.get(username=user_data.get('username'))
        key = user.keys.all().first()
        user2 = User.objects.get(username=user_error_data.get('username'))
        key2 = user2.keys.all().first()
        client = APIClient()
        client.login(
            username=user_data.get('username'),
            password=user_data.get('password'),
        )
        url = reverse('key-list')
        response = client.put(
            f'{url}{key2.id}/',
            {'name': 'test'},
        )
        self.assertEqual(response.status_code, 404)

    def test_user_cannot_patch_api_key(self):
        """User cannot patch api key"""
        user = User.objects.get(username=user_data.get('username'))
        key = user.keys.all().first()
        user2 = User.objects.get(username=user_error_data.get('username'))
        key2 = user2.keys.all().first()
        client = APIClient()
        client.login(
            username=user_data.get('username'),
            password=user_data.get('password'),
        )
        url = reverse('key-list')
        response = client.patch(
            f'{url}{key2.id}/',
            {'name': 'test'},
        )
        self.assertEqual(response.status_code, 404)


class ExchangeRateTestCase(TestCase):
    def setUp(self):
        """Set up"""
        self.user = User.objects.create_user(**user_data)
        key = ApiKey.objects.create(
            user=self.user,
            name='app',
            api_key=str(uuid4()),
        )

    def test_user_can_get_exchange_rate_login(self):
        """User can get exchange rate login"""
        client = APIClient()
        client.login(
            username=user_data.get('username'),
            password=user_data.get('password'),
        )
        response = client.get(
            reverse('latest'),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = loads(response.content)
        self.assertEqual(data.get('provider_1').get('name'), 'dof')
        self.assertEqual(data.get('provider_2').get('name'), 'fixer')
        self.assertEqual(data.get('provider_3').get('name'), 'banxico')

    def test_user_can_get_exchange_rate_api_key(self):
        """User can get exchange rate api key"""
        key = ApiKey.objects.get(user=self.user)
        client = APIClient()
        token = f'Token {str(key.api_key)}'
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = client.get(
            reverse('latest'),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = loads(response.content)
        self.assertEqual(data.get('provider_1').get('name'), 'dof')
        self.assertEqual(data.get('provider_2').get('name'), 'fixer')
        self.assertEqual(data.get('provider_3').get('name'), 'banxico')

    def test_user_can_get_exchange_rate_api_key_param(self):
        """User can get exchange rate api key param"""
        key = ApiKey.objects.get(user=self.user)
        client = APIClient()
        url = reverse('latest')
        response = client.get(
            f'{url}?api_key={str(key.api_key)}',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = loads(response.content)
        self.assertEqual(data.get('provider_1').get('name'), 'dof')
        self.assertEqual(data.get('provider_2').get('name'), 'fixer')
        self.assertEqual(data.get('provider_3').get('name'), 'banxico')

    def test_user_can_get_exchange_rate_error(self):
        """User can get exchange rate error"""
        client = APIClient()
        response = client.get(
            reverse('latest'),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
