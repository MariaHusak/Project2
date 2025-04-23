from django.contrib import admin
from django.urls import path
from online_market.views import *
from online_market import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("register/", views.register, name="register"),
    path("", views.home, name="home"),
    path("confirm-email/<uidb64>/<token>/", views.confirm_email, name="confirm_email"),
    path('login/', views.login_view, name='login'),
    path('bike/', views.order_bike, name='bike'),
]
