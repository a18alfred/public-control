from accounts.models import Account, Profile
from problems.models import Category, Problem, Assignment, Signature
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient


class ProblemAPIViewsTestCase(APITestCase):
    """
    Тестирование Views API Problem
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
        self.password = 'asdasdl2@asAS'

        self.email_super = 'super@super.com'
        self.super = Account.objects.create_superuser(email=self.email_super, password=self.password,
                                                      phone_number='8140', is_phone_confirmed=True)
        self.profile = Profile.objects.get(account=self.super)
        self.profile.region_iso = 'RU-ALT'
        self.profile.save()

        self.email_moderator = 'moderator@test.com'
        self.user_moderator = Account.objects.create_user(self.email_moderator, self.password, phone_number='8141',
                                                          is_phone_confirmed=True)
        self.user_moderator.is_moderator = True
        self.user_moderator.is_active = True
        self.user_moderator.save()

        self.email_government = 'government@test.com'
        self.user_government = Account.objects.create_user(self.email_government, self.password, phone_number='8142',
                                                           is_phone_confirmed=True)
        self.user_government.is_government = True
        self.user_government.is_active = True
        self.user_government.save()

        self.email_mc = 'mc@test.com'
        self.user_mc = Account.objects.create_user(self.email_mc, self.password, phone_number='8143',
                                                   is_phone_confirmed=True)
        self.user_mc.is_management_company = True
        self.user_mc.is_active = True
        self.user_mc.save()

        self.email_simple1 = 'simple1@test.com'
        self.simple_user1 = Account.objects.create_user(self.email_simple1, self.password, phone_number='8144',
                                                        is_phone_confirmed=True)
        self.simple_user1.is_active = True
        self.profile = Profile.objects.get(account=self.simple_user1)
        self.profile.region_iso = 'RU-ALT'
        self.profile.save()
        self.simple_user1.save()

        self.email_simple2 = 'simple2@test.com'
        self.simple_user2 = Account.objects.create_user(self.email_simple2, self.password, phone_number='8145',
                                                        is_phone_confirmed=True)
        self.simple_user2.is_active = True
        self.profile = Profile.objects.get(account=self.simple_user2)
        self.profile.region_iso = 'RU-ALT'
        self.profile.save()
        self.simple_user2.save()

        self.test_category = Category.objects.create(name='test_category')
        self.problem = Problem.objects.create(category=self.test_category, description='description',
                                              account=self.super,
                                              region_iso='RU-ALT', is_published=True)

        self.problem1 = Problem.objects.create(category=self.test_category, description='description',
                                               account=self.super,
                                               region_iso='RU-ALT', is_published=True)
        self.problem2 = Problem.objects.create(category=self.test_category, description='description',
                                               account=self.simple_user1,
                                               region_iso='RU-ALT', is_published=True)
        self.problem3 = Problem.objects.create(category=self.test_category, description='description',
                                               account=self.simple_user1,
                                               region_iso='RU-ALT', is_published=True)
        self.problem4 = Problem.objects.create(category=self.test_category, description='description',
                                               account=self.simple_user1,
                                               region_iso='RU-ALT', is_published=True)

    def tearDown(self):
        self.super.delete()
        self.user_moderator.delete()
        self.user_government.delete()
        self.user_mc.delete()
        self.simple_user1.delete()
        self.simple_user2.delete()
        self.test_category.delete()
        self.problem.delete()
        self.problem1.delete()
        self.problem2.delete()
        self.problem3.delete()
        self.problem4.delete()

    def test_problem_detail_view(self):
        """
        path: problems/<int:pk>/
        Получение детальной информации о проблеме
        """

        url = reverse('problems:problem_detail', kwargs={'pk': self.problem.id})
        client = APIClient()
        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = client.delete(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        url = reverse('problems:problem_detail', kwargs={'pk': '24ff0a1d-b38e-472c-9ee5-35a5b396ce21'})
        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_problem_create(self):
        """
        path: problems/create/
        Для любого зарегистрированного пользователя
        """
        url = reverse('accounts:jwt-create')

        resp = self.client.post(url, {'email': self.email_simple1, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token = resp.data['access']

        client = APIClient()
        url = reverse('problems:problem_create')

        data = {
            "description": "description",
            "region_iso": "RU-ALT",
            "category": str(self.test_category.id)
        }
        resp = client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token)

        data = {
            "description": "description",
            "region_iso": "RU-UD",
            "category": str(self.test_category.id)
        }
        resp = client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            "description": "description",
            "region_iso": "RU-ALT",
            "category": str(self.test_category.id)
        }
        resp = client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = {
            "description": "description",
            "region_iso": "RU-ALT",
        }
        resp = client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_problem_delete(self):
        """
        path: problems/delete/<int:pk>/
        403 - если не создатель пролблемы, не модератор или не суперюзер
        """
        url = reverse('accounts:jwt-create')

        resp = self.client.post(url, {'email': self.email_simple1, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_simple = resp.data['access']

        resp = self.client.post(url, {'email': self.email_simple2, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_simple2 = resp.data['access']

        resp = self.client.post(url, {'email': self.email_moderator, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_moderator = resp.data['access']

        resp = self.client.post(url, {'email': self.email_super, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_super = resp.data['access']

        client = APIClient()
        url = reverse('problems:problem_delete', kwargs={'pk': self.problem2.id})

        resp = client.delete(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple2)
        resp = client.delete(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        url = reverse('problems:problem_delete', kwargs={'pk': self.problem1.id})
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple2)
        resp = client.delete(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        url = reverse('problems:problem_delete', kwargs={'pk': self.problem2.id})
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.delete(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        url = reverse('problems:problem_delete', kwargs={'pk': self.problem3.id})
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_super)
        resp = client.delete(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        url = reverse('problems:problem_delete', kwargs={'pk': self.problem4.id})
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_moderator)
        resp = client.delete(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        url = reverse('problems:problem_delete', kwargs={'pk': '24ff0a1d-b38e-472c-9ee5-35a5b396ce21'})
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_moderator)
        resp = client.delete(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_problem_closed_by_owner_view(self):
        """
        path: problems/close/<int:pk>/
        Закрыть в данном view может только пользователь
        """
        url = reverse('accounts:jwt-create')

        resp = self.client.post(url, {'email': self.email_simple1, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_simple = resp.data['access']

        resp = self.client.post(url, {'email': self.email_simple2, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_simple2 = resp.data['access']

        resp = self.client.post(url, {'email': self.email_moderator, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_moderator = resp.data['access']

        resp = self.client.post(url, {'email': self.email_super, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_super = resp.data['access']

        client = APIClient()
        url = reverse('problems:problem_close_by_owner', kwargs={'pk': self.problem2.id})

        data = {
            "status": "in_progress"
        }

        resp = client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_super)
        resp = client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple2)
        resp = client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        data = {
            "status": "closed"
        }

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = {
            "status": "closed"
        }

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.put(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        data = {
            "status": "asdasdasd"
        }

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
        }

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            "status": "closed"
        }
        url = reverse('problems:problem_close_by_owner', kwargs={'pk': '24ff0a1d-b38e-472c-9ee5-35a5b396ce21'})
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_problem_update_status_by_responder_view(self):
        """
        path: problems/updatestatus/<int:pk>/
        Тестируем изменение статуса на проблемы на i_progress или completed.
        Поменять может представитель УК или власти.
        """
        url = reverse('accounts:jwt-create')

        resp = self.client.post(url, {'email': self.email_simple1, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_simple = resp.data['access']

        resp = self.client.post(url, {'email': self.email_simple2, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_simple2 = resp.data['access']

        resp = self.client.post(url, {'email': self.email_government, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_gov = resp.data['access']

        resp = self.client.post(url, {'email': self.email_mc, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_mc = resp.data['access']

        client = APIClient()
        url = reverse('problems:problem_update_status_by_responder', kwargs={'pk': self.problem2.id})

        data = {
            "status": "closed"
        }

        resp = client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple2)
        resp = client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_gov)
        resp = client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        data = {
        }

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_gov)
        resp = client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            "status": "in_progress"
        }

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_gov)
        resp = client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = {
            "status": "completed"
        }

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_mc)
        resp = client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = {
            "status": "completed"
        }

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_mc)
        resp = client.put(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        url = reverse('problems:problem_update_status_by_responder',
                      kwargs={'pk': '24ff0a1d-b38e-472c-9ee5-35a5b396ce21'})
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_mc)
        resp = client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_problem_super_update_view(self):
        """
        path: problems/superupdate/<int:pk>/
        Тестируем внесение глобальных изменений в проблему. Действие доступно только суперюзеру
        """
        url = reverse('accounts:jwt-create')

        resp = self.client.post(url, {'email': self.email_simple1, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_simple = resp.data['access']

        resp = self.client.post(url, {'email': self.email_simple2, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_simple2 = resp.data['access']

        resp = self.client.post(url, {'email': self.email_government, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_gov = resp.data['access']

        resp = self.client.post(url, {'email': self.email_moderator, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_moderator = resp.data['access']

        resp = self.client.post(url, {'email': self.email_super, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_super = resp.data['access']

        client = APIClient()
        url = reverse('problems:problem_super_update', kwargs={'pk': self.problem2.id})

        data = {
            "description": "test",
            "addressFull": "test address"
        }

        resp = client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple2)
        resp = client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_gov)
        resp = client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_super)
        resp = client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_super)
        resp = client.put(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            "description": "test",
            "addressFull": "test address",
            "region_iso": "RU-ALT"
        }
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_super)
        resp = client.put(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        url = reverse('problems:problem_super_update', kwargs={'pk': '24ff0a1d-b38e-472c-9ee5-35a5b396ce21'})
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_super)
        resp = client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_problem_moderator_update_view(self):
        """
        path: problems/update/<int:pk>/
        Тестируем изменение статуса и категории проблемы. Только для модератора или суперюзера
        """
        url = reverse('accounts:jwt-create')

        resp = self.client.post(url, {'email': self.email_simple1, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_simple = resp.data['access']

        resp = self.client.post(url, {'email': self.email_simple2, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_simple2 = resp.data['access']

        resp = self.client.post(url, {'email': self.email_mc, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_mc = resp.data['access']

        resp = self.client.post(url, {'email': self.email_moderator, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_moderator = resp.data['access']

        resp = self.client.post(url, {'email': self.email_super, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_super = resp.data['access']

        client = APIClient()
        url = reverse('problems:problem_moderator_update', kwargs={'pk': self.problem2.id})

        data = {
            "status": "closed",
        }

        resp = client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple2)
        resp = client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_mc)
        resp = client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_moderator)
        resp = client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_moderator)
        resp = client.put(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        data = {
            "category": str(self.test_category.id),
            "status": "in_progress"
        }

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_super)
        resp = client.put(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_super)
        resp = client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        url = reverse('problems:problem_moderator_update', kwargs={'pk': '24ff0a1d-b38e-472c-9ee5-35a5b396ce21'})
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_super)
        resp = client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_problem_user_created_list(self):
        """
        path: problems/mylist/
        Тестируем получение списка всех проблем созданных пользователем
        """
        url = reverse('accounts:jwt-create')

        resp = self.client.post(url, {'email': self.email_simple1, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_simple = resp.data['access']

        resp = self.client.post(url, {'email': self.email_simple2, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_simple2 = resp.data['access']

        url = reverse('problems:problem_user_created')
        client = APIClient()

        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple2)
        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_problem_user_signed_list(self):
        """
        path: problems/mysigned/
        Тестируем получение списка всех проблем подписанных пользователем
        """
        url = reverse('accounts:jwt-create')

        resp = self.client.post(url, {'email': self.email_simple1, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_simple = resp.data['access']

        resp = self.client.post(url, {'email': self.email_simple2, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_simple2 = resp.data['access']

        url = reverse('problems:problem_user_signed')
        client = APIClient()

        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple2)
        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_is_signed_is_assigned_api_service(self):
        """
        Тестируем is_signed и is_assigned параметры возвращаемые серсвером о проблеме
        """
        url = reverse('accounts:jwt-create')

        resp = self.client.post(url, {'email': self.email_moderator, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_moderator = resp.data['access']

        resp = self.client.post(url, {'email': self.email_super, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_super = resp.data['access']

        url = reverse('problems:problem_detail', kwargs={'pk': self.problem2.id})
        client = APIClient()
        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        is_signed = resp.data['is_signed']
        is_assigned = resp.data['is_assigned']

        self.assertFalse(is_signed)
        self.assertFalse(is_assigned)

        s1 = Signature.objects.create(account=self.user_moderator, problem=self.problem2)
        a1 = Assignment.objects.create(account=self.user_moderator, problem=self.problem2)

        expected_str = 'problem: ' + str(self.problem2.id) + ', email: ' + str(self.email_moderator)
        self.assertEqual(s1.__str__(), expected_str)
        self.assertEqual(a1.__str__(), expected_str)

        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        is_signed = resp.data['is_signed']
        is_assigned = resp.data['is_assigned']

        self.assertFalse(is_signed)
        self.assertFalse(is_assigned)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_super)
        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        is_signed = resp.data['is_signed']
        is_assigned = resp.data['is_assigned']

        self.assertFalse(is_signed)
        self.assertFalse(is_assigned)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_moderator)
        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        is_signed = resp.data['is_signed']
        is_assigned = resp.data['is_assigned']

        self.assertTrue(is_signed)
        self.assertTrue(is_assigned)

        s1.delete()
        a1.delete()

    def test_problem_user_assigned_list_view(self):
        """
        path: problems/myassigned/
        Тестируем получение списка всех проблем назначенных пользователю (только для модератора и представителя)
        """
        url = reverse('accounts:jwt-create')

        resp = self.client.post(url, {'email': self.email_simple1, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_simple = resp.data['access']

        resp = self.client.post(url, {'email': self.email_moderator, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_moderator = resp.data['access']

        resp = self.client.post(url, {'email': self.email_super, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_super = resp.data['access']

        url = reverse('problems:problem_user_assigned')
        client = APIClient()

        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_moderator)
        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        assigned_count = resp.data['count']
        self.assertEqual(assigned_count, 0)

        a1 = Assignment.objects.create(account=self.user_moderator, problem=self.problem2)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_moderator)
        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        assigned_count = resp.data['count']
        self.assertEqual(assigned_count, 1)

        a1.delete()

    def test_problem_to_moderate_list_view(self):
        """
        path: problems/tomoderate/
        Тестируем получение списка всех проблем, которые должны пройти модерацию.
        Только для модератора и суперюзера
        """
        url = reverse('accounts:jwt-create')

        resp = self.client.post(url, {'email': self.email_simple1, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_simple = resp.data['access']

        resp = self.client.post(url, {'email': self.email_government, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_gov = resp.data['access']

        resp = self.client.post(url, {'email': self.email_moderator, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_moderator = resp.data['access']

        resp = self.client.post(url, {'email': self.email_super, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_super = resp.data['access']

        url = reverse('problems:problem_to_moderate_list')
        client = APIClient()

        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_gov)
        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_moderator)
        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_super)
        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_problem_published_list_view(self):
        """
        path: problems/all/
        Тестируем получение списка всех проблем, которые были опубликованы
        """
        url = reverse('accounts:jwt-create')

        resp = self.client.post(url, {'email': self.email_simple1, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_simple = resp.data['access']

        url = reverse('problems:problem_all_list')
        client = APIClient()

        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.post(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_problem_published_ymap_list_view(self):
        """
        path: problems/ymaplist/
        Тестируем получение списка всех проблем, которые были опубликованы. Лист для карты
        """
        url = reverse('accounts:jwt-create')

        resp = self.client.post(url, {'email': self.email_simple1, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_simple = resp.data['access']

        url = reverse('problems:problem_yandex_map_list')
        client = APIClient()

        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.assertEqual(resp.data[0]['type'], 'Feature')
        self.assertTrue(resp.data[0]['geometry'])
        self.assertTrue(resp.data[0]['properties'])

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # self.assertContains(resp.data['type'], 'Feature')

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.post(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_problem_yandex_map_balloon_view(self):
        """
        path: problems/ymapballoon/<uuid:pk>/
        Тестируем получения краткой информации по проблеме для яндекс балуна
        """

        url = reverse('problems:problem_yandex_map_balloon', kwargs={'pk': self.problem.id})
        client = APIClient()
        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = client.delete(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        url = reverse('problems:problem_detail', kwargs={'pk': '24ff0a1d-b38e-472c-9ee5-35a5b396ce21'})
        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_statistics_view(self):
        """
        path: problems/stats/
        Тестируем получение списка статистики
        """
        url = reverse('problems:get_stats')
        client = APIClient()

        self.problem1.status = 'active'
        self.problem1.save()

        resp = client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        expected_count = Problem.objects.filter(is_published=True).count()
        self.assertEqual(expected_count, resp.data['total'])

        resp = client.post(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
