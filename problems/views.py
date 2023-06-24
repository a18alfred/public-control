from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.generics import (UpdateAPIView, RetrieveAPIView, ListAPIView, DestroyAPIView, CreateAPIView,
                                     RetrieveUpdateDestroyAPIView)
from rest_framework.views import APIView
from .serializers import CategorySerializer, CategoryPostPutDeleteSerializer, ProblemCreateSerializer, \
    ProblemGetSerializer, PictureSerializer, CommentSerializer, SignatureSerializer, ProblemStatusSerializer, \
    ProblemSuperSerializer, ProblemOnlyStatusCategorySerializer, ProblemListSerializer, AssignmentSerializer, \
    ProblemYandexMapListSerializer, ProblemYandexMapBalloonSerializer
from .models import Category, Picture, Comment, Problem, Signature, Assignment
from accounts.permissions import IsSuperUser, IsOwnerOrSuperUserOrModerator, IsOwnerOrSpecialUser, IsOwner, \
    IsResponderUser, IsSuperUserOrModeratorUser, IsSpecialUser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.response import Response
from django.conf import settings
from django_filters import rest_framework as filters
from .service import ProblemFilter, ProblemStatsFilter
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from core.constants import REGION_CODES


@method_decorator(cache_page(60), name='dispatch')
class CategoryTreeView(ListAPIView):
    """
    Класс для получения списка всех категорий в виде дерева.
    """
    pagination_class = None
    queryset = Category.objects.root_nodes()
    serializer_class = CategorySerializer


class CategoryCreateView(CreateAPIView):
    """
    Класс для создания новой категории
    """
    permission_classes = [IsSuperUser, ]
    queryset = Category.objects.all()
    serializer_class = CategoryPostPutDeleteSerializer


class CategoryGetPutDeleteView(RetrieveUpdateDestroyAPIView):
    """
    Класс для удалеия и изменения категории
    """
    permission_classes = [IsSuperUser, ]
    queryset = Category.objects.all()
    serializer_class = CategoryPostPutDeleteSerializer


class ProblemPictureUploadView(CreateAPIView, IsOwnerOrSuperUserOrModerator):
    """
    Класс для загрузки фотографий к проблеме
    """
    permission_classes = [IsAuthenticated, ]
    queryset = Picture.objects.all()
    serializer_class = PictureSerializer

    def create(self, request, *args, **kwargs):
        """
        Перед загрузкой проверяем, что пользователю принадлежит проблема
        400 если превышено максимальное колличество фото для одной проблемы
        403 если недостаточно прав для загрузки фото для данной проблемы
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not self.has_object_permission(request=request, view=self,
                                          obj=serializer.validated_data['problem']):
            return Response({"account": "Недостаточно прав для выпонения данного дейсвия"},
                            status=status.HTTP_403_FORBIDDEN)

        if Picture.objects.filter(
                problem=serializer.validated_data['problem']).count() >= settings.MAX_NUMBER_PICTURES_PER_PROBLEM:
            return Response(
                {"picture": "Превышено максимально число фотографий: %s" % settings.MAX_NUMBER_PICTURES_PER_PROBLEM},
                status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ProblemPictureDeleteUpdateView(RetrieveUpdateDestroyAPIView, IsOwnerOrSuperUserOrModerator):
    """
    Класс для удаления и обновления фотографии
    Удалить может только собственник, модератор и суперюзер
    """
    permission_classes = [IsAuthenticated, ]
    queryset = Picture.objects.all()
    serializer_class = PictureSerializer

    def retrieve(self, request, *args, **kwargs):
        return Response({"detail": "Метод \"GET\" не разрешен."},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def put(self, request, *args, **kwargs):
        return Response({"detail": "Метод \"PUT\" не разрешен."},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        if not self.has_object_permission(request=request, view=self,
                                          obj=instance.problem):
            return Response({"account": "Недостаточно прав для выпонения данного дейсвия"},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if not self.has_object_permission(request=request, view=self,
                                          obj=instance.problem):
            return Response({"account": "Недостаточно прав для выпонения данного дейсвия"},
                            status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProblemAddCommentView(CreateAPIView, IsOwnerOrSpecialUser):
    """
    Класс для добавления комментария к проблеме.
    Комментарий может оставить только пользователь, который создал проблему или
    специальный пользователь: модератор, суперюзер или представитель
    """
    permission_classes = [IsAuthenticated, ]
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def create(self, request, *args, **kwargs):
        """
        Перед добавлением проверяем, что пользователю принадлежит проблема
        403 если недостаточно прав для оставления комментария
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not self.has_object_permission(request=request, view=self,
                                          obj=serializer.validated_data['problem']):
            return Response({"account": "Недостаточно прав для выпонения данного дейсвия"},
                            status=status.HTTP_403_FORBIDDEN)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(account=self.request.user)


