from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .import views

urlpatterns = [
    path("home", views.inicio, name="home"),
    path("", LoginView.as_view(template_name='auth/login.html'), name='login'),
    path("logout/", LogoutView.as_view(template_name='auth/logout.html'), name='logout'),
]
