from accounts.models import Account, Profile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient


class AccountsViewsTestCase(APITestCase):
    """
    Тестирование Views
    """

    def setUp(self):
        """
        Создаём пользователей с разными правами:
        СуперЮзер
        Модератор
        Представитель власти
        Представитель УК
        Обычный пользователь
        """
        password = 'asdasdl2@asAS'

        email = 'super@super.com'
        self.super = Account.objects.create_superuser(email=email, password=password, phone_number='8133',
                                                      is_phone_confirmed=True)
        self.super.account_profile.region_iso = 'RU-ALT'
        self.super.account_profile.save()

        email1 = 'test1@test.com'
        self.user_moderator = Account.objects.create_user(email1, password, phone_number='8134',
                                                          is_phone_confirmed=True)
        self.user_moderator.is_moderator = True
        self.user_moderator.is_active = True
        self.user_moderator.save()

        email2 = 'test2@test.com'
        self.user_government = Account.objects.create_user(email2, password, phone_number='8135',
                                                           is_phone_confirmed=True)
        self.user_government.is_government = True
        self.user_government.is_active = True
        self.user_government.save()

        email3 = 'test3@test.com'
        self.user_mc = Account.objects.create_user(email3, password, phone_number='8136', is_phone_confirmed=True)
        self.user_mc.is_management_company = True
        self.user_mc.is_active = True
        self.user_mc.save()

        email4 = 'test4@test.com'
        self.simple_user1 = Account.objects.create_user(email4, password, phone_number='8137', is_phone_confirmed=True)
        self.simple_user1.is_active = True
        self.simple_user1.save()

        email5 = 'test5@test.com'
        self.simple_user2 = Account.objects.create_user(email5, password, phone_number='8138', is_phone_confirmed=True)
        self.simple_user2.is_active = True
        self.simple_user2.save()

    def tearDown(self):
        self.super.delete()
        self.user_moderator.delete()
        self.user_government.delete()
        self.user_mc.delete()
        self.simple_user1.delete()
        self.simple_user2.delete()

    def test_successful_jwt_auth(self):
        """
        Тестируем авторизацию пользователя и получние JWT токенов
        """
        client = APIClient()
        url = reverse('accounts:jwt-create')

        resp = self.client.post(url, {'email': 'super@super.com', 'password': 'asdasdl2@asAS'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in resp.data)
        self.assertTrue('refresh' in resp.data)

    def test_view_accounts_list_only_for_superuser(self):
        """
        path: accounts/all/
        Тестируем получение списка всех пользователей
        Список может получить только superuser
        Остальные пользователи получат 401 ошибку
        """
        url = reverse('accounts:jwt-create')

        resp = self.client.post(url, {'email': 'super@super.com', 'password': 'asdasdl2@asAS'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token = resp.data['access']

        url = reverse('accounts:accounts_list')
        resp = self.client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='JWT ' + 'abc')
        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_view_accounts_list_403_for_not_superuser(self):
        """
        path: accounts/all/
        Тестируем получение списка всех пользователей
         403 если не superuser
        """
        url = reverse('accounts:jwt-create')

        resp = self.client.post(url, {'email': 'test4@test.com', 'password': 'asdasdl2@asAS'}, format='json')
        token = resp.data['access']
        data = {
            "is_moderator": True,
        }
        url = reverse('accounts:accounts_list')
        simple_client = APIClient()
        simple_client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        resp = simple_client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_view_account_update_only_for_superuser(self):
        """
        path: accounts/update/<int:pk>/
        Тестируем обновление прав аккаунта. Только суперюзер имеет на это право.
        """
        url = reverse('accounts:jwt-create')

        resp = self.client.post(url, {'email': 'super@super.com', 'password': 'asdasdl2@asAS'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token = resp.data['access']
        data = {
            "is_moderator": True,
        }

        url = reverse('accounts:account_update', kwargs={'pk': self.user_moderator.id})
        resp = self.client.put(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        client = APIClient()

        client.credentials(HTTP_AUTHORIZATION='JWT ' + 'abc')
        resp = client.put(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        resp = client.put(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_view_account_update_403_for_not_superuser(self):
        """
        path: accounts/update/<int:pk>/
        Тестируем обновление прав аккаунта. 403 если не superuser
        """
        url = reverse('accounts:jwt-create')

        resp = self.client.post(url, {'email': 'test4@test.com', 'password': 'asdasdl2@asAS'}, format='json')
        token = resp.data['access']
        data = {
            "is_moderator": True,
        }
        url = reverse('accounts:account_update', kwargs={'pk': self.user_moderator.id})
        simple_client = APIClient()
        simple_client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        resp = simple_client.put(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_view_account_delete_only_for_superuser(self):
        """
        path: accounts/delete/<int:pk>/
        Тестируем удаление аккаунта. Только суперюзер имеет на это право.
        """
        url = reverse('accounts:jwt-create')

        resp = self.client.post(url, {'email': 'super@super.com', 'password': 'asdasdl2@asAS'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token = resp.data['access']

        url = reverse('accounts:account_delete', kwargs={'pk': self.user_moderator.id})
        resp = self.client.delete(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        client = APIClient()

        client.credentials(HTTP_AUTHORIZATION='JWT ' + 'abc')
        resp = client.delete(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        resp = client.delete(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_view_account_delete_403_for_not_superuser(self):
        """
        path: accounts/update/<int:pk>/
        Тестируем удаление аккаунта. 403 если не superuser
        """
        url = reverse('accounts:jwt-create')

        resp = self.client.post(url, {'email': 'test4@test.com', 'password': 'asdasdl2@asAS'}, format='json')
        token = resp.data['access']

        url = reverse('accounts:account_delete', kwargs={'pk': self.user_moderator.id})
        simple_client = APIClient()
        simple_client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        resp = simple_client.delete(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_view_profile_detail_only_for_owner_or_superuser(self):
        """
        path: profile/<int:pk>/
        Тестируем получение детального профайла.
        Может получить только владелец аккаунта(owner) или superuser
        Остальные пользователи получат 403 ошибку
        """
        url = reverse('accounts:jwt-create')

        resp = self.client.post(url, {'email': 'super@super.com', 'password': 'asdasdl2@asAS'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_super = resp.data['access']

        resp = self.client.post(url, {'email': 'test1@test.com', 'password': 'asdasdl2@asAS'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_owner = resp.data['access']

        resp = self.client.post(url, {'email': 'test2@test.com', 'password': 'asdasdl2@asAS'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_stranger = resp.data['access']

        url = reverse('accounts:profile_detail', kwargs={'pk': self.user_moderator.id})
        resp = self.client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='JWT ' + 'abc')
        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_super)
        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_owner)
        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_stranger)
        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        url = reverse('accounts:profile_detail', kwargs={'pk': '24ff0a1d-b38e-472c-9ee5-35a5b396ce21'})
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_owner)
        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_view_profile_update_only_for_owner_or_superuser(self):
        """
        path: profile/update/<int:pk>/
        Тестируем внесение изменений профайла.
        Может произвести только владелец аккаунта(owner) или superuser
        Остальные пользователи получат 403 ошибку
        """
        url = reverse('accounts:jwt-create')

        resp = self.client.post(url, {'email': 'super@super.com', 'password': 'asdasdl2@asAS'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_super = resp.data['access']

        resp = self.client.post(url, {'email': 'test1@test.com', 'password': 'asdasdl2@asAS'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_owner = resp.data['access']

        resp = self.client.post(url, {'email': 'test2@test.com', 'password': 'asdasdl2@asAS'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_stranger = resp.data['access']

        data = {
            "first_name": "test",
        }

        url = reverse('accounts:profile_update', kwargs={'pk': self.user_moderator.id})
        resp = self.client.put(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='JWT ' + 'abc')
        resp = client.put(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_super)
        resp = client.put(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_owner)
        resp = client.put(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_stranger)
        resp = client.put(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        url = reverse('accounts:profile_update', kwargs={'pk': '24ff0a1d-b38e-472c-9ee5-35a5b396ce21'})
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_super)
        resp = client.put(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_blacklist_token_view(self):
        """
        path: auth/logout/blacklist/
        Тестируем внесение в черный список refresh token.

        """
        url = reverse('accounts:jwt-create')

        resp = self.client.post(url, {'email': 'super@super.com', 'password': 'asdasdl2@asAS'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        refresh = resp.data['refresh']

        data = {
            "refresh": refresh
        }

        client = APIClient()

        url = reverse('accounts:jwt-refresh')

        client.credentials(HTTP_AUTHORIZATION='')
        resp = client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        refresh = resp.data['refresh']

        data = {
            "refresh": refresh
        }

        url = reverse('accounts:blacklist')

        client.credentials(HTTP_AUTHORIZATION='')
        resp = client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_205_RESET_CONTENT)

        client.credentials(HTTP_AUTHORIZATION='')
        resp = client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
