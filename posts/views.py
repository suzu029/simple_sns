from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin # ★追加
from django.views.generic.edit import UpdateView # ★追加
from django.urls import reverse_lazy # ★追加

from .models import Post, UserProfile # UserProfileをインポート
from .forms import PostForm, UserGroupForm # UserGroupFormをインポート
# Groupモデルは使用しません（投稿のassociated_groupで集計するため）


# ★★★ 既存の post_list 関数 ★★★
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
    
    context = {
        'posts': posts,
        'total_group_a_likes': total_group_a_likes,
        'total_group_b_likes': total_group_b_likes,
    }
    
    return render(request, 'posts/post_list.html', context)


# ★★★ 修正後の post_create 関数 ★★★
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
            # 投稿者のUserProfileからグループを取得して設定
            post.associated_group = user_group 
            post.save()
            return redirect('post_list')
    else:
        form = PostForm()
    return render(request, 'posts/post_form.html', {'form': form})


# ★★★ 新規追加の SetUserGroupView クラス (Class-Based View) ★★★
class SetUserGroupView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserGroupForm
    template_name = 'posts/set_user_group.html'
    success_url = reverse_lazy('post_list')

    # ログインユーザーのUserProfileオブジェクトを取得または新規作成する
    def get_object(self, queryset=None):
        try:
            # 既存のプロフィールを取得
            return self.request.user.userprofile
        except UserProfile.DoesNotExist:
            # プロフィールが存在しない場合、新規作成して返す
            return UserProfile.objects.create(user=self.request.user, associated_group='N')


# ★★★ 既存の like_post 関数 ★★★
@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('post_list')