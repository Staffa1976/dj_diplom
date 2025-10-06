from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Post, Comment, Like

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'text', 'created_at']
        read_only_fields = ['user', 'created_at']
        extra_kwargs = {'post': {'required': False }}


class PostSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'image', 'description', 'created_at', 'updated_at', 'user', 'likes_count', 'comments_count', 'comments']
        read_only_fields = ['created_at', 'updated_at', 'user']

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

class PostDetailSerializer(PostSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta(PostSerializer.Meta):
        fields = list(PostSerializer.Meta.fields) + ['comments', ]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'first_name', 'last_name']  # добавьте нужные поля

class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # используем отдельный сериализатор для пользователя
    post = serializers.StringRelatedField(read_only=True)  # если нужно только название поста

    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['created_at']

    def validate(self, data):
        # Проверяем уникальность лайка
        if Like.objects.filter(
            user=self.context['request'].user,
            post_id=self.context['view'].kwargs['post_id']
        ).exists():
            raise serializers.ValidationError("Вы уже поставили лайк этому посту")
        return data

