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

User = get_user_model()


def index(request):
    return render(request, 'index.html')


class PostViewSet(viewsets.ModelViewSet):
    parser_classes = [MultiPartParser, FormParser]
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']

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
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {'error': 'Только автор может удалить пост'},
                status=status.HTTP_403_FORBIDDEN
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class LikeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

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

    # Определяем разрешения для разных действий
    def get_permissions(self):
        # Для GET-запросов разрешаем доступ всем
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        # Для остальных действий (создание, обновление, удаление) требуется авторизация
        return [permissions.IsAuthenticated()]

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