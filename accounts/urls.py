from django.urls import include, path
from .views import BlacklistTokenUpdateView
from .views import ProfileUpdateView, ProfileDetailView, AccountListView, AccountUpdateView, AccountDeleteView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = 'accounts'

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/logout/blacklist/', BlacklistTokenUpdateView.as_view(),
         name='blacklist'),

    path('accounts/all/', AccountListView.as_view(), name='accounts_list'),
    path('accounts/update/<uuid:pk>/', AccountUpdateView.as_view(), name='account_update'),
    path('accounts/delete/<uuid:pk>/', AccountDeleteView.as_view(), name='account_delete'),
    path('profile/<uuid:pk>/', ProfileDetailView.as_view(), name='profile_detail'),
    path('profile/update/<uuid:pk>/', ProfileUpdateView.as_view(), name='profile_update'),
]
