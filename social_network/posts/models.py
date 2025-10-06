
from django.db import models
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

User = get_user_model()


class Post(models.Model):

    title = models.CharField(max_length=200, verbose_name='Заголовок', null=True, blank=True)
    image = models.ImageField(upload_to='images/', verbose_name='Изображение')
    description = models.TextField(verbose_name='Описание', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')

    def __str__(self):
        return self.title or 'Без заголовка'

    def clean(self):
        if not self.image:
            raise ValidationError({'image': 'Изображение не должно быть пустым'})

    def get_likes_count(self):
        # Возвращает количество лайков для поста
        return self.likes.count()

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-created_at']


# для доп. задания
# class PostImage(models.Model):
#     ...


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')



class Comment(models.Model):
    text = models.TextField(verbose_name='Текст комментария')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    update_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)


    def __str__(self):
        return f'Комментарий от пользователя {self.user.username} к посту {self.post.title}'

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']
