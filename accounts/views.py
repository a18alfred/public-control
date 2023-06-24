from rest_framework.generics import (UpdateAPIView, RetrieveAPIView, ListAPIView, DestroyAPIView)
from django.http import Http404
from django_filters import rest_framework as filters
from .service import AccountFilter
from .models import Account, Profile
from .serializers import ProfileSerializer, AccountSerializer, AccountUpdateSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.response import Response
from .permissions import IsOwner, IsOwnerOrSuperUser, IsSuperUser
from rest_framework.permissions import IsAuthenticated


class AccountListView(ListAPIView):
    """
    Класс для получения списка аккаунтов с возможностью фильрации.
    Только для СуперЮзера
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsSuperUser, ]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = AccountFilter


class AccountUpdateView(UpdateAPIView):
    """
    Класс для внесения изменения в определённый аккаунт. Например права пользователя.
    Только для СуперЮзера.
    """
    queryset = Account.objects.all()
    serializer_class = AccountUpdateSerializer
    permission_classes = [IsSuperUser, ]


class AccountDeleteView(DestroyAPIView):
    """
    Класс для удаления аккаунта.
    Только для СуперЮзера
    """
    queryset = Account.objects.all()
    serializer_class = AccountUpdateSerializer
    permission_classes = [IsSuperUser, ]


class ProfileUpdateView(UpdateAPIView):
    """
    Класс для внесения изменений в профайл пользователя.
    Только для владельца профайла и СуперЮзера
    """
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrSuperUser, ]

    def get_object(self):
        pk = self.kwargs['pk']
        try:
            obj = Profile.objects.get(account_id=pk)
            self.check_object_permissions(self.request, obj)
            return obj
        except Profile.DoesNotExist:
            raise Http404


class ProfileDetailView(RetrieveAPIView):
    """
    Класс для получения профайла пользователя.
    Только для владельца профайла и СуперЮзера
    """
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrSuperUser, ]

    def get_object(self):
        pk = self.kwargs['pk']
        try:
            obj = Profile.objects.get(account_id=pk)
            self.check_object_permissions(self.request, obj)
            return obj
        except Profile.DoesNotExist:
            raise Http404


class BlacklistTokenUpdateView(APIView):
    """
    Используется для разлогинивания. Действующий refresh токен вносится в черный список.
    """
    permission_classes = [AllowAny]
    authentication_classes = ()

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
