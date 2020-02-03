from django.urls import path
from article import views


urlpatterns = [
    path('', views.PostOverall.as_view(), name='PostOverall'),
    path('<int:id>/', views.PostDetail.as_view(), name='PostDetail'),
    path('my_posts_view/', views.my_posts_view, name='my_posts_view'),
    path('user_posts_view/', views.user_posts_view, name='user_posts_view'),

] 