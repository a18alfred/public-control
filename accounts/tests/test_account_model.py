from django.test import TestCase
from accounts.models import Account


class AccountModelTestCase(TestCase):
    """
    Тестируем модель Account
    """

    def test_account_str_return(self):
        """
        Тестируем __str__ модели Account
        :return: email
        """
        email_lowercase = 'normal@normal.com'
        password = 'asdasdl2@asAS'
        user = Account.objects.create_user(email=email_lowercase, password=password, phone_number='8123',
                                           is_phone_confirmed=True)
        self.assertEqual(user.__str__(), email_lowercase)
