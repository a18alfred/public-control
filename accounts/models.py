from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
from core.constants import REGION_CODES
import uuid
from core.picture_compressor import validate_image


class Account(AbstractUser):
    """
    Кастомная user модель для аккаунтов.
    username отсутсвует
    email является логином

    is_moderator - флажок является ли пользователь модератором
    is_government -флажок является ли пользователь представителем власти
    is_management_company -флажок является ли пользователь представителем управляющей компании
    phone_number - телефон пользователя
    is_phone_confirmed - подтвердён или нет телефон
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    username = None
    email = models.EmailField(unique=True, verbose_name="электронная почта")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']

    is_moderator = models.BooleanField(default=False, verbose_name="модератор")
    is_government = models.BooleanField(default=False, verbose_name="представитель власти")
    is_management_company = models.BooleanField(default=False, verbose_name="представитель УК")

    phone_number = models.CharField(unique=True, max_length=15, verbose_name="телефон")
    is_phone_confirmed = models.BooleanField(default=False, verbose_name="телефон подтверждён")

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        ordering = ['date_joined']
        verbose_name = "аккаунт"
        verbose_name_plural = "аккаунты"


def upload_avatar_path(instance, filename):
    """
    Функция возвращает путь для сохранения фото. Фотографии хранятся в media/problems/pictures/${problem.pk}
    """
    return '/'.join(['accounts', str(instance.account.pk), str(uuid.uuid4()) + '.jpg'])


class Profile(models.Model):
    """
    Модель для хранения пользовательских данных.
    account - аккаунт к которому привязан профайл
    first_name - имя
    middle_name - отчество
    last_name - фамилия
    full_name - полное имя одной строкой
    date_of_birth - дата рождения
    avatar - фотография пользователя (аватарка)

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

    company_name - название компании, которую представляет пользователь
    company_inn - ИНН компании
    position - должность в компании
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name="account_profile")

    first_name = models.CharField(max_length=100, blank=True, verbose_name="имя")
    middle_name = models.CharField(max_length=100, blank=True, verbose_name="отчество")
    last_name = models.CharField(max_length=100, blank=True, verbose_name="фамилия")
    full_name = models.CharField(max_length=300, blank=True, verbose_name="полное имя")

    date_of_birth = models.DateField(blank=True, null=True, verbose_name='дата рождения')

    avatar = models.ImageField(blank=True, null=True, upload_to=upload_avatar_path, validators=[validate_image],
                               verbose_name='фото пользователя')

    addressFull = models.CharField(max_length=300, blank=True, verbose_name='полный адрес')
    postal_code = models.CharField(max_length=10, blank=True, verbose_name='индекс')
    country = models.CharField(max_length=50, blank=True, verbose_name='страна')
    federal_district = models.CharField(max_length=300, blank=True, verbose_name='федеральный округ')
    region_iso = models.CharField(max_length=13, choices=REGION_CODES, blank=True, verbose_name='регион')
    area_with_type = models.CharField(max_length=300, blank=True, verbose_name='район в регионе с типом')
    city_with_type = models.CharField(max_length=300, blank=True, verbose_name='город с типом')
    city_district_with_type = models.CharField(max_length=300, blank=True, verbose_name='район города с типом')
    settlement_with_type = models.CharField(max_length=300, blank=True, verbose_name='населенный пункт с типом')
    street_with_type = models.CharField(max_length=300, blank=True, verbose_name='улица с типом')
    house = models.CharField(max_length=10, blank=True, verbose_name='номер дома')
    block = models.CharField(max_length=10, blank=True, verbose_name='корпус/строение')
    flat = models.CharField(max_length=10, blank=True, verbose_name='номер квартиры')

    company_name = models.CharField(max_length=300, blank=True, verbose_name="название компании")
    company_inn = models.CharField(max_length=300, blank=True, verbose_name="ИНН компании")
    position = models.CharField(max_length=100, blank=True, verbose_name="должность в компании")

    def __str__(self):
        return self.account.email

    class Meta:
        verbose_name = "учётная запись"
        verbose_name_plural = "учётные записи"
