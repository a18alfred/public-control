from django.test import TestCase
from problems.models import Problem, Category, Picture, Comment
from accounts.models import Account, Profile
from core.picture_compressor import create_test_image
import os
from django.conf import settings
from problems.signals import auto_delete_file_on_change, auto_delete_icon_on_change, auto_add_time_when_status_changes


class SignalsTestCase(TestCase):

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
        self.super = Account.objects.create_superuser(email=email, password=password, phone_number='8139',
                                                      is_phone_confirmed=True)
        self.profile = Profile.objects.get(account_id=self.super.id)
        self.profile.region_iso = 'RU-ALT'
        self.profile.save()

        email1 = 'test1@test.com'
        self.user_moderator = Account.objects.create_user(email1, password, phone_number='8140',
                                                          is_phone_confirmed=True)
        self.user_moderator.is_moderator = True
        self.user_moderator.is_active = True
        self.user_moderator.save()

        email2 = 'test2@test.com'
        self.user_government = Account.objects.create_user(email2, password, phone_number='8141',
                                                           is_phone_confirmed=True)
        self.user_government.is_government = True
        self.user_government.is_active = True
        self.user_government.save()

        email3 = 'test3@test.com'
        self.user_mc = Account.objects.create_user(email3, password, phone_number='8142', is_phone_confirmed=True)
        self.user_mc.is_management_company = True
        self.user_mc.is_active = True
        self.user_mc.save()

        email4 = 'test4@test.com'
        self.simple_user1 = Account.objects.create_user(email4, password, phone_number='8143', is_phone_confirmed=True)
        self.simple_user1.is_active = True
        self.simple_user1.save()

        email5 = 'test5@test.com'
        self.simple_user2 = Account.objects.create_user(email5, password, phone_number='8144', is_phone_confirmed=True)
        self.simple_user2.is_active = True
        self.simple_user2.save()

        self.test_category = Category.objects.create(name='test_category')
        self.problem1 = Problem.objects.create(category=self.test_category, description='description',
                                               account=self.super,
                                               region_iso='RU-ALT', status='under_review')

        self.problem1.save()

        self.problem2 = Problem.objects.create(category=self.test_category, description='description',
                                               account=self.simple_user1,
                                               region_iso='RU-ALT')
        self.problem2.save()
        self.problem3 = Problem.objects.create(category=self.test_category, description='description',
                                               account=self.simple_user1,
                                               region_iso='RU-ALT')
        self.problem3.save()

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

    def test_auto_delete_file_on_change(self):
        """
        Тестируем удаление старого файла фото после обновления фото и удаление директории
        если файлов в ней нет.
        Тестируем сжатие файла
        """
        problem_test = Problem.objects.create(category=self.test_category, description='description',
                                              account=self.simple_user1,
                                              region_iso='RU-ALT')

        picture1 = Picture(problem=problem_test, uploaded_picture=create_test_image())
        picture1.save()
        self.assertTrue(picture1.uploaded_picture)
        picture2 = Picture(problem=problem_test, uploaded_picture=create_test_image())
        picture2.save()

        dir_name_problem = '/'.join([str(settings.MEDIA_ROOT), 'problems', str(problem_test.id)])
        dir_name = '/'.join([str(settings.MEDIA_ROOT), 'problems', str(problem_test.id), 'pictures', ])

        self.assertEqual(len(os.listdir(dir_name)), 2)

        picture1.uploaded_picture = ''
        picture1.save()
        self.assertTrue(os.path.exists(dir_name))
        picture2.uploaded_picture = ''
        picture2.save()
        self.assertFalse(os.path.exists(dir_name))
        picture1 = Picture(problem=problem_test, uploaded_picture=create_test_image())
        picture1.save()
        self.assertTrue(os.path.exists(dir_name_problem))
        problem_test.delete()
        self.assertFalse(os.path.exists(dir_name_problem))

        comment = Comment.objects.create(problem=self.problem2, comment='test')
        comment.save()
        comment.uploaded_picture = create_test_image()
        comment.save()
        self.assertTrue(comment.uploaded_picture)

        comment.id = None
        self.assertFalse(auto_delete_file_on_change(Comment, comment))

    def test_auto_delete_icon_on_delete(self):
        """
        Тестируем файла/фото из дериктории после удаления файла из модели категория
        """
        category1 = Category.objects.create(name='some test category1', icon=create_test_image())
        category2 = Category.objects.create(name='some test category2')
        dir_name1 = '/'.join([str(settings.MEDIA_ROOT), 'categories', str(category1.slug)])
        dir_name2 = '/'.join([str(settings.MEDIA_ROOT), 'categories', str(category2.slug)])
        dir_name_default = '/'.join([str(settings.MEDIA_ROOT), 'categories', 'default_category_icon.png'])

        self.assertEqual(len(os.listdir(dir_name1)), 1)
        self.assertFalse(os.path.exists(dir_name2))

        category1.delete()
        self.assertFalse(os.path.exists(dir_name1))
        category2.delete()
        self.assertTrue(os.path.exists(dir_name_default))

    def test_auto_delete_icon_on_change(self):
        category = Category.objects.create(name='test_category_test')
        category.id = None
        self.assertFalse(auto_delete_icon_on_change(Category, category))

    def test_auto_add_time_when_status_changes(self):
        """
        Тестируем автоматическое выставление дат при смене статуса
        """
        self.problem1.status = 'under_review'
        self.problem1.save()
        self.assertTrue(self.problem1.dateCreated)
        self.assertTrue(self.problem1.dateUnderReview)
        self.assertFalse(self.problem1.dateActive)
        self.assertFalse(self.problem1.dateInProgress)
        self.assertFalse(self.problem1.dateCompleted)
        self.assertFalse(self.problem1.dateClosed)
        self.assertFalse(self.problem1.dateRejected)
        self.assertFalse(self.problem1.is_published)

        self.problem1.status = 'active'
        self.problem1.save()
        self.assertTrue(self.problem1.dateCreated)
        self.assertTrue(self.problem1.dateUnderReview)
        self.assertTrue(self.problem1.dateActive)
        self.assertFalse(self.problem1.dateInProgress)
        self.assertFalse(self.problem1.dateCompleted)
        self.assertFalse(self.problem1.dateClosed)
        self.assertFalse(self.problem1.dateRejected)
        self.assertTrue(self.problem1.is_published)

        self.problem1.status = 'in_progress'
        self.problem1.save()
        self.assertTrue(self.problem1.dateCreated)
        self.assertTrue(self.problem1.dateUnderReview)
        self.assertTrue(self.problem1.dateActive)
        self.assertTrue(self.problem1.dateInProgress)
        self.assertFalse(self.problem1.dateCompleted)
        self.assertFalse(self.problem1.dateClosed)
        self.assertFalse(self.problem1.dateRejected)
        self.assertTrue(self.problem1.is_published)

        self.problem1.status = 'completed'
        self.problem1.save()
        self.assertTrue(self.problem1.dateCreated)
        self.assertTrue(self.problem1.dateUnderReview)
        self.assertTrue(self.problem1.dateActive)
        self.assertTrue(self.problem1.dateInProgress)
        self.assertTrue(self.problem1.dateCompleted)
        self.assertFalse(self.problem1.dateClosed)
        self.assertFalse(self.problem1.dateRejected)
        self.assertTrue(self.problem1.is_published)

        self.problem1.status = 'closed'
        self.problem1.save()
        self.assertTrue(self.problem1.dateCreated)
        self.assertTrue(self.problem1.dateUnderReview)
        self.assertTrue(self.problem1.dateActive)
        self.assertTrue(self.problem1.dateInProgress)
        self.assertTrue(self.problem1.dateCompleted)
        self.assertTrue(self.problem1.dateClosed)
        self.assertFalse(self.problem1.dateRejected)
        self.assertTrue(self.problem1.is_published)

        self.problem1.status = 'rejected'
        self.problem1.save()
        self.assertTrue(self.problem1.dateCreated)
        self.assertTrue(self.problem1.dateUnderReview)
        self.assertTrue(self.problem1.dateActive)
        self.assertTrue(self.problem1.dateInProgress)
        self.assertTrue(self.problem1.dateCompleted)
        self.assertTrue(self.problem1.dateClosed)
        self.assertTrue(self.problem1.dateRejected)
        self.assertFalse(self.problem1.is_published)

        self.problem1.status = 'created'
        self.problem1.save()
        self.assertTrue(self.problem1.dateCreated)
        self.assertFalse(self.problem1.dateUnderReview)
        self.assertFalse(self.problem1.dateActive)
        self.assertFalse(self.problem1.dateInProgress)
        self.assertFalse(self.problem1.dateCompleted)
        self.assertFalse(self.problem1.dateClosed)
        self.assertFalse(self.problem1.dateRejected)
        self.assertFalse(self.problem1.is_published)

        problem_test = Problem.objects.create(category=self.test_category, description='description',
                                              account=self.simple_user1,
                                              region_iso='RU-ALT')
        problem_test.id = None
        self.assertFalse(auto_add_time_when_status_changes(Problem, problem_test))
