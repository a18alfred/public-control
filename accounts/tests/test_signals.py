from django.test import TestCase
from accounts.models import Profile, Account
from core.picture_compressor import create_test_image
import os
from django.conf import settings
from accounts.signals import auto_delete_file_on_change
from accounts.signals import auto_delete_file_on_change


class SignalsTestCase(TestCase):

    def test_auto_delete_file_on_change(self):
        """
        Тестируем удаление старого файла фото после обновления пользовательского фото и удаление директории
        если файлов в ней нет
        """
        email_lowercase = 'normal@normal.com'
        password = 'asdasdl2@asAS'
        user = Account.objects.create_user(email=email_lowercase, password=password, phone_number='8127',
                                           is_phone_confirmed=True)
        profile = Profile.objects.get(account_id=user.id)
        profile.delete()

        dir_name = '/'.join([str(settings.MEDIA_ROOT), 'accounts', str(profile.account.pk)])
        profile.avatar = create_test_image(name='test1.png')
        profile.save()
        self.assertEqual(len(os.listdir(dir_name)), 1)
        profile.avatar = create_test_image(name='test2.png')
        profile.save()
        self.assertEqual(len(os.listdir(dir_name)), 1)
        profile.avatar = ''
        profile.save()
        self.assertFalse(os.path.exists(dir_name))
        profile.delete()
        self.assertFalse(os.path.exists(dir_name))

        profile = Profile.objects.create(account=user)
        profile.id = None
        self.assertFalse(auto_delete_file_on_change(Profile, profile))

    def test_auto_compress_image(self):
        email_lowercase = 'normal@normal.com'
        password = 'asdasdl2@asAS'
        user = Account.objects.create_user(email=email_lowercase, password=password, phone_number='8128',
                                           is_phone_confirmed=True)
        Profile.objects.get(account_id=user.id).delete()
        profile = Profile.objects.create(account=user, avatar=create_test_image(name='test2.png'))
        self.assertTrue(profile.avatar)
        profile.delete()
