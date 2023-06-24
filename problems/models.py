from django.db import models
from django.dispatch import receiver
from django.conf import settings
import uuid
from django.conf import settings
from slugify import slugify
# Валидаторы для проверка долготы и широты
from django.core.validators import MaxValueValidator, MinValueValidator
# Модуль для создания дерева категорий и подкатегорий
from mptt.models import MPTTModel, TreeForeignKey
# Модуль для сжатия фото
from core.picture_compressor import validate_image
# Константы кодов регионов и статусов проблемы
from core.constants import REGION_CODES, PROBLEM_STATUS, PROBLEM_URGENCY
from accounts.models import Account
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def upload_picture_path(instance, filename):
    """
    Функция возвращает путь для сохранения фото. Фотографии хранятся в media/problems/pictures/${problem.pk}
    """
    return '/'.join(['categories', str(instance.slug), filename])


class Category(MPTTModel):
    """
    Модель для хранения категорий и субкатегорий проблем (строится с помощью дерева) проблем. Например: ЖКХ, дороги,
    учебные заведения и т.д.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    name = models.CharField(max_length=100, blank=False, unique=True, verbose_name='название')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children',
                            verbose_name='родитель')
    icon = models.ImageField(blank=True, null=True, upload_to=upload_picture_path,
                             default='categories/default_category_icon.png', validators=[validate_image],
                             verbose_name='иконка для категории')
    slug = models.SlugField(max_length=255, unique=True, default='default')

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        ordering = ['name']
        verbose_name = "категория"
        verbose_name_plural = "категории"

    def __str__(self):
        """
        Возращает название категории
        """
        return self.name

    def save(self, *args, **kwargs):
        """
        Переопределенная функция сохранения, которая сжимает фото перед сохранением на сервере.
        """
        if not self.icon:
            self.icon = 'categories/default_category_icon.png'
        self.slug = slugify(self.name, to_lower=True)
        super(Category, self).save(*args, **kwargs)


class Problem(models.Model):
    """
    Основная модель проблемы. Модель включает в себя:

    account - Аккаунт, который открыл проблему

    description - Подробное описание проблемы
    category - Категория проблемы
    status - Статус проблемы (выбирается из PROBLEM_STATUS), после создания всегда 1
    urgency - Срочность проблемы

    addressFull - Адрес одной строкой (полный, с индексом)
    postal_code - Индекс
    country - Страна
    federal_district - Федеральный округ
    region_iso - Код ISO региона
    area_with_type - Район в регионе с типом
    city_with_type - Город с типом
    city_district_with_type - 	Район города с типом
    settlement_with_type - Населенный пункт с типом
    street_with_type - 	Улица с типом
    house - Номер дома
    block - Корпус/строение
    flat - Номер квартиры

    addressDescription - если точный адрес не указан, то можно описать местонахождение проблемы своими словами
    latitude и longitude - графические координаты (широта и долгота) проблемы

    dateCreated - Дата создания проблемы, заполняется автоматически
    dateUnderReview - Дата смены статуса на Under Review
    dateActive - Дата смены статуса на Active
    dateInProgress - Дата смены статуса на In Progress
    dateCompleted - Дата смены статуса на Completed
    dateClosed - Дата смены статуса на Closed
    dateRejected - Дата смены статуса на Rejected
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_problems',
                                null=True, blank=True)

    description = models.TextField(blank=False, verbose_name='описание')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name='категория')
    status = models.CharField(choices=PROBLEM_STATUS, max_length=20, blank=False, default='created',
                              verbose_name='статус')
    urgency = models.CharField(choices=PROBLEM_URGENCY, max_length=1, blank=False, default='Т',
                               verbose_name='срочность')
    is_published = models.BooleanField(default=False, editable=False, verbose_name="опубликована")

    addressFull = models.CharField(max_length=300, blank=True, verbose_name='полный адрес')
    postal_code = models.CharField(max_length=10, blank=True, verbose_name='индекс')
    country = models.CharField(max_length=50, blank=True, verbose_name='страна')
    federal_district = models.CharField(max_length=300, blank=True, verbose_name='федеральный округ')
    region_iso = models.CharField(max_length=13, choices=REGION_CODES, blank=False, verbose_name='регион')
    area_with_type = models.CharField(max_length=300, blank=True, verbose_name='район в регионе с типом')
    city_with_type = models.CharField(max_length=300, blank=True, verbose_name='город с типом')
    city_district_with_type = models.CharField(max_length=300, blank=True, verbose_name='район города с типом')
    settlement_with_type = models.CharField(max_length=300, blank=True, verbose_name='населенный пункт с типом')
    street_with_type = models.CharField(max_length=300, blank=True, verbose_name='улица с типом')
    house = models.CharField(max_length=10, blank=True, verbose_name='номер дома')
    block = models.CharField(max_length=10, blank=True, verbose_name='корпус/строение')
    flat = models.CharField(max_length=10, blank=True, verbose_name='номер квартиры')
    addressDescription = models.CharField(max_length=300, blank=True,
                                          verbose_name='местонахождение проблемы своими словами')
    latitude = models.FloatField(validators=[MinValueValidator(-90), MaxValueValidator(90)], blank=True, null=True,
                                 verbose_name='широта')
    longitude = models.FloatField(validators=[MinValueValidator(-180), MaxValueValidator(180)], blank=True, null=True,
                                  verbose_name='долгота')

    dateCreated = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    dateUnderReview = models.DateTimeField(blank=True, null=True,
                                           verbose_name='Дата смены статуса на "На рассмотрении"')
    dateActive = models.DateTimeField(blank=True, null=True, verbose_name='Дата смены статуса на "На рассмотрении"')
    dateInProgress = models.DateTimeField(blank=True, null=True, verbose_name='Дата смены статуса на "Ведутся работы"')
    dateCompleted = models.DateTimeField(blank=True, null=True, verbose_name='Дата смены статуса на "Исполнена"')
    dateClosed = models.DateTimeField(blank=True, null=True, verbose_name='Дата закрытия')
    dateRejected = models.DateTimeField(blank=True, null=True, verbose_name='Дата отклонения')

    signature_count = models.IntegerField(default=0, editable=False, verbose_name='Количество подписей')

    def get_signature_count(self):
        signature_count = self.problem_signatures.all().count()
        self.signature_count = signature_count
        self.save()
        return signature_count

    class Meta:
        verbose_name = "проблема"
        verbose_name_plural = "проблемы"
        ordering = ['dateCreated']

    def __str__(self):
        """
        Возращает дату создания
        """
        generated_string = str(self.id) + ' ' + str(self.dateCreated.date())
        return generated_string


