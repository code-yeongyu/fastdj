from django.urls import path
from custom_user import views
from rest_framework.authtoken import views as drf_views

urlpatterns = [
    path('', views.ProfileAPIView.as_view(), name=''),
    path('<string>/', views.ProfileDetail.as_view(), name=''),
    path('auth/', drf_views.obtain_auth_token),
    path('register/', views.register, name='register'),

] 