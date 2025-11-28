from django import forms
from .models import Post, UserProfile 

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image'] 
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }

# ★ 新規追加: ユーザーグループ設定フォーム
class UserGroupForm(forms.ModelForm):
    GROUP_CHOICES_LOGIN = [
        ('A', 'GroupA'),
        ('B', 'GroupB'),
    ]
    # associated_groupを必須フィールドにし、choicesを変更
    associated_group = forms.ChoiceField(
        choices=GROUP_CHOICES_LOGIN,
        widget=forms.RadioSelect,
        label='関連付けグループ',
        required=True
    )
    
    class Meta:
        model = UserProfile
        fields = ['associated_group']