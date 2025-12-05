from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin # ★追加
from django.views.generic.edit import UpdateView # ★追加
from django.urls import reverse_lazy # ★追加
from django.contrib import messages # ★追加: メッセージフレームワーク

from .models import Post, UserProfile # UserProfileをインポート
from .forms import PostForm, UserGroupForm, GroupNameForm # ★GroupNameFormをインポート
# Groupモデルは使用しません（投稿のassociated_groupで集計するため）


# ★★★ 新規追加: グループ名変更ビュー ★★★
@login_required
def group_name_setting_view(request):
    # ログインユーザーのUserProfileインスタンスを取得
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        # プロフィールがない場合は作成してリダイレクト（念のため）
        UserProfile.objects.create(user=request.user)
        return redirect('group_name_setting')

    if request.method == 'POST':
        form = GroupNameForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'グループ名を更新しました。')
            return redirect('post_list') # ホーム画面へリダイレクト
    else:
        form = GroupNameForm(instance=user_profile)
    
    return render(request, 'posts/group_name_form.html', {'form': form})


# ★★★ 既存の post_list 関数 (修正) ★★★
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
    
    # ★追加/変更: ログインユーザーのカスタムグループ名を取得（未ログイン時はデフォルトを使用）
    group_a_display_name = 'Group A'
    group_b_display_name = 'Group B'
    if request.user.is_authenticated:
        try:
            user_profile = request.user.userprofile
            group_a_display_name = user_profile.group_a_name
            group_b_display_name = user_profile.group_b_name
        except UserProfile.DoesNotExist:
            # プロフィールがない場合はデフォルト名のまま（通常はsignalsで作成されるはず）
            pass


    context = {
        'posts': posts,
        'total_group_a_likes': total_group_a_likes,
        'total_group_b_likes': total_group_b_likes,
        'group_a_display_name': group_a_display_name, # ★追加
        'group_b_display_name': group_b_display_name, # ★追加
    }
    
    return render(request, 'posts/post_list.html', context)


# ★★★ 修正後の post_create 関数 (エラーの原因ではないが、元の関数を再確認) ★★★
@login_required
def post_create(request):
    # グループが未設定（'N'）の場合はグループ設定画面へリダイレクト
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


# ★★★ 既存の SetUserGroupView (修正) ★★★
class SetUserGroupView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserGroupForm
    template_name = 'posts/set_user_group.html'
    success_url = reverse_lazy('post_list')


    def get_object(self, queryset=None):
        try:
            # 既存のプロフィールを取得
            return self.request.user.userprofile
        except UserProfile.DoesNotExist:
            # プロフィールがない場合は作成して返す
            return UserProfile.objects.create(user=self.request.user, associated_group='N')
            
    # ★追加: 成功時にメッセージを表示
    def form_valid(self, form):
        messages.success(self.request, '所属グループを更新しました。')
        return super().form_valid(form)


# ★★★ 既存の like_post 関数 ★★★
@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('post_list')