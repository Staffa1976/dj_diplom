from rest_framework import viewsets, permissions, status, exceptions
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render
from .models import Post, Like, Comment
from .serializers import (
    PostSerializer,
    LikeSerializer,
    CommentSerializer,
    PostDetailSerializer
)
from django.contrib.auth import get_user_model
from .permissions import IsAuthorOrReadOnly
from rest_framework.pagination import PageNumberPagination

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

User = get_user_model()


def index(request):
    return render(request, 'index.html')


class PostViewSet(viewsets.ModelViewSet):
    parser_classes = [MultiPartParser, FormParser]
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['created_at', 'updated_at']  # Фильтрация по датам
    search_fields = ['title', 'description']  # Поиск по полям
    ordering_fields = ['created_at', 'updated_at']  # Сортировка по датам

    def get_permissions(self):
        # Разрешаем анонимный доступ для GET-запросов
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [permissions.AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PostDetailSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # Удаление поста
    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LikeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    permission_classes=PageNumberPagination

    def create(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)

        if Like.objects.filter(post=post, user=request.user).exists():
            return Response({'detail': 'Вы уже поставили лайк'}, status=status.HTTP_400_BAD_REQUEST)

        like = Like.objects.create(post=post, user=request.user)
        serializer = LikeSerializer(like, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        like = get_object_or_404(Like, post=post, user=request.user)
        like.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        likes = post.likes.all()
        serializer = LikeSerializer(likes, many=True, context={'request': request})
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    lookup_field = 'id'  # указываем, что ищем по полю id
    lookup_url_kwarg = 'comment_id'  # указываем имя параметра в URL
    pagination_class = PageNumberPagination

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['created_at']
    ordering_fields = ['created_at']


    # Определяем разрешения для разных действий
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated, IsAuthorOrReadOnly]
        return super().get_permissions()

    def get_queryset(self):
        try:
            post_id = self.kwargs.get('post_id')
            return Comment.objects.filter(post_id=post_id)
        except Exception as e:
            raise exceptions.APIException(f"Ошибка при получении комментариев: {str(e)}")

    def perform_create(self, serializer):
        try:
            post_id = self.kwargs.get('post_id')
            post = Post.objects.get(id=post_id)  # Проверяем существование поста
            serializer.save(
                user=self.request.user,
                post_id=post_id
            )
        except Post.DoesNotExist:
            raise exceptions.NotFound("Пост не найден")
        except Exception as e:
            raise exceptions.APIException(f"Ошибка при создании комментария: {str(e)}")

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise exceptions.PermissionDenied("Только автор может удалить комментарий")
        instance.delete()