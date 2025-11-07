from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post
from .forms import PostForm
from django.contrib.auth.models import Group  # Groupモデルをインポート


def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    
    # --- グループ別いいね総数の集計 ---
    total_group_a_likes = 0
    total_group_b_likes = 0
    
    try:
        group_a = Group.objects.get(name='GroupA')
        group_b = Group.objects.get(name='GroupB')
        
        # 全ての投稿をループし、GroupA/Bユーザーからのいいねをカウントして加算
        for post in posts:
            total_group_a_likes += post.likes.filter(groups=group_a).count()
            total_group_b_likes += post.likes.filter(groups=group_b).count()
            
    except Group.DoesNotExist:
        # GroupA または GroupB が存在しない場合は、総数は 0 のまま
        pass
    
    # 集計結果をコンテキストに追加
    context = {
        'posts': posts,
        'total_group_a_likes': total_group_a_likes,
        'total_group_b_likes': total_group_b_likes,
    }
    
    return render(request, 'posts/post_list.html', context)


@login_required
def post_create(request): # ★ 削除されていた関数を復活
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('post_list')
    else:
        form = PostForm()
    return render(request, 'posts/post_form.html', {'form': form})


@login_required
def like_post(request, post_id): # ★ 削除されていた関数を復活
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('post_list')