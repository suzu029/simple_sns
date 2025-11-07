from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    # 投稿を関連付けるグループの選択肢 (★追加)
    GROUP_CHOICES = [
        ('A', 'GroupA'),
        ('B', 'GroupB'),
        ('N', 'None'), 
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    
    # ★ 追加: 投稿がどのグループに関連付けられるか
    associated_group = models.CharField(
        max_length=1,
        choices=GROUP_CHOICES,
        default='N',
        verbose_name='関連付けグループ'
    )

    def __str__(self):
        return self.content[:20]

    def total_likes(self):
        return self.likes.count()  # いいね数を数えるメソッド