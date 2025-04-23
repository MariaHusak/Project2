from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from .user_service import create_user_and_log, login_user_via_facade
from .bike_service import build_bike, create_bike_order, log_bike_order
from .user_service import confirm_user_email_by_token


def home(request):
    return render(request, "home.html")


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = create_user_and_log(form)
            confirm_user_email_by_token(user)
            return render(request, "login.html")
        return render(request, "register.html", {"form": form})

    form = CustomUserCreationForm()
    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        try:
            user = login_user_via_facade(email, password)
            if user.is_verified:
                login(request, user)
                return redirect("bike")
            return render(request, "login.html", {"error": "Будь ласка, підтвердіть вашу електронну пошту."})
        except ValueError:
            return render(request, "login.html", {"error": "Невірні облікові дані."})

    return render(request, "login.html")


def order_bike(request):
    bike_type = request.GET.get("type", "regular")
    bike = build_bike(bike_type)
    bike_order = create_bike_order(bike_type, bike)

    user = request.user
    user.bike_orders.add(bike_order)
    user.save()

    log_bike_order(user, bike_type, bike)

    return render(request, "bike.html", {
        "bike": str(bike),
        "bike_order": bike_order
    })


def confirm_email(request, uidb64, token):
    user = confirm_user_email_by_token(uidb64, token)
    if user:
        return redirect("login")
    return render(request, "invalid_token.html")
