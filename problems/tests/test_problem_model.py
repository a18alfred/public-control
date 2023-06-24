from django.test import TestCase
from problems.models import Problem, Category, Signature
from accounts.models import Account, Profile


class ProblemModelTestCase(TestCase):

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
        self.super = Account.objects.create_superuser(email=email, password=password, phone_number='8144',
                                                      is_phone_confirmed=True)
        self.profile = Profile.objects.get(account_id=self.super.id)
        self.profile.region_iso = 'RU-ALT'
        self.profile.save()

        email1 = 'test1@test.com'
        self.user_moderator = Account.objects.create_user(email1, password, phone_number='8143',
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
        self.user_mc = Account.objects.create_user(email3, password, phone_number='8141', is_phone_confirmed=True)
        self.user_mc.is_management_company = True
        self.user_mc.is_active = True
        self.user_mc.save()

        email4 = 'test4@test.com'
        self.simple_user1 = Account.objects.create_user(email4, password, phone_number='8140', is_phone_confirmed=True)
        self.simple_user1.is_active = True
        self.simple_user1.save()

        email5 = 'test5@test.com'
        self.simple_user2 = Account.objects.create_user(email5, password, phone_number='8139', is_phone_confirmed=True)
        self.simple_user2.is_active = True
        self.simple_user2.save()

        self.test_category = Category.objects.create(name='test_category')
        self.problem1 = Problem.objects.create(category=self.test_category, description='description',
                                               account=self.super,
                                               region_iso='RU-ALT', status='under_review')
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

    def test_problem_str(self):
        """
        Тестируем __str__ модели проблема
        """
        expected = str(self.problem1.id) + ' ' + str(self.problem1.dateCreated.date())
        self.assertEqual(self.problem1.__str__(), expected)

    def test_default_problem_status_after_creation(self):
        """
        Тестируем начальный статус после создания проблемы. Какой бы его не ввели, изначально он будет равен 'created'
        """
        self.assertEqual(self.problem1.status, 'created')

    def test_signature_count(self):
        """
        Тестируем получение колличества подписей под проблемой
        """
        s1 = Signature.objects.create(problem=self.problem1, account=self.simple_user1)
        s2 = Signature.objects.create(problem=self.problem1, account=self.simple_user2)

        s3 = Signature.objects.create(problem=self.problem2, account=self.simple_user2)

        self.assertEqual(self.problem1.signature_count, 2)
        self.assertEqual(self.problem2.signature_count, 1)

        s1.delete()

        self.assertEqual(self.problem1.signature_count, 1)