def upload_picture_path(instance, filename):
    """
    Функция возвращает путь для сохранения фото. Фотографии хранятся в media/problems/pictures/${problem.pk}
    """
    return '/'.join(['problems', str(instance.problem.pk), 'pictures', str(uuid.uuid4()) + '.jpg'])


class Picture(models.Model):
    """
    Модель для хранения фотограйий. Модель включает:
    problem - проблема к которой относится фото
    uploaded_picture - ссылка на сохраненное фото на сервере
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="problem_picture")
    uploaded_picture = models.ImageField(blank=False, upload_to=upload_picture_path, validators=[validate_image],
                                         verbose_name='загруженное фото')

    class Meta:
        verbose_name = "фото"
        verbose_name_plural = "фотографии"


class Comment(models.Model):
    """
    Модель для хранения комментарий. Модель включает в себя:
    account - Автор комментария
    problem - Проблема к которой относится комментарий
    comment - Комментарий
    date - Дата написания комментария. Заполняется автоматически
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='problem_comment')
    comment = models.CharField(max_length=520, blank=False, verbose_name='комментарий')
    uploaded_picture = models.ImageField(blank=True, null=True, upload_to=upload_picture_path,
                                         validators=[validate_image], verbose_name='загруженное фото')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата комментария')

    class Meta:
        verbose_name = "комментарий"
        verbose_name_plural = "комментарии"


class Signature(models.Model):
    """
    Модель для хранения подписей пользователей под проблемой
    account - Подписавшийся пользователь
    problem - Проблема под которой пользователь подписался
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
                                related_name='account_signatures')
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='problem_signatures')

    class Meta:
        unique_together = [('problem', 'account'), ]
        verbose_name = "подпись"
        verbose_name_plural = "подписи"

    def __str__(self):
        """
        Возращает id проблемы и аккаунт, который подписался
        """
        generated_string = 'problem: ' + str(self.problem.id) + ', email: ' + str(self.account.email)
        return generated_string


class Assignment(models.Model):
    """
    Модель для хранения модераторов, представителей назначенных к конкретной проблеме
    account - Назначенный пользователь
    problem - Проблема под которой пользователь назначен
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
                                related_name='account_assignment')
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='problem_assignment')

    class Meta:
        unique_together = [('problem', 'account'), ]
        verbose_name = "назначение"
        verbose_name_plural = "назначения"

    def __str__(self):
        """
        Возращает id проблемы и аккаунт, который назначился
        """
        generated_string = 'problem: ' + str(self.problem.id) + ', email: ' + str(self.account.email)
        return generated_string
