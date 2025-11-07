from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post
from .forms import PostForm
# Groupモデルは使用しません（投稿のassociated_groupで集計するため）


def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    
    # --- グループ別いいね総数の集計 ---
    total_group_a_likes = 0
    total_group_b_likes = 0
    
    # 全ての投稿をループし、投稿の associated_group に応じていいね数を集計
    for post in posts:
        # 投稿のassociated_groupが'A'の場合、その投稿のいいね数をGroupAの総数に加算
        if post.associated_group == 'A':
            total_group_a_likes += post.total_likes()
        
        # 投稿のassociated_groupが'B'の場合、その投稿のいいね数をGroupBの総数に加算
        elif post.associated_group == 'B':
            total_group_b_likes += post.total_likes()
            
    # ---------------------------------
    
    context = {
        'posts': posts,
        'total_group_a_likes': total_group_a_likes,
        'total_group_b_likes': total_group_b_likes,
    }
    
    return render(request, 'posts/post_list.html', context)


@login_required
def post_create(request): # ★ 復活
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
def like_post(request, post_id): # ★ 復活
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('post_list')