from django.test import TestCase
from accounts.models import Account, Profile
from core.picture_compressor import create_test_image


class ProfileModelTestCase(TestCase):
    """
    Тестируем модель Profile
    """

    def test_automatic_profile_creation_and_str_return(self):
        """
        Тестируем автоматическое созднание профайла после регистрации нового пользователя и __str__ модели Profile
        :return: email
        """
        email_lowercase = 'normal@normal.com'
        password = 'asdasdl2@asAS'
        user = Account.objects.create_user(email=email_lowercase, password=password, phone_number='8125',
                                           is_phone_confirmed=True)
        self.assertEqual(Profile.objects.get(account_id=user.id).__str__(), email_lowercase)

    def test_profile_avatar_compression_on_save(self):
        """
        Тестируем сжатие пользовательского фото после сохранения профайла
        """
        email_lowercase = 'normal@normal.com'
        password = 'asdasdl2@asAS'
        user = Account.objects.create_user(email=email_lowercase, password=password, phone_number='8126',
                                           is_phone_confirmed=True)
        profile = Profile.objects.get(account_id=user.id)
        
        avatar_image = create_test_image()
        profile.avatar = avatar_image
        profile.save()
        self.assertTrue(profile.avatar)
        profile.delete()
