from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect("dashboard")
    else:
        form = AuthenticationForm()
    return render(request, "auth/login.html", {"form": form})


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "auth/register.html", {"form": form})
#

# @login_required - disable this now so it doesn't block pages without log in

def dashboard(request):
    return render(request, "dashboard/admin.html")


# @login_required - disable this now so it doesn't block pages without log in

def warehouses_list(request):
    return render(request, "warehouses/list.html")


# @login_required - disable this now so it doesn't block pages without log in

def vehicles_list(request):
    return render(request, "vehicles/list.html")


# @login_required - disable this now so it doesn't block pages without log in

def mail_list(request):
    return render(request, "mail/list.html")


# @login_required - disable this now so it doesn't block pages without log in

def mail_detail(request):
    return render(request, "mail/detail.html")


# @login_required - disable this now so it doesn't block pages without log in

def deliveries_list(request):
    return render(request, "deliveries/list.html")


# @login_required - disable this now so it doesn't block pages without log in

def invoices_list(request):
    return render(request, "invoices/list.html")


# @login_required - disable this now so it doesn't block pages without log in
def client_profile(request):
    return render(request, "clients/profile.html")
