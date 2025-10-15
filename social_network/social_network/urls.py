from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

from posts.views import PostViewSet, CommentViewSet, LikeViewSet, index

# Создаем роутер
router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')  # Базовый URL для постов

# Добавляем кастомные URL для комментариев
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),

    # Включаем роутинг DRF
    path('api/', include(router.urls)),  # Все API начинается с /api/

    # URL для получения списка комментариев и создание нового
    path('api/posts/<int:post_id>/comments/',
         CommentViewSet.as_view({
             'post': 'create',  # Создание комментария
             'get': 'list'  # Получение списка комментариев
         }),
         name='comment-list'),

    # Работа с конкретным комментарием
    path(
        'api/posts/<int:post_id>/comments/<int:comment_id>/',
        CommentViewSet.as_view({
            'get': 'retrieve',        # Получение комментария
            'put': 'update',         # Обновление комментария
            'patch': 'partial_update', # Частичное обновление
            'delete': 'destroy'      # Удаление комментария
        }),
        name='comment-detail'
    ),

path(
        'api/posts/<int:post_id>/likes/',
        LikeViewSet.as_view({
            'get': 'list',
            'post': 'create',
            'delete': 'destroy'
        }),
        name='like-list'
    ),
    path(
        'api/posts/<int:post_id>/likes/<int:like_id>/',
        LikeViewSet.as_view({
            'get': 'retrieve',
            'delete': 'destroy'
        }),
        name='like-detail'
    )
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)