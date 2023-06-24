from django.test import TestCase
from problems.models import Problem, Category
from accounts.models import Account, Profile
from core.picture_compressor import create_test_image


class CategoryModelTestCase(TestCase):

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
        self.super = Account.objects.create_superuser(email=email, password=password, phone_number='8141',
                                                      is_phone_confirmed=True)
        self.profile = Profile.objects.get(account_id=self.super.id)
        self.profile.region_iso = 'RU-ALT'
        self.profile.save()

        email1 = 'test1@test.com'
        self.user_moderator = Account.objects.create_user(email1, password, phone_number='8142',
                                                          is_phone_confirmed=True)
        self.user_moderator.is_moderator = True
        self.user_moderator.is_active = True
        self.user_moderator.save()

        email2 = 'test2@test.com'
        self.user_government = Account.objects.create_user(email2, password, phone_number='8143',
                                                           is_phone_confirmed=True)
        self.user_government.is_government = True
        self.user_government.is_active = True
        self.user_government.save()

        email3 = 'test3@test.com'
        self.user_mc = Account.objects.create_user(email3, password, phone_number='8144', is_phone_confirmed=True)
        self.user_mc.is_management_company = True
        self.user_mc.is_active = True
        self.user_mc.save()

        email4 = 'test4@test.com'
        self.simple_user1 = Account.objects.create_user(email4, password, phone_number='8145', is_phone_confirmed=True)
        self.simple_user1.is_active = True
        self.simple_user1.save()

        email5 = 'test5@test.com'
        self.simple_user2 = Account.objects.create_user(email5, password, phone_number='8146', is_phone_confirmed=True)
        self.simple_user2.is_active = True
        self.simple_user2.save()

        self.test_category = Category.objects.create(name='test_category')
        self.test_category.save()
        self.test_category2 = Category.objects.create(name='test_category2', icon=create_test_image())
        self.test_category2.save()
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
        self.test_category2.delete()

    def test_category_str(self):
        """
        Тестируем __str__ модели категория
        """
        name = 'test'
        category = Category.objects.create(name=name)
        self.assertEqual(category.__str__(), name)

    def test_category_slug(self):
        """
        Тестируем автогенерацию slug модели категория
        """
        name = 'test'
        category = Category.objects.create(name=name)
        category.save()
        self.assertTrue(category.slug)

    def test_category_default_icon(self):
        """
        Тестируем дефолтную иконку после удаления иконки у категории
        """
        self.assertEqual(self.test_category.icon, 'categories/default_category_icon.png')
        self.assertNotEqual(self.test_category2.icon, 'categories/default_category_icon.png')
        self.test_category2.icon = ''
        self.test_category2.save()

        self.assertEqual(self.test_category2.icon, 'categories/default_category_icon.png')
