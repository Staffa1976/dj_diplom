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

class LikeSerializer(serializers.ModelSerializer):
    # Настраиваем отображение связанных полей
    user = serializers.StringRelatedField(read_only=True)
    post = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Like
        fields = '__all__'  # или явно указать все поля: ['user', 'post', 'created_at']
        read_only_fields = ['created_at']  # дата создания только для чтения

    # Дополнительная валидация, если нужно
    def validate(self, data):
        # Проверяем, что пользователь не может лайкнуть один пост дважды
        if Like.objects.filter(user=data['user'], post=data['post']).exists():
            raise serializers.ValidationError("Вы уже лайкнули этот пост")
        return data

