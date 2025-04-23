from django.urls import path
from .views import *
from market import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("", views.home, name="home"),
    path("confirm-email/<uidb64>/<token>/", views.confirm_email, name="confirm_email"),
    path('login/', views.login_view, name='login'),
    path('bike/', views.order_bike, name='bike'),
]
