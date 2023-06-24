from django.test import TestCase
from accounts.managers import CustomUserManager
from accounts.models import Account


class CustomUserManagerTestCase(TestCase):
    """
    Тестируем CustomUserManager
    """

    def test_create_user(self):
        """
        Создание обычного пользователя
        """
        email_lowercase = 'normal@normal.com'
        password = 'asdasdl2@asAS'
        user = Account.objects.create_user(email=email_lowercase, password=password, phone_number='8129',
                                           is_phone_confirmed=True)
        self.assertEqual(user.email, email_lowercase)
        self.assertTrue(user.has_usable_password())

    def test_create_user_without_email(self):
        """
        Создание обычного пользователя без email. Должны получить ошибку.
        """
        email_lowercase = ''
        password = 'asdasdl2@asAS'
        with self.assertRaisesMessage(ValueError, 'The Email must be set'):
            user = Account.objects.create_user(email=email_lowercase, password=password, phone_number='8129',
                                               is_phone_confirmed=True)

    def test_create_user_email_domain_normalize_rfc3696(self):
        # According to https://tools.ietf.org/html/rfc3696#section-3
        # the "@" symbol can be part of the local part of an email address
        returned = CustomUserManager.normalize_email(r'Abc\@DEF@EXAMPLE.com')
        self.assertEqual(returned, r'Abc\@DEF@example.com')

    def test_create_user_email_domain_normalize(self):
        returned = CustomUserManager.normalize_email('normal@DOMAIN.COM')
        self.assertEqual(returned, 'normal@domain.com')

    def test_create_user_email_domain_normalize_with_whitespace(self):
        returned = CustomUserManager.normalize_email(r'email\ with_whitespace@D.COM')
        self.assertEqual(returned, r'email\ with_whitespace@d.com')

    def test_create_user_is_staff(self):
        email = 'normal@normal.com'
        password = 'asdasdl2@asAS'
        user = Account.objects.create_user(email, password, is_staff=True, phone_number='8130', is_phone_confirmed=True)
        self.assertEqual(user.email, email)
        self.assertTrue(user.is_staff)

    def test_create_super_user_raises_error_on_false_is_superuser(self):
        with self.assertRaisesMessage(ValueError, 'Superuser должен иметь is_superuser=True.'):
            Account.objects.create_superuser(email='test@test.com', password='test', is_superuser=False,
                                             phone_number='8131', is_phone_confirmed=True)

    def test_create_superuser_must_be_true_is_staff_is_superuser_is_active_is_moderator_is_government_is_management_company_is_phone_confirmed(
            self):
        """
        Тестируем создание superuser со всеми правами.
        """
        email = 'normal@normal.com'
        password = 'asdasdl2@asAS'
        user = Account.objects.create_superuser(email=email, password=password, phone_number='8132',
                                                is_phone_confirmed=True)
        self.assertEqual(user.email, email)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_moderator)
        self.assertTrue(user.is_government)
        self.assertTrue(user.is_management_company)
        self.assertTrue(user.is_phone_confirmed)

    def test_make_random_password(self):
        allowed_chars = 'abcdefg'
        password = CustomUserManager().make_random_password(5, allowed_chars)
        self.assertEqual(len(password), 5)
        for char in password:
            self.assertIn(char, allowed_chars)
