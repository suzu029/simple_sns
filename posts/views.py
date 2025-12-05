# suzu029/simple_sns/simple_sns-980b52dbcc7f9528f8b8fcf88fa3333b1812607a/posts/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.views.generic.edit import UpdateView 
from django.urls import reverse_lazy 
from django.contrib import messages 

from django.http import JsonResponse # ★追加
from django.views.decorators.http import require_POST # ★追加

from .models import Post, UserProfile 
from .forms import PostForm, UserGroupForm, GroupNameForm 


# ----------------------------------------------------
# 1. グループ名変更ビュー (group_name_setting_view)
# ----------------------------------------------------
@login_required
def group_name_setting_view(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=request.user)
        return redirect('group_name_setting')

    if request.method == 'POST':
        form = GroupNameForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'グループ名を更新しました。')
            return redirect('post_list')
    else:
        form = GroupNameForm(instance=user_profile)
    
    return render(request, 'posts/group_name_form.html', {'form': form})


# ----------------------------------------------------
# 2. 投稿一覧関数 (post_list)
# ----------------------------------------------------
def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    
    # --- グループ別いいね総数の集計 ---
    total_group_a_likes = 0
    total_group_b_likes = 0
    
    for post in posts:
        if post.associated_group == 'A':
            total_group_a_likes += post.total_likes()
        elif post.associated_group == 'B':
            total_group_b_likes += post.total_likes()
            
    # ---------------------------------
    
    # ログインユーザーのカスタムグループ名を取得
    group_a_display_name = 'Group A'
    group_b_display_name = 'Group B'
    if request.user.is_authenticated:
        try:
            user_profile = request.user.userprofile
            group_a_display_name = user_profile.group_a_name
            group_b_display_name = user_profile.group_b_name
        except UserProfile.DoesNotExist:
            pass


    context = {
        'posts': posts,
        'total_group_a_likes': total_group_a_likes,
        'total_group_b_likes': total_group_b_likes,
        'group_a_display_name': group_a_display_name, 
        'group_b_display_name': group_b_display_name, 
    }
    
    return render(request, 'posts/post_list.html', context)


# ----------------------------------------------------
# 3. 投稿作成関数 (post_create)
# ----------------------------------------------------
@login_required
def post_create(request):
    try:
        user_group = request.user.userprofile.associated_group
        if user_group == 'N':
            return redirect('set_user_group')
    except UserProfile.DoesNotExist:
        return redirect('set_user_group')
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.associated_group = user_group 
            post.save()
            return redirect('post_list')
    else:
        form = PostForm()
    return render(request, 'posts/post_form.html', {'form': form})


# ----------------------------------------------------
# 4. グループ選択ビュー (SetUserGroupView)
# ----------------------------------------------------
class SetUserGroupView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserGroupForm
    template_name = 'posts/set_user_group.html'
    success_url = reverse_lazy('post_list')

    def get_object(self, queryset=None):
        try:
            return self.request.user.userprofile
        except UserProfile.DoesNotExist:
            return UserProfile.objects.create(user=self.request.user, associated_group='N')
            
    def form_valid(self, form):
        messages.success(self.request, '所属グループを更新しました。')
        return super().form_valid(form)


# ----------------------------------------------------
# 5. いいね/いいね解除関数 (like_post) - Ajax対応済み
# ----------------------------------------------------
@login_required
@require_POST 
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

    new_total_likes = post.total_likes()
    
    return JsonResponse({
        'status': 'ok',
        'post_id': post_id,
        'action': action,
        'total_likes': new_total_likes,
        'is_liked': liked
    })