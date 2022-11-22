from django.db import models
from core.models import CreatedModel
from django.contrib.auth import get_user_model

User = get_user_model()


class Post(CreatedModel):
    text = models.TextField('текст поста', help_text='текст нового поста')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='группа',
        help_text='Группа, к которой будет относиться пост')
    image = models.ImageField('Картиночка', upload_to='posts/', blank=True)

    class Meta:
        ordering = ('-created', )
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        default_related_name = 'posts'

    def __str__(post):
        return post.text[:15]


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(max_length=200)

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(group):
        return group.title


class Comment(CreatedModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(
        'Поделитесь своим неинтересным мнением', help_text='текст коммента')

    class Meta:
        ordering = ('-created', )
        default_related_name = 'comments'

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["author", "user"], name="unique_follower_following"
            )
        ]

    def __str__(self):
        return f"{self.user.username} подписан на {self.author.username}"
