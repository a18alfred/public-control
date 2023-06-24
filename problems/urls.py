from django.urls import include, path
from .views import CategoryTreeView, CategoryCreateView, CategoryGetPutDeleteView, ProblemCreateView, ProblemDetailView, \
    ProblemPictureUploadView, ProblemPictureDeleteUpdateView, ProblemDeleteView, ProblemAddCommentView, \
    ProblemDeleteCommentView, SingProblemView, ProblemClosedByOwnerView, ProblemUpdateStatusByResponderView, \
    ProblemSuperUpdateView, ProblemModeratorUpdateView, ProblemUserCreatedListView, ProblemUserSignedListView, \
    AssignProblemView, AssignProblemDeleteView, ProblemUserAssignedListView, ProblemToModerateListView, \
    ProblemPublishedListView, StatisticsView, ProblemPublishedYandexMapListView, ProblemYandexMapBalloonView
from django.views.decorators.cache import cache_page

app_name = 'problems'

urlpatterns = [
    path('categories/all/', CategoryTreeView.as_view(), name='category_tree'),
    path('categories/create/', CategoryCreateView.as_view(), name='category_create'),
    path('categories/<uuid:pk>/', CategoryGetPutDeleteView.as_view(), name='category_update_delete'),
    path('problems/create/', ProblemCreateView.as_view(), name='problem_create'),
    path('problems/<uuid:pk>/', ProblemDetailView.as_view(), name='problem_detail'),
    path('problems/delete/<uuid:pk>/', ProblemDeleteView.as_view(), name='problem_delete'),
    path('problems/picture/upload/', ProblemPictureUploadView.as_view(), name='picture_upload'),
    path('problems/picture/update/<uuid:pk>/', ProblemPictureDeleteUpdateView.as_view(), name='picture_update_delete'),
    path('problems/comment/add/', ProblemAddCommentView.as_view(), name='comment_add'),
    path('problems/comment/delete/<uuid:pk>/', ProblemDeleteCommentView.as_view(), name='comment_delete'),
    path('problems/sign/', SingProblemView.as_view(), name='problem_sign'),
    path('problems/assign/', AssignProblemView.as_view(), name='problem_assign'),
    path('problems/assign/delete/<uuid:pk>/', AssignProblemDeleteView.as_view(), name='problem_assign_delete'),
    path('problems/close/<uuid:pk>/', ProblemClosedByOwnerView.as_view(), name='problem_close_by_owner'),
    path('problems/updatestatus/<uuid:pk>/', ProblemUpdateStatusByResponderView.as_view(),
         name='problem_update_status_by_responder'),
    path('problems/superupdate/<uuid:pk>/', ProblemSuperUpdateView.as_view(), name='problem_super_update'),
    path('problems/update/<uuid:pk>/', ProblemModeratorUpdateView.as_view(), name='problem_moderator_update'),
    path('problems/mylist/', ProblemUserCreatedListView.as_view(), name='problem_user_created'),
    path('problems/mysigned/', ProblemUserSignedListView.as_view(), name='problem_user_signed'),
    path('problems/myassigned/', ProblemUserAssignedListView.as_view(), name='problem_user_assigned'),
    path('problems/tomoderate/', ProblemToModerateListView.as_view(), name='problem_to_moderate_list'),
    path('problems/all/', ProblemPublishedListView.as_view(), name='problem_all_list'),
    path('problems/ymaplist/', ProblemPublishedYandexMapListView.as_view(),
         name='problem_yandex_map_list'),
    path('problems/ymapballoon/<uuid:pk>/', ProblemYandexMapBalloonView.as_view(),
         name='problem_yandex_map_balloon'),
    path('problems/stats/', StatisticsView.as_view(), name='get_stats'),
]
