from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image', 'associated_group'] # ★ associated_group を追加
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
            # ★ associated_group をラジオボタンで表示
            'associated_group': forms.RadioSelect(), 
        }