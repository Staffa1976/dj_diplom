from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Post, Like, Comment
from .serializers import (
    PostSerializer,
    LikeSerializer,
    CommentSerializer,
    PostDetailSerializer
)
from django.contrib.auth import get_user_model

User = get_user_model()

class PostViewSet(viewsets.ModelViewSet):
    parser_classes = [MultiPartParser, FormParser]
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PostDetailSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create_like(self, request, pk=None):
        post = self.get_object()
        user = request.user
        like, created = Like.objects.get_or_create(user=user, post=post)
        if created:
            return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)
        return Response({'status': 'already liked'}, status=status.HTTP_400_BAD_REQUEST)

    def delete_like(self, request, pk=None):
        post = self.get_object()
        user = request.user
        like = get_object_or_404(Like, user=user, post=post)
        like.delete()
        return Response({'status': 'unliked'}, status=status.HTTP_204_NO_CONTENT)

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs['post_pk'])
        return Comment.objects.filter(post=post)

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs['post_pk'])
        serializer.save(user=self.request.user, post=post)

class LikeViewSet(viewsets.GenericViewSet):
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Like.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['post_pk'])
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if created:
            return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)
        return Response({'status': 'already liked'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['post_pk'])
        like = get_object_or_404(Like, user=request.user, post=post)
        like.delete()
        return Response({'status': 'unliked'}, status=status.HTTP_204_NO_CONTENT)

