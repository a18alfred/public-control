from accounts.models import Account, Profile
from problems.models import Category, Problem, Signature
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from core.picture_compressor import create_test_image


class SignatureAPIViewsTestCase(APITestCase):
    """
    Тестирование Views API Signature
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
        self.profile = Profile.objects.get(account_id=self.super.id)
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
        self.simple_user1.save()

        self.email_simple2 = 'simple2@test.com'
        self.simple_user2 = Account.objects.create_user(self.email_simple2, self.password, phone_number='8145',
                                                        is_phone_confirmed=True)
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

    def test_sign_problem_view(self):
        """
        path: problems/sign/
        Тестируем оставление пользователем подписи под проблемой.
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

        resp = self.client.post(url, {'email': self.email_government, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_gov = resp.data['access']

        resp = self.client.post(url, {'email': self.email_mc, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token_mc = resp.data['access']

        client = APIClient()
        url = reverse('problems:problem_sign')

        data = {
            "problem": str(self.problem1.id),
            "account": str(self.simple_user1.id),
        }

        resp = client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        data = {
        }

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            "problem": str(self.problem1.id),
            "account": str(self.simple_user1.id),
        }

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            "problem": str(self.problem3.id),
            "account": str(self.simple_user2.id),
        }

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        data = {
            "problem": str(self.problem3.id),
            "account": str(self.simple_user1.id),
        }

        client.credentials(HTTP_AUTHORIZATION='JWT ' + token_simple)
        resp = client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
