from django import forms
from .models import Post, UserProfile 

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image'] 
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }

# ★ 既存のUserGroupFormは変更なし
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

# ★新規追加: ユーザーがグループ名を設定するためのフォーム
class GroupNameForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['group_a_name', 'group_b_name']
        labels = {
            'group_a_name': 'グループAの表示名',
            'group_b_name': 'グループBの表示名',
        }