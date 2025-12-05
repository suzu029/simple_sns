from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver 
from django.core.exceptions import ObjectDoesNotExist #

# PostとUserProfileで共通のグループ選択肢のキー (表示名はUserProfileから取得)
GROUP_KEYS = [ 
    ('A', 'GroupA'), 
    ('B', 'GroupB'), 
    ('N', 'None'), 
]

class UserProfile(models.Model): 
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    associated_group = models.CharField(
        max_length=1,
        choices=GROUP_KEYS, 
        default='N',
        verbose_name='関連付けグループ'
    )
    # ★追加: ユーザーが任意で設定するグループ名
    group_a_name = models.CharField(max_length=50, default='Group A')
    group_b_name = models.CharField(max_length=50, default='Group B')
    
    def __str__(self):
        return self.user.username

    # ★追加/変更: グループキーに対応する表示名を取得するヘルパーメソッド
    def get_group_display_name(self, key):
        if key == 'A':
            return self.group_a_name
        elif key == 'B':
            return self.group_b_name
        return 'None'

    # get_associated_group_display メソッドは、現在の所属グループ名を取得
    def get_associated_group_display(self):
        return self.get_group_display_name(self.associated_group)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # ★変更: デフォルトのグループ名を設定してUserProfileを作成
        UserProfile.objects.create(user=instance, associated_group='N', group_a_name='Group A', group_b_name='Group B')

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        # ★変更: デフォルトのグループ名を設定してUserProfileを作成
        UserProfile.objects.create(user=instance, associated_group='N', group_a_name='Group A', group_b_name='Group B')


class Post(models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField() 
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    
    associated_group = models.CharField(
        max_length=1,
        choices=GROUP_KEYS, 
        default='N',
        verbose_name='関連付けグループ'
    )

    def __str__(self):
        return self.content[:20]
    
    def total_likes(self):
        return self.likes.count()
    
    # Postのget_associated_group_displayは、投稿者のUserProfileから表示名を取得
    def get_associated_group_display(self):
        key = self.associated_group
        if key == 'N':
            return 'None'
        try:
            # ★変更: 投稿者のUserProfileからカスタム名を取得
            return self.user.userprofile.get_group_display_name(key)
        except UserProfile.DoesNotExist:
            return f"Group{key} (投稿者プロフィールなし)"