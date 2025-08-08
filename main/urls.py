from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('player-stats/', views.player_stats, name='player_stats'),
    path('player-comparison/', views.player_comparison, name='player_comparison'),
    path('prediction/', views.match_prediction, name='match_prediction'),
    path('community/', views.posts, name='community'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('delete/<int:post_id>/', views.delete_post, name='delete_post'),
    path('news/', views.news_detail, name='news_detail'),
]