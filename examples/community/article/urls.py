from django.urls import path
from article import views


urlpatterns = [
    path('user_posts_view/', views.user_posts_view, name='user_posts_view'),
    path('my_posts_view/', views.my_posts_view, name='my_posts_view'),
    path('<int:pk>/', views.PostDetail.as_view(), name='PostDetail'),
    path('', views.PostList.as_view(), name='PostList'),

] 