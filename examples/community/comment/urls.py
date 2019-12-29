from django.urls import path
from comment import views

urlpatterns = [
    path('get_comments_view/', views.get_comments_view, name='get_comments_view'),

] 