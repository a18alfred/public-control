from django.contrib import admin
from .models import Problem, Picture, Category, Comment, Signature, Assignment


class PictureInline(admin.StackedInline):
    model = Picture
    extra = 3


class CommentInline(admin.StackedInline):
    model = Comment
    extra = 2


class ProblemAdmin(admin.ModelAdmin):
    readonly_fields = ['signature_count', 'is_published', 'dateCreated', 'dateUnderReview', 'dateActive',
                       'dateInProgress', 'dateCompleted', 'dateClosed', 'dateRejected']
    fieldsets = [
        (None,
         {'fields': ['account', 'description', 'category', 'status', 'urgency', 'is_published', 'signature_count']}),
        ('Адрес',
         {'fields': ['addressFull', 'postal_code', 'country', 'federal_district', 'region_iso', 'area_with_type',
                     'city_with_type', 'city_district_with_type', 'settlement_with_type', 'street_with_type', 'house',
                     'block',
                     'flat', 'addressDescription', 'latitude', 'longitude', ]}),
        ('Даты',
         {'fields': ['dateCreated', 'dateUnderReview', 'dateActive', 'dateInProgress', 'dateCompleted', 'dateClosed',
                     'dateRejected', ]}),
    ]
    inlines = [PictureInline, CommentInline]
    list_display = ('category', 'id', 'dateCreated', 'region_iso', 'urgency', 'status', 'is_published')
    list_filter = ['dateCreated', 'category', 'urgency',
                   'status', 'region_iso', 'is_published']
    search_fields = ['description', 'addressFull', ]


class CategoryAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'parent', 'icon', ]}),
    ]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Problem, ProblemAdmin)
admin.site.register(Signature)
admin.site.register(Assignment)
