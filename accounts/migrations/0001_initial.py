# Generated by Django 3.1.6 on 2021-02-15 11:32

import accounts.models
import core.picture_compressor
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='электронная почта')),
                ('is_moderator', models.BooleanField(default=False, verbose_name='модератор')),
                ('is_government', models.BooleanField(default=False, verbose_name='представитель власти')),
                ('is_management_company', models.BooleanField(default=False, verbose_name='представитель УК')),
                ('phone_number', models.CharField(max_length=15, unique=True, verbose_name='телефон')),
                ('is_phone_confirmed', models.BooleanField(default=False, verbose_name='телефон подтверждён')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'аккаунт',
                'verbose_name_plural': 'аккаунты',
                'ordering': ['date_joined'],
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('first_name', models.CharField(blank=True, max_length=100, verbose_name='имя')),
                ('middle_name', models.CharField(blank=True, max_length=100, verbose_name='отчество')),
                ('last_name', models.CharField(blank=True, max_length=100, verbose_name='фамилия')),
                ('full_name', models.CharField(blank=True, max_length=300, verbose_name='полное имя')),
                ('date_of_birth', models.DateField(blank=True, null=True, verbose_name='дата рождения')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to=accounts.models.upload_avatar_path, validators=[core.picture_compressor.validate_image], verbose_name='фото пользователя')),
                ('addressFull', models.CharField(blank=True, max_length=300, verbose_name='полный адрес')),
                ('postal_code', models.CharField(blank=True, max_length=10, verbose_name='индекс')),
                ('country', models.CharField(blank=True, max_length=50, verbose_name='страна')),
                ('federal_district', models.CharField(blank=True, max_length=300, verbose_name='федеральный округ')),
                ('region_kladr', models.CharField(blank=True, choices=[('0100000000000', 'Республика Адыгея (Адыгея)'), ('0200000000000', 'Республика Башкортостан'), ('0300000000000', 'Республика Бурятия'), ('0400000000000', 'Республика Алтай'), ('0500000000000', 'Республика Дагестан'), ('0600000000000', 'Республика Ингушетия'), ('0700000000000', 'Кабардино-Балкарская Республика'), ('0800000000000', 'Республика Калмыкия'), ('0900000000000', 'Карачаево-Черкесская Республика'), ('1000000000000', 'Республика Карелия'), ('1100000000000', 'Республика Коми'), ('1200000000000', 'Республика Марий Эл'), ('1300000000000', 'Республика Мордовия'), ('1400000000000', 'Республика Саха (Якутия)'), ('1500000000000', 'Республика Северная Осетия - Алания'), ('1600000000000', 'Республика Татарстан (Татарстан)'), ('1700000000000', 'Республика Тыва'), ('1800000000000', 'Удмуртская Республика'), ('1900000000000', 'Республика Хакасия'), ('2000000000000', 'Чеченская Республика'), ('2100000000000', 'Чувашская Республика - Чувашия'), ('2200000000000', 'Алтайский край'), ('2300000000000', 'Краснодарский край'), ('2400000000000', 'Красноярский край'), ('2500000000000', 'Приморский край'), ('2600000000000', 'Ставропольский край'), ('2700000000000', 'Хабаровский край'), ('2800000000000', 'Амурская область'), ('2900000000000', 'Архангельская область'), ('3000000000000', 'Астраханская область'), ('3100000000000', 'Белгородская область'), ('3200000000000', 'Брянская область'), ('3300000000000', 'Владимирская область'), ('3400000000000', 'Волгоградская область'), ('3500000000000', 'Вологодская область'), ('3600000000000', 'Воронежская область'), ('3700000000000', 'Ивановская область'), ('3800000000000', 'Иркутская область'), ('3900000000000', 'Калининградская область'), ('4000000000000', 'Калужская область'), ('4100000000000', 'Камчатский край'), ('4200000000000', 'Кемеровская область'), ('4300000000000', 'Кировская область'), ('4400000000000', 'Костромская область'), ('4500000000000', 'Курганская область'), ('4600000000000', 'Курская область'), ('4700000000000', 'Ленинградская область'), ('4800000000000', 'Липецкая область'), ('4900000000000', 'Магаданская область'), ('5000000000000', 'Московская область'), ('5100000000000', 'Мурманская область'), ('5200000000000', 'Нижегородская область'), ('5300000000000', 'Новгородская область'), ('5400000000000', 'Новосибирская область'), ('5500000000000', 'Омская область'), ('5600000000000', 'Оренбургская область'), ('5700000000000', 'Орловская область'), ('5800000000000', 'Пензенская область'), ('5900000000000', 'Пермский край'), ('6000000000000', 'Псковская область'), ('6100000000000', 'Ростовская область'), ('6200000000000', 'Рязанская область'), ('6300000000000', 'Самарская область'), ('6400000000000', 'Саратовская область'), ('6500000000000', 'Сахалинская область'), ('6600000000000', 'Свердловская область'), ('6700000000000', 'Смоленская область'), ('6800000000000', 'Тамбовская область'), ('6900000000000', 'Тверская область'), ('7000000000000', 'Томская область'), ('7100000000000', 'Тульская область'), ('7200000000000', 'Тюменская область'), ('7300000000000', 'Ульяновская область'), ('7400000000000', 'Челябинская область'), ('7500000000000', 'Забайкальский край'), ('7600000000000', 'Ярославская область'), ('7700000000000', 'г. Москва'), ('7800000000000', 'Санкт-Петербург'), ('7900000000000', 'Еврейская автономная область'), ('8300000000000', 'Ненецкий автономный округ'), ('8600000000000', 'Ханты-Мансийский автономный округ - Югра автономный округ'), ('8700000000000', 'Чукотский автономный округ'), ('8900000000000', 'Ямало-Ненецкий автономный округ'), ('9100000000000', 'Республика Крым'), ('9200000000000', 'г. Севастополь'), ('9900000000000', 'г. Байконур')], max_length=13, verbose_name='регион')),
                ('area_with_type', models.CharField(blank=True, max_length=300, verbose_name='район в регионе с типом')),
                ('city_with_type', models.CharField(blank=True, max_length=300, verbose_name='город с типом')),
                ('city_district_with_type', models.CharField(blank=True, max_length=300, verbose_name='район города с типом')),
                ('settlement_with_type', models.CharField(blank=True, max_length=300, verbose_name='населенный пункт с типом')),
                ('street_with_type', models.CharField(blank=True, max_length=300, verbose_name='улица с типом')),
                ('house', models.CharField(blank=True, max_length=10, verbose_name='номер дома')),
                ('block', models.CharField(blank=True, max_length=10, verbose_name='корпус/строение')),
                ('flat', models.CharField(blank=True, max_length=10, verbose_name='номер квартиры')),
                ('company_name', models.CharField(blank=True, max_length=300, verbose_name='название компании')),
                ('company_inn', models.CharField(blank=True, max_length=300, verbose_name='ИНН компании')),
                ('position', models.CharField(blank=True, max_length=100, verbose_name='должность в компании')),
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='account_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'учётная запись',
                'verbose_name_plural': 'учётные записи',
            },
        ),
    ]
