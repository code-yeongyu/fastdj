from django.urls import path
from custom_user import views

urlpatterns = [
    path('', views.ProfileAPIView.as_view(), name=''),
    path('<string>/', views.ProfileDetail.as_view(), name=''),
    path('register/', views.register, name='register'),

] 