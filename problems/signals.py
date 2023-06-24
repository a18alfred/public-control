import os
from django.conf import settings
from .models import Picture, Comment, Category, Problem, Signature
from django.dispatch import receiver
from django.db.models.signals import post_delete, pre_save, post_save
from django.utils import timezone
from core.picture_compressor import compress_picture
from django.core.exceptions import ObjectDoesNotExist
from .service import create_dummy_problems


@receiver(post_delete, sender=Picture)
@receiver(post_delete, sender=Comment)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Удаляет файлы/фото из дериктории после удаления файла из модели. И удаляет дерикторию если она пустая
    """
    if instance.uploaded_picture:
        if os.path.isfile(instance.uploaded_picture.path):
            os.remove(instance.uploaded_picture.path)
            dir_name = '/'.join([str(settings.MEDIA_ROOT), 'problems', str(instance.problem.pk), 'pictures', ])
            dir_name_problem = '/'.join([str(settings.MEDIA_ROOT), 'problems', str(instance.problem.pk)])
            if os.path.exists(dir_name) and os.path.isdir(dir_name):
                if not os.listdir(dir_name):
                    os.rmdir(dir_name)
                    if os.path.exists(dir_name_problem) and os.path.isdir(dir_name_problem):
                        if not os.listdir(dir_name_problem):
                            os.rmdir(dir_name_problem)


@receiver(pre_save, sender=Picture)
@receiver(pre_save, sender=Comment)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Удаляет файлы/фото из дериктории после изменения файла в модели
    Сжимает фото перед сохранением
    """
    if instance.uploaded_picture:
        instance.uploaded_picture = compress_picture(instance.uploaded_picture)

    if instance.pk is None:
        return False
    else:
        try:
            old_object = sender.objects.get(pk=instance.pk)
        except ObjectDoesNotExist:
            return False
        if old_object.uploaded_picture:
            old_file = old_object.uploaded_picture
            new_file = instance.uploaded_picture
            if not old_file == new_file:
                if os.path.isfile(old_file.path):
                    os.remove(old_file.path)
                    if not new_file:
                        dir_name = '/'.join(
                            [str(settings.MEDIA_ROOT), 'problems', str(instance.problem.pk), 'pictures'])
                        dir_name_problem = '/'.join([str(settings.MEDIA_ROOT), 'problems', str(instance.problem.pk)])
                        if os.path.exists(dir_name) and os.path.isdir(dir_name):
                            if not os.listdir(dir_name):
                                os.rmdir(dir_name)
                                if os.path.exists(dir_name_problem) and os.path.isdir(dir_name_problem):
                                    if not os.listdir(dir_name_problem):
                                        os.rmdir(dir_name_problem)


@receiver(post_delete, sender=Category)
def auto_delete_icon_on_delete(sender, instance, **kwargs):
    """
    Удаляет файлы/фото из дериктории после удаления файла из модели. И удаляет дерикторию если она пустая
    """
    if instance.icon:
        if os.path.isfile(instance.icon.path):
            if not instance.icon.path == '\\'.join([str(settings.MEDIA_ROOT), 'categories\default_category_icon.png']):
                os.remove(instance.icon.path)
            dir_name = '/'.join([str(settings.MEDIA_ROOT), 'categories', str(instance.slug)])
            if os.path.exists(dir_name) and os.path.isdir(dir_name):
                if not os.listdir(dir_name):
                    os.rmdir(dir_name)


@receiver(pre_save, sender=Category)
def auto_delete_icon_on_change(sender, instance, **kwargs):
    """
    Удаляет файлы/фото из дериктории после изменения файла в модели
    """
    ################################ Для тестов №№№№№№№№№№№№№№№№№№
    # create_dummy_problems()
    ##################
    if instance.pk is None:
        return False

    try:
        category = sender.objects.get(pk=instance.pk)
    except ObjectDoesNotExist:
        return False

    if category.icon:
        old_file = category.icon
        if old_file:
            new_file = instance.icon
            if not old_file == new_file:
                if not old_file.path == '\\'.join([str(settings.MEDIA_ROOT), 'categories\default_category_icon.png']):
                    if os.path.isfile(old_file.path):
                        os.remove(old_file.path)


@receiver(post_save, sender=Problem)
def default_problem_status_after_creation(sender, instance, created, **kwargs):
    """
    Если статус только что созданной проблемы не "Created", то он корректируется на Created
    """

    if created:
        if instance.status != 'created':
            instance.status = 'created'
            instance.save()


@receiver(pre_save, sender=Problem)
def auto_add_time_when_status_changes(sender, instance, **kwargs):
    """
    Автоматическое выставление дат при смене статуса и автоматическая публикация если статус подходящий
    """
    if instance.pk is None:
        return False

    try:
        problem = sender.objects.get(pk=instance.pk)
    except ObjectDoesNotExist:
        return False

    status_now = problem.status

    if instance.status == 'created' or instance.status == 'under_review' or instance.status == 'rejected':
        instance.is_published = False
    else:
        instance.is_published = True

    if status_now != instance.status:
        if instance.status == 'created':
            instance.dateUnderReview = None
            instance.dateActive = None
            instance.dateInProgress = None
            instance.dateCompleted = None
            instance.dateClosed = None
            instance.dateRejected = None
        if instance.status == 'under_review':
            instance.dateUnderReview = timezone.now()
            instance.dateActive = None
            instance.dateInProgress = None
            instance.dateCompleted = None
            instance.dateClosed = None
            instance.dateRejected = None
        if instance.status == 'active':
            instance.dateActive = timezone.now()
            instance.dateInProgress = None
            instance.dateCompleted = None
            instance.dateClosed = None
            instance.dateRejected = None
        if instance.status == 'in_progress':
            instance.dateInProgress = timezone.now()
            instance.dateCompleted = None
            instance.dateClosed = None
            instance.dateRejected = None
        if instance.status == 'completed':
            instance.dateCompleted = timezone.now()
            instance.dateClosed = None
            instance.dateRejected = None
        if instance.status == 'closed':
            instance.dateClosed = timezone.now()
            instance.dateRejected = None
        if instance.status == 'rejected':
            instance.dateRejected = timezone.now()


@receiver(post_save, sender=Signature)
def auto_problem_signature_count_add(sender, instance, created, **kwargs):
    """
    Если пользователь подписался под проблемой, то автоматически считаем кол-во подписей и сохраняем
    """
    instance.problem.get_signature_count()


@receiver(post_delete, sender=Signature)
def auto_problem_signature_count_subtract(sender, instance, **kwargs):
    """
    Сокращаем число подписей после её удаления
    """
    instance.problem.get_signature_count()
