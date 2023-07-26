from django.urls import path

from blog import views
from blog.views import (
    PostCreateView, UserProfileUpdateView, PostUpdateView,
    PostDeleteView, CommentCreateView,
    CommentUpdateView, CommentDeleteView
)

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:id>/', views.post_detail, name='post_detail'),
    path('category/<slug:category_slug>/',
         views.category_posts, name='category_posts'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('posts/create/', PostCreateView.as_view(), name='create_post'),
    path(
        'edit_profile/<int:pk>/',
        UserProfileUpdateView.as_view(),
        name='edit_profile'
        ),
    path('posts/<int:pk>/edit/', PostUpdateView.as_view(), name='edit_post'),
    path(
        'posts/<int:pk>/delete/',
        PostDeleteView.as_view(),
        name='delete_post'
        ),
    path(
        'posts/<int:post_id>/comment/',
        CommentCreateView.as_view(),
        name='add_comment'
        ),
    path(
        'posts/<int:post_id>/edit_comment/<int:pk>/',
        CommentUpdateView.as_view(),
        name='edit_comment'
        ),
    path(
        'posts/<int:post_id>/delete_comment/<int:pk>/',
        CommentDeleteView.as_view(),
        name='delete_comment'
        ),
]
