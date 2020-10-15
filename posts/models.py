from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts')
    group = models.ForeignKey(Group, related_name='posts',
                              blank=True, null=True,
                              on_delete=models.SET_NULL)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts_comment')
    text = models.TextField()
    created = models.DateTimeField('date published', auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, # пользователь, который подписывается
                             related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE, # пользователь, на которого подписываются
                             related_name='following')

    class Meta:
        unique_together = ('user', 'author')