class ProblemDeleteCommentView(DestroyAPIView):
    """
    Класс для удаления фотографии
    Может удалить только пользователь загрузивший фото, модератор или суперюзер
    """
    permission_classes = [IsOwnerOrSuperUserOrModerator, ]
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class SingProblemView(CreateAPIView):
    """
    Класс для создания подписи под проблемой
    Любой пользователь может оставить подпись под проблемой
    """
    permission_classes = [IsAuthenticated, ]
    queryset = Signature.objects.all()
    serializer_class = SignatureSerializer

    def create(self, request, *args, **kwargs):
        """
        Перед добавлением подписи проверяем, что поле account совпадает с пользователем
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not serializer.validated_data['account'] == self.request.user:
            return Response({"account": "Недостаточно прав для выпонения данного дейсвия"},
                            status=status.HTTP_403_FORBIDDEN)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(account=self.request.user)


class AssignProblemView(CreateAPIView):
    """
    Класс для назначение проблемы к конкретному модератору или представителю
    """
    permission_classes = [IsSpecialUser, ]
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer

    def create(self, request, *args, **kwargs):
        """
        Перед добавлением подписи проверяем, что поле account совпадает с пользователем
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not serializer.validated_data['account'] == self.request.user:
            return Response({"account": "Недостаточно прав для выпонения данного дейсвия"},
                            status=status.HTTP_403_FORBIDDEN)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(account=self.request.user)


