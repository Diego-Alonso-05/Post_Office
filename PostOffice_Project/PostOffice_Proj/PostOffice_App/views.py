from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from pymongo import MongoClient
from datetime import datetime
from django import forms
from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from django.shortcuts import redirect
from django.contrib.auth import logout

client = MongoClient("mongodb://localhost:27017")
db = client["PostOffice_Proj_MDB"]  # ← o nome da tua base de dados
deliveries = db["deliveries"]
notifications = db["notifications"]
routes = db["routes"]
users = db["users"]
postoffice = db["postoffice"]
vehicles = db["vehicles"]


def role_required(allowed_roles):
    """Decorator to restrict view access by user role."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # fetch the user's role from MongoDB
            user_doc = users.find_one({"username": request.user.username})
            if not user_doc or user_doc.get("role") not in allowed_roles:
                return HttpResponseForbidden("You do not have permission to view this page.")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

from django.contrib.auth import authenticate, login as auth_login

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)

            # fetch role from MongoDB
            mongo_user = users.find_one({"username": username})
            if mongo_user:
                request.session["role"] = mongo_user.get("role", "client")  # default to client

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

# Pages


@login_required
def dashboard(request):
    user_doc = users.find_one({"username": request.user.username})
    role = user_doc.get("role")

    if role == "admin":
        stats = {
            "total_vehicles": vehicles.count_documents({}),
            "total_deliveries": deliveries.count_documents({}),
            "total_clients": users.count_documents({"role":"client"})
        }
    elif role == "driver":
        stats = {
            "my_deliveries": list(deliveries.find({"driver_id": user_doc["_id"]}))
        }
    else:  # client
        stats = {
            "my_deliveries": list(deliveries.find({"client_id": user_doc["_id"]}))
        }

    return render(request, "dashboard/admin.html", {"stats": stats, "role": role})

def warehouses_list(request):
    return render(request, "warehouses/list.html")

def logout_view(request):
    logout(request)
    request.session.flush()  # clears role from session
    return redirect("login")


@login_required
@role_required(["admin"])
def vehicles_list(request):
    all_vehicles = list(vehicles.find())
    return render(request, "vehicles/list.html", {"vehicles": all_vehicles})

def mail_list(request):
    return render(request, "mail/list.html")

def mail_detail(request, mail_id):
    return render(request, "mail/detail.html", {"mail_id": mail_id})

@login_required
@role_required(["driver", "admin"])
def deliveries_list(request):
    user_doc = users.find_one({"username": request.user.username})
    if user_doc["role"] == "driver":
        all_deliveries = list(deliveries.find({"driver_id": user_doc["_id"]}))
    else:
        all_deliveries = list(deliveries.find())
    return render(request, "deliveries/list.html", {"deliveries": all_deliveries})

@login_required
@role_required(["client", "admin"])
def client_profile(request):
    user_doc = users.find_one({"username": request.user.username})
    my_deliveries = list(deliveries.find({"client_id": user_doc["_id"]}))
    return render(request, "clients/profile.html", {"deliveries": my_deliveries, "user": user_doc})

class VehicleForm(forms.Form):
    plate_number = forms.CharField(max_length=10, label="Plate Number")
    model = forms.CharField(max_length=50)
    assigned_driver = forms.CharField(max_length=50, required=False)
    status = forms.ChoiceField(choices=[('active', 'Active'), ('inactive', 'Inactive')])

def vehicles_create(request):
    if request.method == "POST":
        form = VehicleForm(request.POST)
        if form.is_valid():
            # save to your MongoDB collection, example:
            vehicles.insert_one(form.cleaned_data)
            return redirect('vehicles_list')
    else:
        form = VehicleForm()
    return render(request, 'vehicles/create.html', {'form': form})

def vehicles_edit(request, vehicle_id):
    # find the vehicle in MongoDB
    vehicle = vehicles.find_one({"_id": vehicle_id})
    if not vehicle:
        return redirect("vehicles_list")  # fallback if not found

    if request.method == "POST":
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicles.update_one(
                {"_id": vehicle_id},
                {"$set": form.cleaned_data}
            )
            return redirect("vehicles_list")
    else:
        # populate form with existing vehicle data
        form = VehicleForm(initial=vehicle)

    return render(request, "vehicles/edit.html", {"form": form, "vehicle_id": vehicle_id})
