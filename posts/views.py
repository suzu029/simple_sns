# suzu029/simple_sns/simple_sns-980b52dbcc7f9528f8b8fcf88fa3333b1812607a/posts/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.views.generic.edit import UpdateView 
from django.urls import reverse_lazy 
from django.contrib import messages 

from .models import Post, UserProfile 
from .forms import PostForm, UserGroupForm, GroupNameForm 

# ★追加
from django.http import JsonResponse 
from django.views.decorators.http import require_POST 

from django.http import JsonResponse # ★この行を追加
from django.views.decorators.http import require_POST # ★この行を追加

from .models import Post, UserProfile # UserProfileをインポート
from .forms import PostForm, UserGroupForm, GroupNameForm

# ... (他のビュー関数は省略) ...

# ★★★ 既存の like_post 関数を修正 ★★★
@login_required
@require_POST # POSTメソッドのみ許可
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    liked = False
    
    if user in post.likes.all():
        post.likes.remove(user)
        action = 'unliked'
    else:
        post.likes.add(user)
        action = 'liked'
        liked = True

    # 新しいいいね総数を取得
    new_total_likes = post.total_likes()
    
    # JSONレスポンスを返す
    return JsonResponse({
        'status': 'ok',
        'post_id': post_id,
        'action': action,
        'total_likes': new_total_likes,
        'is_liked': liked
    })