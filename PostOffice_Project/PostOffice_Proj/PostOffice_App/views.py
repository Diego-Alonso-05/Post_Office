from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from pymongo import MongoClient
from datetime import datetime
from django import forms

client = MongoClient("mongodb://localhost:27017")
db = client["bdII_14366"]  # ← o nome da tua base de dados
deliveries = db["deliveries"]
notifications = db["notifications"]
routes = db["routes"]
users = db["users"]
postoffice = db["postoffice"]
vehicles = db["vehicles"]

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

# Pages
def dashboard(request):
    return render(request, "dashboard/admin.html")

def warehouses_list(request):
    return render(request, "warehouses/list.html")

def vehicles_list(request):
    return render(request, "vehicles/list.html")

def mail_list(request):
    return render(request, "mail/list.html")

def mail_detail(request, mail_id):
    return render(request, "mail/detail.html", {"mail_id": mail_id})

def deliveries_list(request):
    return render(request, "deliveries/list.html")

def client_profile(request):
    return render(request, "clients/profile.html")

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
