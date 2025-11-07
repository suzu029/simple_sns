from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('new/', views.post_create, name='post_create'),
    # ★変更: クラスベースビューを使うように修正
    path('set-group/', views.SetUserGroupView.as_view(), name='set_user_group'), 
    path('<int:post_id>/like/', views.like_post, name='like_post'),
]