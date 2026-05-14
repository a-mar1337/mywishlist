from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import EmailLoginForm, ProfileForm, RegisterForm
import logging

logger = logging.getLogger(__name__)
def register_view(request):
    if request.user.is_authenticated:
        return redirect("wishlists:dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            logger.info("New user registered: %s", user.email)
            login(request, user)
            messages.success(request, "Регистрация прошла успешно.")
            return redirect("wishlists:dashboard")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("wishlists:dashboard")

    if request.method == "POST":
        form = EmailLoginForm(request.POST)

        if form.is_valid():
            user = form.cleaned_data["user"]
            logger.info("User logged in: %s", user.email)
            login(request, user)
            messages.success(request, "Вы успешно вошли в аккаунт.")
            return redirect("wishlists:dashboard")
        else:
            logger.warning("Failed login attempt")
    else:
        form = EmailLoginForm()

    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request):
    if request.method == "POST":
        logger.info("User logged out: %s", request.user.email)
        logout(request)
        messages.success(request, "Вы вышли из аккаунта.")
        return redirect("home")

    return redirect("wishlists:dashboard")


@login_required
def profile_view(request):
    profile = request.user.profile

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)

        if form.is_valid():
            form.save()
            logger.info("Profile updated: %s", request.user.email)
            messages.success(request, "Профиль обновлён.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "accounts/profile.html", {"form": form})