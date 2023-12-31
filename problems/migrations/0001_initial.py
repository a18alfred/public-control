# Generated by Django 3.1.6 on 2021-02-15 11:32

import core.picture_compressor
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields
import problems.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='название')),
                ('icon', models.ImageField(blank=True, default='categories/default_category_icon.png', null=True, upload_to=problems.models.upload_picture_path, validators=[core.picture_compressor.validate_image], verbose_name='иконка для категории')),
                ('slug', models.SlugField(default='default', max_length=255, unique=True)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='problems.category', verbose_name='родитель')),
            ],
            options={
                'verbose_name': 'категория',
                'verbose_name_plural': 'категории',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('description', models.TextField(verbose_name='описание')),
                ('status', models.CharField(choices=[('created', 'Проблема создана, но не опубликована'), ('under_review', 'Проблема находиться на рассмотрении перед публикацией'), ('active', 'Проблема проверена и опубликована'), ('in_progress', 'Проблема была замечена и решается'), ('completed', 'Проблема решена'), ('closed', 'Проблема закрыта'), ('rejected', 'Проблема была отклонена или закрыта')], default='created', max_length=20, verbose_name='статус')),
                ('urgency', models.CharField(choices=[('А', 'Аварийная'), ('Т', 'Текущая'), ('П', 'Продолжительная')], default='Т', max_length=1, verbose_name='срочность')),
                ('is_published', models.BooleanField(default=False, editable=False, verbose_name='опубликована')),
                ('addressFull', models.CharField(blank=True, max_length=300, verbose_name='полный адрес')),
                ('postal_code', models.CharField(blank=True, max_length=10, verbose_name='индекс')),
                ('country', models.CharField(blank=True, max_length=50, verbose_name='страна')),
                ('federal_district', models.CharField(blank=True, max_length=300, verbose_name='федеральный округ')),
                ('region_kladr', models.CharField(choices=[('0100000000000', 'Республика Адыгея (Адыгея)'), ('0200000000000', 'Республика Башкортостан'), ('0300000000000', 'Республика Бурятия'), ('0400000000000', 'Республика Алтай'), ('0500000000000', 'Республика Дагестан'), ('0600000000000', 'Республика Ингушетия'), ('0700000000000', 'Кабардино-Балкарская Республика'), ('0800000000000', 'Республика Калмыкия'), ('0900000000000', 'Карачаево-Черкесская Республика'), ('1000000000000', 'Республика Карелия'), ('1100000000000', 'Республика Коми'), ('1200000000000', 'Республика Марий Эл'), ('1300000000000', 'Республика Мордовия'), ('1400000000000', 'Республика Саха (Якутия)'), ('1500000000000', 'Республика Северная Осетия - Алания'), ('1600000000000', 'Республика Татарстан (Татарстан)'), ('1700000000000', 'Республика Тыва'), ('1800000000000', 'Удмуртская Республика'), ('1900000000000', 'Республика Хакасия'), ('2000000000000', 'Чеченская Республика'), ('2100000000000', 'Чувашская Республика - Чувашия'), ('2200000000000', 'Алтайский край'), ('2300000000000', 'Краснодарский край'), ('2400000000000', 'Красноярский край'), ('2500000000000', 'Приморский край'), ('2600000000000', 'Ставропольский край'), ('2700000000000', 'Хабаровский край'), ('2800000000000', 'Амурская область'), ('2900000000000', 'Архангельская область'), ('3000000000000', 'Астраханская область'), ('3100000000000', 'Белгородская область'), ('3200000000000', 'Брянская область'), ('3300000000000', 'Владимирская область'), ('3400000000000', 'Волгоградская область'), ('3500000000000', 'Вологодская область'), ('3600000000000', 'Воронежская область'), ('3700000000000', 'Ивановская область'), ('3800000000000', 'Иркутская область'), ('3900000000000', 'Калининградская область'), ('4000000000000', 'Калужская область'), ('4100000000000', 'Камчатский край'), ('4200000000000', 'Кемеровская область'), ('4300000000000', 'Кировская область'), ('4400000000000', 'Костромская область'), ('4500000000000', 'Курганская область'), ('4600000000000', 'Курская область'), ('4700000000000', 'Ленинградская область'), ('4800000000000', 'Липецкая область'), ('4900000000000', 'Магаданская область'), ('5000000000000', 'Московская область'), ('5100000000000', 'Мурманская область'), ('5200000000000', 'Нижегородская область'), ('5300000000000', 'Новгородская область'), ('5400000000000', 'Новосибирская область'), ('5500000000000', 'Омская область'), ('5600000000000', 'Оренбургская область'), ('5700000000000', 'Орловская область'), ('5800000000000', 'Пензенская область'), ('5900000000000', 'Пермский край'), ('6000000000000', 'Псковская область'), ('6100000000000', 'Ростовская область'), ('6200000000000', 'Рязанская область'), ('6300000000000', 'Самарская область'), ('6400000000000', 'Саратовская область'), ('6500000000000', 'Сахалинская область'), ('6600000000000', 'Свердловская область'), ('6700000000000', 'Смоленская область'), ('6800000000000', 'Тамбовская область'), ('6900000000000', 'Тверская область'), ('7000000000000', 'Томская область'), ('7100000000000', 'Тульская область'), ('7200000000000', 'Тюменская область'), ('7300000000000', 'Ульяновская область'), ('7400000000000', 'Челябинская область'), ('7500000000000', 'Забайкальский край'), ('7600000000000', 'Ярославская область'), ('7700000000000', 'г. Москва'), ('7800000000000', 'Санкт-Петербург'), ('7900000000000', 'Еврейская автономная область'), ('8300000000000', 'Ненецкий автономный округ'), ('8600000000000', 'Ханты-Мансийский автономный округ - Югра автономный округ'), ('8700000000000', 'Чукотский автономный округ'), ('8900000000000', 'Ямало-Ненецкий автономный округ'), ('9100000000000', 'Республика Крым'), ('9200000000000', 'г. Севастополь'), ('9900000000000', 'г. Байконур')], max_length=13, verbose_name='регион')),
                ('area_with_type', models.CharField(blank=True, max_length=300, verbose_name='район в регионе с типом')),
                ('city_with_type', models.CharField(blank=True, max_length=300, verbose_name='город с типом')),
                ('city_district_with_type', models.CharField(blank=True, max_length=300, verbose_name='район города с типом')),
                ('settlement_with_type', models.CharField(blank=True, max_length=300, verbose_name='населенный пункт с типом')),
                ('street_with_type', models.CharField(blank=True, max_length=300, verbose_name='улица с типом')),
                ('house', models.CharField(blank=True, max_length=10, verbose_name='номер дома')),
                ('block', models.CharField(blank=True, max_length=10, verbose_name='корпус/строение')),
                ('flat', models.CharField(blank=True, max_length=10, verbose_name='номер квартиры')),
                ('addressDescription', models.CharField(blank=True, max_length=300, verbose_name='местонахождение проблемы своими словами')),
                ('latitude', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(-90), django.core.validators.MaxValueValidator(90)], verbose_name='широта')),
                ('longitude', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(-180), django.core.validators.MaxValueValidator(180)], verbose_name='долгота')),
                ('dateCreated', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('dateUnderReview', models.DateTimeField(blank=True, null=True, verbose_name='Дата смены статуса на "На рассмотрении"')),
                ('dateActive', models.DateTimeField(blank=True, null=True, verbose_name='Дата смены статуса на "На рассмотрении"')),
                ('dateInProgress', models.DateTimeField(blank=True, null=True, verbose_name='Дата смены статуса на "Ведутся работы"')),
                ('dateCompleted', models.DateTimeField(blank=True, null=True, verbose_name='Дата смены статуса на "Исполнена"')),
                ('dateClosed', models.DateTimeField(blank=True, null=True, verbose_name='Дата закрытия')),
                ('dateRejected', models.DateTimeField(blank=True, null=True, verbose_name='Дата отклонения')),
                ('signature_count', models.IntegerField(default=0, editable=False, verbose_name='Количество подписей')),
                ('account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_problems', to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='problems.category', verbose_name='категория')),
            ],
            options={
                'verbose_name': 'проблема',
                'verbose_name_plural': 'проблемы',
                'ordering': ['dateCreated'],
            },
        ),
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('uploaded_picture', models.ImageField(upload_to=problems.models.upload_picture_path, validators=[core.picture_compressor.validate_image], verbose_name='загруженное фото')),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='problem_picture', to='problems.problem')),
            ],
            options={
                'verbose_name': 'фото',
                'verbose_name_plural': 'фотографии',
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('comment', models.CharField(max_length=520, verbose_name='комментарий')),
                ('uploaded_picture', models.ImageField(blank=True, null=True, upload_to=problems.models.upload_picture_path, validators=[core.picture_compressor.validate_image], verbose_name='загруженное фото')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Дата комментария')),
                ('account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='problem_comment', to='problems.problem')),
            ],
            options={
                'verbose_name': 'комментарий',
                'verbose_name_plural': 'комментарии',
            },
        ),
        migrations.CreateModel(
            name='Signature',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='account_signatures', to=settings.AUTH_USER_MODEL)),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='problem_signatures', to='problems.problem')),
            ],
            options={
                'verbose_name': 'подпись',
                'verbose_name_plural': 'подписи',
                'unique_together': {('problem', 'account')},
            },
        ),
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='account_assignment', to=settings.AUTH_USER_MODEL)),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='problem_assignment', to='problems.problem')),
            ],
            options={
                'verbose_name': 'назначение',
                'verbose_name_plural': 'назначения',
                'unique_together': {('problem', 'account')},
            },
        ),
    ]
