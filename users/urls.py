from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

app_name = 'users'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='users:login'), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/<int:pk>/', views.profile_detail, name='profile_detail'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('search/', views.search_matches, name='search'),
    path('like/<int:user_id>/', views.like_profile, name='like_profile'),
    path('matches/', views.matches_list, name='matches'),
    path('blog/new/', views.create_blog_post, name='create_blog_post'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<int:post_id>/', views.blog_detail, name='blog_detail'),
    path('blog/<int:post_id>/edit/', views.edit_blog_post, name='edit_blog_post'),
    path('blog/<int:post_id>/like/', views.like_blog_post, name='like_blog_post'),
    path('chat/', views.chat_inbox, name='chat_inbox'),
    path('chat/<int:user_id>/', views.chat_room, name='chat_room'),
    path('chat/<int:user_id>/send/', views.send_message, name='send_message'),
    path('chat/unread/', views.get_unread_count, name='get_unread_count'),
    path('map/', views.map_view, name='map_view'),
    path('api/map-users/', views.map_users_api, name='map_users_api'),
    path('update-location/', views.update_location, name='update_location'),
]
