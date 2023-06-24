from accounts.models import Account, Profile
from problems.models import Category, Problem, Picture
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from django.conf import settings
from PIL import Image
import tempfile
from core.picture_compressor import create_test_image


class PictureAPIViewsTestCase(APITestCase):
    """
    Тестирование Views API Picture
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

        self.test_category = Category.objects.create(name='test_category')
        self.problem1 = Problem.objects.create(category=self.test_category, description='description',
                                               account=self.super,
                                               region_iso='RU-ALT')
        self.problem2 = Problem.objects.create(category=self.test_category, description='description',
                                               account=self.simple_user1,
                                               region_iso='RU-ALT')
        self.problem3 = Problem.objects.create(category=self.test_category, description='description',
                                               account=self.simple_user1,
                                               region_iso='RU-ALT')

    def tearDown(self):
        self.problem1.delete()
        self.problem2.delete()
        self.problem3.delete()
        self.super.delete()
        self.user_moderator.delete()
        self.user_government.delete()
        self.user_mc.delete()
        self.simple_user1.delete()
        self.simple_user2.delete()
        self.test_category.delete()

    def test_picture_upload_view(self):
        """
        path: problems/picture/upload/
        Загрузка фотографии для проблемы.
        """

        url = reverse('accounts:jwt-create')

        resp = self.client.post(url, {'email': 'test4@test.com', 'password': 'asdasdl2@asAS'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_simple = resp.data['access']

        resp = self.client.post(url, {'email': 'test5@test.com', 'password': 'asdasdl2@asAS'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_simple2 = resp.data['access']

        resp = self.client.post(url, {'email': 'test1@test.com', 'password': 'asdasdl2@asAS'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_moderator = resp.data['access']

        resp = self.client.post(url, {'email': 'super@super.com', 'password': 'asdasdl2@asAS'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_super = resp.data['access']

        client = APIClient()
        url = reverse('problems:picture_upload')

        data = {
            "problem": str(self.problem2.id),
            "uploaded_picture": create_test_image()
        }

        resp = client.post(url, data, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        data = {
            "problem": str(self.problem2.id),
            "uploaded_picture": create_test_image()
        }

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.post(url, data, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = {
            "problem": str(self.problem2.id),
            "uploaded_picture": create_test_image()
        }

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple2)
        resp = client.post(url, data, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        data = {
            "problem": str(self.problem2.id),
            "uploaded_picture": create_test_image()
        }

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.post(url, data, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = {
            "problem": str(self.problem2.id),
            "uploaded_picture": create_test_image()
        }

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.post(url, data, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            "problem": str(self.problem3.id),
            "uploaded_picture": create_test_image()
        }

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_moderator)
        resp = client.post(url, data, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = {
            "problem": str(self.problem3.id),
            "uploaded_picture": create_test_image()
        }

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_super)
        resp = client.post(url, data, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = {
            "problem": str(self.problem3.id),
            "uploaded_picture": create_test_image()
        }

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_super)
        resp = client.post(url, data, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            "problem": str(self.problem1.id),
            "uploaded_picture": create_test_image()
        }

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.post(url, data, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_picture_delete_view(self):
        """
        path: problems/picture/update/<int:pk>/
        Тестируем удаление фотографии. Только для создателя проблемы, модератора и суперюзера
        """

        url = reverse('accounts:jwt-create')

        resp = self.client.post(url, {'email': 'test4@test.com', 'password': 'asdasdl2@asAS'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_simple = resp.data['access']

        resp = self.client.post(url, {'email': 'test5@test.com', 'password': 'asdasdl2@asAS'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_simple2 = resp.data['access']

        resp = self.client.post(url, {'email': 'test1@test.com', 'password': 'asdasdl2@asAS'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_moderator = resp.data['access']

        resp = self.client.post(url, {'email': 'super@super.com', 'password': 'asdasdl2@asAS'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_super = resp.data['access']

        client = APIClient()
        url = reverse('problems:picture_upload')

        data = {
            "problem": str(self.problem2.id),
            "uploaded_picture": create_test_image()
        }

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.post(url, data, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        pictureId_1 = resp.data['id']

        data = {
            "problem": str(self.problem2.id),
            "uploaded_picture": create_test_image()
        }

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.post(url, data, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        pictureId_2 = resp.data['id']

        url = reverse('problems:picture_update_delete', kwargs={'pk': pictureId_1})
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple2)
        resp = client.delete(url, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.delete(url, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        url = reverse('problems:picture_update_delete', kwargs={'pk': pictureId_1})
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.delete(url, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        url = reverse('problems:picture_update_delete', kwargs={'pk': pictureId_2})
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_super)
        resp = client.delete(url, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        data = {
            "problem": str(self.problem2.id),
            "uploaded_picture": create_test_image()
        }
        url = reverse('problems:picture_upload')
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.post(url, data, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        pictureId_3 = resp.data['id']

        url = reverse('problems:picture_update_delete', kwargs={'pk': pictureId_3})
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple2)
        resp = client.delete(url, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        url = reverse('problems:picture_update_delete', kwargs={'pk': pictureId_3})
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_moderator)
        resp = client.delete(url, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_picture_update_view(self):
        """
        path: problems/picture/update/<int:pk>/
        Тестируем обновление фотографии. Только для создателя проблемы, модератора и суперюзера
        """

        url = reverse('accounts:jwt-create')

        resp = self.client.post(url, {'email': 'test4@test.com', 'password': 'asdasdl2@asAS'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_simple = resp.data['access']

        resp = self.client.post(url, {'email': 'test5@test.com', 'password': 'asdasdl2@asAS'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_simple2 = resp.data['access']

        resp = self.client.post(url, {'email': 'test1@test.com', 'password': 'asdasdl2@asAS'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_moderator = resp.data['access']

        resp = self.client.post(url, {'email': 'super@super.com', 'password': 'asdasdl2@asAS'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_super = resp.data['access']

        client = APIClient()
        url = reverse('problems:picture_upload')

        data = {
            "problem": str(self.problem2.id),
            "uploaded_picture": create_test_image()
        }

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.post(url, data, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        pictureId_1 = resp.data['id']

        data = {
            "problem": str(self.problem2.id),
            "uploaded_picture": create_test_image()
        }

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.post(url, data, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        pictureId_2 = resp.data['id']

        url = reverse('problems:picture_update_delete', kwargs={'pk': pictureId_1})
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.put(url, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_moderator)
        resp = client.put(url, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_super)
        resp = client.put(url, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple2)
        resp = client.put(url, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.get(url, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.assertTrue(Problem.objects.prefetch_related('problem_picture'))

        data = {
            "uploaded_picture": create_test_image()
        }
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.patch(url, data, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = {
            "uploaded_picture": create_test_image()
        }
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_super)
        resp = client.patch(url, data, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = {
            "uploaded_picture": create_test_image()
        }
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_moderator)
        resp = client.patch(url, data, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = {
            "uploaded_picture": create_test_image()
        }
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple2)
        resp = client.patch(url, data, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        url = reverse('problems:picture_update_delete', kwargs={'pk': '24ff0a1d-b38e-472c-9ee5-35a5b396ce21'})
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.delete(url, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
