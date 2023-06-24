from django_filters import rest_framework as filters
from .models import Problem, Assignment, Signature, Category
from core.constants import PROBLEM_STATUS
from django.contrib.contenttypes.models import ContentType


class ProblemFilter(filters.FilterSet):
    """
    Фильтр для работы со списком проблем
    """
    latitude = filters.RangeFilter()
    longitude = filters.RangeFilter()
    status = filters.MultipleChoiceFilter(choices=PROBLEM_STATUS)
    category = filters.AllValuesMultipleFilter()

    o = filters.OrderingFilter(fields=['dateCreated', 'signature_count'])

    class Meta:
        model = Problem
        fields = ['category', 'status', 'urgency', 'region_iso', 'latitude', 'longitude', ]


class ProblemStatsFilter(filters.FilterSet):
    """
    Фильтр для работы со статистикой проблем
    """
    category = filters.AllValuesMultipleFilter()

    class Meta:
        model = Problem
        fields = ['category', 'urgency', ]


def is_signed(obj, user) -> bool:
    """
    Проверяем подписался ли пользователь под проблемой
    """
    if not user.is_authenticated:
        return False

    # if Signature.objects.filter(account=user, problem=obj):
    #     return True
    if user.account_signatures.filter(problem=obj):
        return True
    return False


def is_assigned(obj, user) -> bool:
    """
    Проверяем назначина ли проблема пользователю
    """
    if not user.is_authenticated:
        return False

    # if Assignment.objects.filter(account=user, problem=obj):
    #     return True
    if user.account_assignment.filter(problem=obj):
        return True
    return False


def create_dummy_problems():
    """
    Создание большого кол-ва проблем для тестов
    """
    Problem.objects.all().delete()
    lon_start = 53.165
    lat = 56.874
    inc = 0.015

    for x in range(50):
        lon = lon_start
        for x in range(50):
            Problem.objects.create(account_id='e71c7114-71af-4946-bdbd-631fa85c8ad7',
                                   category_id='250cd9bf-3a51-4b97-a28b-b5e6f2706a74',
                                   description='test',
                                   is_published=True,
                                   status='active',
                                   region_iso='RU-UD',
                                   latitude=lat, longitude=lon)

            lon = lon + inc
        lat = lat + inc
