from accounts.models import Account, Profile
from problems.models import Category, Problem
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient


class CategoryAPIViewsTestCase(APITestCase):
    """
    Тестирование Views API Category
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
        self.super = Account.objects.create_superuser(email=email, password=password, phone_number='8140',
                                                      is_phone_confirmed=True)
        self.profile = Profile.objects.get(account_id=self.super.id)
        self.profile.region_iso = 'RU-ALT'
        self.profile.save()

        email1 = 'test1@test.com'
        self.user_moderator = Account.objects.create_user(email1, password, phone_number='8141',
                                                          is_phone_confirmed=True)
        self.user_moderator.is_moderator = True
        self.user_moderator.is_active = True
        self.user_moderator.save()

        email2 = 'test2@test.com'
        self.user_government = Account.objects.create_user(email2, password, phone_number='8142',
                                                           is_phone_confirmed=True)
        self.user_government.is_government = True
        self.user_government.is_active = True
        self.user_government.save()

        email3 = 'test3@test.com'
        self.user_mc = Account.objects.create_user(email3, password, phone_number='8143', is_phone_confirmed=True)
        self.user_mc.is_management_company = True
        self.user_mc.is_active = True
        self.user_mc.save()

        email4 = 'test4@test.com'
        self.simple_user1 = Account.objects.create_user(email4, password, phone_number='8144', is_phone_confirmed=True)
        self.simple_user1.is_active = True
        self.simple_user1.save()

        email5 = 'test5@test.com'
        self.simple_user2 = Account.objects.create_user(email5, password, phone_number='8145', is_phone_confirmed=True)
        self.simple_user2.is_active = True
        self.simple_user2.save()

        self.category1 = Category.objects.create(name='test1_parent')
        self.category2 = Category.objects.create(name='test2_parent')
        self.category3 = Category.objects.create(name='test3_parent')

        self.category4 = Category.objects.create(name='test1_child', parent=self.category1)
        self.category5 = Category.objects.create(name='test2_child', parent=self.category2)
        self.category6 = Category.objects.create(name='test3_child', parent=self.category4)

    def tearDown(self):
        self.super.delete()
        self.user_moderator.delete()
        self.user_government.delete()
        self.user_mc.delete()
        self.simple_user1.delete()
        self.simple_user2.delete()

    def test_categories_all_list(self):
        """
        path: categories/all/
        Получение списка (дерева) для всех категорий
        """
        url = reverse('problems:category_tree')
        client = APIClient()
        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.content)
        resp = client.delete(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_categories_create(self):
        """
        path: categories/create/
        Только для superuser
        Тестируем создание новой категорий. 403 если не superuser
        """
        url = reverse('accounts:jwt-create')

        resp = self.client.post(url, {'email': 'super@super.com', 'password': 'asdasdl2@asAS'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token = resp.data['access']

        client = APIClient()
        url = reverse('problems:category_create')
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        data = {
            "name": "test",
        }
        resp = client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        resp = client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
        }
        resp = client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        resp = client.delete(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        url = reverse('accounts:jwt-create')
        resp = self.client.post(url, {'email': 'test4@test.com', 'password': 'asdasdl2@asAS'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token = resp.data['access']

        url = reverse('problems:category_create')
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        data = {
            "name": "test",
        }
        resp = client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        anon_client = APIClient()
        resp = anon_client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_category_update_delete(self):
        """
        path: categories/<int:pk>/
        Только для superuser
        Тестируем удаление и изменение категории. 403 если не superuser
        """
        url = reverse('accounts:jwt-create')

        resp = self.client.post(url, {'email': 'super@super.com', 'password': 'asdasdl2@asAS'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token = resp.data['access']

        client = APIClient()
        url = reverse('problems:category_create')
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        data = {
            "name": "test",
        }
        resp = client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = {
            "name": "test2",
        }
        resp = client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = {
            "name": "test_rename",
        }
        url = reverse('problems:category_update_delete', kwargs={'pk': self.category1.id})
        resp = client.put(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        cat1_id = self.category1.id
        url = reverse('problems:category_update_delete', kwargs={'pk': cat1_id})
        resp = client.delete(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        url = reverse('problems:category_update_delete', kwargs={'pk': cat1_id})
        resp = client.delete(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        url = reverse('accounts:jwt-create')
        resp = self.client.post(url, {'email': 'test4@test.com', 'password': 'asdasdl2@asAS'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token = resp.data['access']

        url = reverse('problems:category_update_delete', kwargs={'pk': self.category2.id})
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        resp = client.put(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        anon_client = APIClient()
        resp = anon_client.put(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