class AssignProblemDeleteView(DestroyAPIView):
    """
    Класс для удаления назначения проблемы к конкретному модератору или представителю
    """
    permission_classes = [IsAuthenticated, IsOwner, ]
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ProblemCreateView(CreateAPIView):
    """
    Класс для создания новой проблемы.
    400 ошибка если регион проблемы не совпадает с регионом пользователя
    Проблему может создать любой зарегистрированный пользователь
    """
    permission_classes = [IsAuthenticated, ]
    queryset = Problem.objects.all()
    serializer_class = ProblemCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not serializer.validated_data['region_iso'] == self.request.user.account_profile.region_iso:
            return Response({"region_iso": "Регион пользователя не совпадает с регионом проблемы"},
                            status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(account=self.request.user)


class ProblemDetailView(RetrieveAPIView):
    """
    Класс для получения детальной информации по проблеме
    """
    queryset = Problem.objects.all()
    serializer_class = ProblemGetSerializer


class ProblemDeleteView(DestroyAPIView):
    """
    Класс для удаления проблемы.
    Удалить может создатель, модератор и суперюзер
    """
    permission_classes = [IsOwnerOrSuperUserOrModerator, ]
    queryset = Problem.objects.all()
    serializer_class = ProblemCreateSerializer


class ProblemClosedByOwnerView(UpdateAPIView):
    """
    Класс для закрытие проблемы пользователем, который её создал
    """
    permission_classes = [IsAuthenticated, IsOwner, ]
    queryset = Problem.objects.all()
    serializer_class = ProblemStatusSerializer

    def put(self, request, *args, **kwargs):
        return Response({"detail": "Метод \"PUT\" не разрешен."},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        if not serializer.validated_data['status'] == 'closed':
            return Response({"status": "Статус можно поменять только на closed"},
                            status=status.HTTP_403_FORBIDDEN)

        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class ProblemUpdateStatusByResponderView(UpdateAPIView):
    """
    Класс для изменения статуса на:
    in_progress Проблема была замечена и решается
    completed Проблема решена
    Поменять может представитель УК или власти.
    """
    permission_classes = [IsResponderUser, ]
    queryset = Problem.objects.all()
    serializer_class = ProblemStatusSerializer

    def put(self, request, *args, **kwargs):
        return Response({"detail": "Метод \"PUT\" не разрешен."},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        if not serializer.validated_data['status'] == 'in_progress' and \
                not serializer.validated_data['status'] == 'completed':
            return Response({"status": "Статус можно поменять только на in_progress или completed"},
                            status=status.HTTP_403_FORBIDDEN)

        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class ProblemSuperUpdateView(UpdateAPIView):
    """
    Класс для внесение глобальных изменений в проблему. Действие доступно только суперюзеру
    """
    permission_classes = [IsSuperUser, ]
    queryset = Problem.objects.all()
    serializer_class = ProblemSuperSerializer


class ProblemModeratorUpdateView(UpdateAPIView):
    """
    Класс для изменения статуса и категории проблемы. Только для модератора или суперюзера
    """
    permission_classes = [IsSuperUserOrModeratorUser, ]
    queryset = Problem.objects.all()
    serializer_class = ProblemOnlyStatusCategorySerializer

    def put(self, request, *args, **kwargs):
        return Response({"detail": "Метод \"PUT\" не разрешен."},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ProblemUserCreatedListView(ListAPIView):
    """
    Класс для получения списка всех проблем созданных пользователем
    """
    permission_classes = [IsAuthenticated, ]
    serializer_class = ProblemListSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProblemFilter

    def get_queryset(self):
        return self.request.user.created_problems.all()


class ProblemUserSignedListView(ListAPIView):
    """
    Класс для получения списка всех проблем, которые были подписаны пользователем
    """
    permission_classes = [IsAuthenticated, ]
    serializer_class = ProblemListSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProblemFilter

    def get_queryset(self):
        return Problem.objects.filter(problem_signatures__account=self.request.user)


class ProblemUserAssignedListView(ListAPIView):
    """
    Класс для получения списка всех проблем, которые были назначены пользователю (модератору или представителю)
    """
    permission_classes = [IsSpecialUser, ]
    serializer_class = ProblemListSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProblemFilter

    def get_queryset(self):
        return Problem.objects.filter(problem_assignment__account=self.request.user)


class ProblemToModerateListView(ListAPIView):
    """
    Класс для получения списка всех проблем, которые нуждаются модерации, так как только что созданы
    """
    permission_classes = [IsSuperUserOrModeratorUser, ]
    serializer_class = ProblemListSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProblemFilter

    def get_queryset(self):
        return Problem.objects.filter(status='created')


class ProblemPublishedListView(ListAPIView):
    """
    Класс для получения списка всех проблем, которые были опубликованы
    """
    serializer_class = ProblemListSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProblemFilter

    def get_queryset(self):
        return Problem.objects.filter(is_published=True)


@method_decorator(cache_page(60 * 5), name='dispatch')
class ProblemPublishedYandexMapListView(ListAPIView):
    """
    Класс для получения списка всех проблем, которые были опубликованы.
    Специальный лист для яндекс карты
    """
    pagination_class = None
    serializer_class = ProblemYandexMapListSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProblemFilter

    def get_queryset(self):
        return Problem.objects.filter(is_published=True)

    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())
    #
    #     serializer = self.get_serializer(queryset, many=True)
    #     response = {'type': 'FeatureCollection', 'features': serializer.data}
    #     return Response(response)


class ProblemYandexMapBalloonView(RetrieveAPIView):
    """
    Класс для получения краткой информации по проблеме для яндекс балуна
    """
    permission_classes = (AllowAny,)
    queryset = Problem.objects.all()
    serializer_class = ProblemYandexMapBalloonSerializer


@method_decorator(cache_page(60 * 5), name='dispatch')
class StatisticsView(RetrieveAPIView):
    """
    Класс для получения статистико по проблемам с фильтрами по региону и срочности.
    """
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProblemStatsFilter

    def get_queryset(self):
        return Problem.objects.filter(is_published=True)

    def summarize(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        region_data = {}
        for ISO in REGION_CODES:
            region_queryset = queryset.filter(region_iso=ISO[0])
            region_data.update({
                ISO[0]: {
                    "total": region_queryset.count(),
                    "active": region_queryset.exclude(status='closed').count(),
                    "closed": region_queryset.filter(status='closed').count()
                }
            })

        stats = {"total": queryset.count(),
                 "active": queryset.exclude(status='closed').count(),
                 "closed": queryset.filter(status='closed').count(),
                 "region_data": region_data}

        return Response(stats)

    def get(self, request, *args, **kwargs):
        return self.summarize(request, *args, **kwargs)
