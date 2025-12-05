from django.urls import path
from .views import post_list, post_create, SetUserGroupView, like_post, group_name_setting_view # ★変更: インポートを明示的にし、group_name_setting_viewを追加

urlpatterns = [
    path('', post_list, name='post_list'),
    path('new/', post_create, name='post_create'),
    path('set-group/', SetUserGroupView.as_view(), name='set_user_group'), 
    path('<int:post_id>/like/', like_post, name='like_post'),
    # ★追加: グループ名変更画面のURL
    path('set-group-name/', group_name_setting_view, name='group_name_setting'),
]