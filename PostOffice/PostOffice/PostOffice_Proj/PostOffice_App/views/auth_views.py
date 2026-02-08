# ==========================================================
#  AUTH VIEWS (login / register / logout)
# ==========================================================
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            # Guardamos el rol en sesión (clave para los templates)
            request.session["role"] = getattr(user, "role", None)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "auth/login.html")


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm()

    return render(request, "auth/register.html", {"form": form})


def logout_view(request):
    auth_logout(request)
    request.session.flush()
    return redirect("login")
