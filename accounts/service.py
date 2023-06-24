from django_filters import rest_framework as filters
from .models import Account, Profile


class ProfileFilter(filters.FilterSet):
    region_iso = filters.CharFilter(field_name='region_iso', lookup_expr='exact')

    class Meta:
        model = Profile
        fields = ['region_iso']


class AccountFilter(filters.FilterSet):
    """
    Фильтр для работы со списком акаунтов
    """

    email = filters.CharFilter(field_name='email', lookup_expr='contains')
    phone_number = filters.CharFilter(field_name='phone_number', lookup_expr='contains')
    is_active = filters.BooleanFilter(field_name='is_active')
    is_superuser = filters.BooleanFilter(field_name='is_superuser')
    is_moderator = filters.BooleanFilter(field_name='is_moderator')
    is_government = filters.BooleanFilter(field_name='is_government')
    is_management_company = filters.BooleanFilter(field_name='is_management_company')
    is_phone_confirmed = filters.BooleanFilter(field_name='is_phone_confirmed')
    date_joined = filters.DateTimeFromToRangeFilter()

    region_iso = filters.CharFilter(field_name='account_profile__region_iso')

    o = filters.OrderingFilter(fields=['email', 'date_joined', ])

    class Meta:
        model = Account
        fields = ['email', 'phone_number', 'is_active', 'is_superuser', 'is_moderator', 'is_government',
                  'is_management_company', 'is_phone_confirmed', 'region_iso', 'date_joined']
