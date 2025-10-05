from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from social_network.posts.views import PostViewSet, CommentViewSet, index

# Создаем роутер
router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')  # Базовый URL для постов

# Добавляем кастомные URL для комментариев
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),

    # Включаем роутинг DRF
    path('api/', include(router.urls)),  # Все API начинается с /api/

    # URL для работы с комментариями
    path('api/posts/<int:post_id>/comments/',
         CommentViewSet.as_view({
             'post': 'create',  # Создание комментария
             'get': 'list'  # Получение списка комментариев
         }),
         name='comment-list'),

    # URL для работы с конкретным комментарием
    path('api/posts/<int:post_id>/comments/',
         CommentViewSet.as_view({
             'get': 'retrieve',  # Получение комментария
             'put': 'update',  # Обновление комментария
             'patch': 'partial_update',  # Частичное обновление
             'delete': 'destroy'  # Удаление комментария
         }),
         name='comment-detail')
]