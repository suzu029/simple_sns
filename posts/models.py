from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver 

# PostとUserProfileで共通のグループ選択肢
GROUP_CHOICES = [
    ('A', 'GroupA'),
    ('B', 'GroupB'),
    ('N', 'None'), 
]

class UserProfile(models.Model): 
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    associated_group = models.CharField(
        max_length=1,
        choices=GROUP_CHOICES,
        default='N',
        verbose_name='関連付けグループ'
    )
    
    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance, associated_group='N')

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance, associated_group='N')


class Post(models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField() 
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    
    associated_group = models.CharField(
        max_length=1,
        choices=GROUP_CHOICES, 
        default='N',
        verbose_name='関連付けグループ'
    )

    def __str__(self):
        return self.content[:20]

    def total_likes(self):
        return self.likes.count()