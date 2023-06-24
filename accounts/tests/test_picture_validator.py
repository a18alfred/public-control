from django.test import TestCase
from accounts.models import Account, Profile
from core.picture_compressor import create_test_image
from django.core.exceptions import ValidationError


class PictureValidatorTestCase(TestCase):
    """
    Тестируем валидацию фотографии по размеру файла
    """

    def test_picture_validator_limit_size(self):
        """
        Тестируем валидацию фотографии по размеру файла
        """
        email_lowercase = 'normal@normal.com'
        password = 'asdasdl2@asAS'
        user = Account.objects.create_user(email=email_lowercase, password=password, phone_number='8124',
                                           is_phone_confirmed=True)
        profile = Profile.objects.get(account_id=user.id)

        with self.assertRaisesMessage(ValidationError, "{'avatar': ['Максимальный размер файла 15 MB']}"):
            avatar_image = create_test_image(size=(2000, 2000), name='test.bmp', ext='bmp')
            profile.avatar = avatar_image
            profile.full_clean()

        profile.delete()
