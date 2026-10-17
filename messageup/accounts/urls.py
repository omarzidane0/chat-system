from django.urls import path
from .views import login, login_view, register_view , forgot_password_view ,register, logout_view, reset_password_view


urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('register_p/', register, name='register_p'),
    path('login_p/', login, name='login_p'),
    path('logout/', logout_view, name='logout'),
    path('reset-password/<str:token>/', reset_password_view, name='reset_password'),
]