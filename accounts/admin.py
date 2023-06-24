from django.contrib import admin
from .models import Account, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    fieldsets = [
        (None, {
            'fields': ['first_name', 'middle_name', 'last_name', 'date_of_birth', 'avatar']}),
        ('Адрес пользователя',
         {'fields': ['addressFull', 'postal_code', 'country', 'federal_district', 'region_iso', 'area_with_type',
                     'city_with_type', 'city_district_with_type', 'settlement_with_type', 'street_with_type', 'house',
                     'block',
                     'flat', ]}),
        ('Компания', {'fields': ['company_name', 'company_inn', 'position']}),
    ]


class AccountAdmin(admin.ModelAdmin):
    readonly_fields = ['email']
    fieldsets = [
        (None, {'fields': ['email', 'phone_number', 'is_phone_confirmed', ]}),
        ('Права',
         {'fields': ['is_active', 'is_staff', 'is_moderator', 'is_government',
                     'is_management_company']}),
        ('Суперпользователь',
         {'fields': ['is_superuser']}),
        ('Даты',
         {'fields': ['date_joined', 'last_login']}),

    ]

    inlines = [ProfileInline, ]
    list_display = ('email', 'date_joined', 'is_active', 'is_moderator', 'is_government',
                    'is_management_company', 'is_superuser',)
    list_filter = ['date_joined', 'is_active', 'is_moderator', 'is_government',
                   'is_management_company', 'is_superuser', ]
    search_fields = ['email']


admin.site.register(Account, AccountAdmin)
