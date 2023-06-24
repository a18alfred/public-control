from .models import Account, Profile
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
import os
from django.conf import settings
from core.picture_compressor import compress_picture
from django.core.exceptions import ObjectDoesNotExist


# Автоматическое создание профиля пользователя для новых пользователей
@receiver(post_save, sender=Account)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(account=instance)


@receiver(post_delete, sender=Profile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Удаляет файлы/фото из дериктории после удаления файла из модели. И удаляет дерикторию если она пустая
    """
    if instance.avatar:
        if os.path.isfile(instance.avatar.path):
            os.remove(instance.avatar.path)
            dir_name = '/'.join([str(settings.MEDIA_ROOT), 'accounts', str(instance.account.pk)])
            if os.path.exists(dir_name) and os.path.isdir(dir_name):
                if not os.listdir(dir_name):
                    os.rmdir(dir_name)


@receiver(pre_save, sender=Profile)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Удаляет файлы/фото из дериктории после изменения файла в модели. И удаляет дерикторию если она пустая.
    Сжимает фото перед сохранением
    """
    if instance.avatar:
        instance.avatar = compress_picture(instance.avatar)

    if instance.pk is None:
        return False
    else:
        try:
            old_profile = sender.objects.get(pk=instance.pk)
        except ObjectDoesNotExist:
            return False
        if old_profile.avatar:
            old_file = old_profile.avatar
            new_file = instance.avatar
            if old_file:
                if not old_file == new_file:
                    if os.path.isfile(old_file.path):
                        os.remove(old_file.path)
            if not instance.avatar:
                dir_name = '/'.join([str(settings.MEDIA_ROOT), 'accounts', str(instance.account.pk)])
                if os.path.exists(dir_name) and os.path.isdir(dir_name):
                    if not os.listdir(dir_name):
                        os.rmdir(dir_name)
