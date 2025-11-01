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
from bson.objectid import ObjectId
from bson.errors import InvalidId


client = MongoClient("mongodb://localhost:27017")
db = client["postoffice"]  # ← o nome da tua base de dados
deliveries = db["deliveries"]
notifications = db["notifications"]
routes_collection = db["routes"]
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

class WarehouseForm(forms.Form):
    name = forms.CharField(label="Warehouse Name", max_length=100)
    address = forms.CharField(label="Address", max_length=200)
    contact = forms.CharField(label="Contact", max_length=50)
    po_schedule_open = forms.TimeField(label="Opening Time", widget=forms.TimeInput(format="%H:%M"))
    po_schedule_close = forms.TimeField(label="Closing Time", widget=forms.TimeInput(format="%H:%M"))
    maximum_storage_capacity = forms.IntegerField(label="Max Storage Capacity")

# Views
@login_required
@role_required(["admin"])
def warehouses_list(request):
    all_warehouses = list(postoffice.find())
    for w in all_warehouses:
        w['id'] = str(w['_id'])
    return render(request, "warehouses/list.html", {"warehouses": all_warehouses})

@login_required
@role_required(["admin"])
def warehouses_create(request):
    if request.method == "POST":
        form = WarehouseForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data.copy()

            # Rename to match your new DB schema
            data["po_schedule_open"] = data["po_schedule_open"].strftime("%H:%M")
            data["po_schedule_close"] = data["po_schedule_close"].strftime("%H:%M")

            # Remove old keys if they exist (safety)
            data.pop("opening_time", None)
            data.pop("closing_time", None)

            # Generate numeric _id manually (since not using ObjectId)
            last = postoffice.find_one(sort=[("_id", -1)])
            data["_id"] = (last["_id"] + 1) if last else 3001

            postoffice.insert_one(data)
            return redirect("warehouses_list")
    else:
        form = WarehouseForm()

    return render(request, "warehouses/create.html", {"form": form})

@login_required
@role_required(["admin", "staff"] )
def warehouses_edit(request, warehouse_id):
    # Convert to integer for querying
    try:
        warehouse_id = int(warehouse_id)
    except ValueError:
        return HttpResponseBadRequest("Invalid warehouse ID")

    warehouse = postoffice.find_one({"_id": warehouse_id})
    if not warehouse:
        return redirect("warehouses_list")

    if request.method == "POST":
        form = WarehouseForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data.copy()
            data["po_schedule_open"] = data["po_schedule_open"].strftime("%H:%M")
            data["po_schedule_close"] = data["po_schedule_close"].strftime("%H:%M")

            postoffice.update_one({"_id": warehouse_id}, {"$set": data})
            messages.success(request, "Warehouse updated successfully.")
            return redirect("warehouses_list")
    else:
        # Convert stored times back to time objects for form display
        if "po_schedule_open" in warehouse:
            warehouse["po_schedule_open"] = datetime.strptime(warehouse["po_schedule_open"], "%H:%M").time()
        if "po_schedule_close" in warehouse:
            warehouse["po_schedule_close"] = datetime.strptime(warehouse["po_schedule_close"], "%H:%M").time()

        form = WarehouseForm(initial=warehouse)

    return render(request, "warehouses/edit.html", {
        "form": form,
        "warehouse_id": warehouse_id
    })

@login_required
@role_required(["admin"])
def warehouses_delete(request, warehouse_id):
    postoffice.delete_one({"_id": ObjectId(warehouse_id)})
    return redirect("warehouses_list")



def logout_view(request):
    logout(request)
    request.session.flush()  # clears role from session
    return redirect("login")

class VehicleForm(forms.Form):
    vehicle_type = forms.CharField(max_length=100)
    plate_number = forms.CharField(max_length=20)
    capacity = forms.FloatField()
    brand = forms.CharField(max_length=100)
    model = forms.CharField(max_length=100)
    vehicle_status = forms.CharField(max_length=50)
    year = forms.IntegerField()
    fuel_type = forms.CharField(max_length=50)
    last_maintenance_date = forms.DateField()

@login_required
@role_required(["Admin", "Manager"])
def vehicles_create(request):
    if request.method == "POST":
        form = VehicleForm(request.POST)
        if form.is_valid():
            # Generate next ID manually (since Mongo int IDs aren’t auto)
            last_vehicle = vehicles.find_one(sort=[("_id", -1)])
            next_id = (last_vehicle["_id"] + 1) if last_vehicle else 4001

            data = form.cleaned_data
            data["_id"] = next_id
            vehicles.insert_one(data)
            return redirect("vehicles_list")
    else:
        form = VehicleForm()

    return render(request, "vehicles/create.html", {"form": form})


@login_required
@role_required(["admin"])
def vehicles_list(request):
    all_vehicles = list(vehicles.find())

    cleaned_vehicles = []
    for v in all_vehicles:
        _id = v.get("_id")
        if _id:  # only add if ID exists
            v["id"] = str(_id)
            cleaned_vehicles.append(v)

    return render(request, "vehicles/list.html", {"vehicles": cleaned_vehicles})

@login_required
def routes_list(request):
    routes = list(routes_collection.find())
    # Convert _id (int or ObjectId) for easier use in templates
    for r in routes:
        r["id"] = r.get("_id")
    context = {"routes": routes}
    return render(request, "routes/list.html", context)

@login_required
@role_required(["Admin"])
@login_required
def vehicles_edit(request, vehicle_id):
    # vehicle_id is an int, not ObjectId
    vehicle = vehicles.find_one({"_id": int(vehicle_id)})

    if not vehicle:
        return HttpResponseNotFound("Vehicle not found")

    if request.method == "POST":
        updated_data = {
            "vehicle_type": request.POST.get("vehicle_type"),
            "plate_number": request.POST.get("plate_number"),
            "capacity": float(request.POST.get("capacity")),
            "brand": request.POST.get("brand"),
            "model": request.POST.get("model"),
            "vehicle_status": request.POST.get("vehicle_status"),
            "year": int(request.POST.get("year")),
            "fuel_type": request.POST.get("fuel_type"),
            "last_maintenance_date": request.POST.get("last_maintenance_date"),
        }
        vehicles.update_one({"_id": int(vehicle_id)}, {"$set": updated_data})
        return redirect("vehicles_list")

    return render(request, "vehicles_edit.html", {"vehicle": vehicle})



def mail_list(request):
    return render(request, "mail/list.html")

def mail_detail(request, mail_id):
    return render(request, "mail/detail.html", {"mail_id": mail_id})

@login_required
@role_required(["driver", "admin", "client"])
def deliveries_list(request):
    deliveries_data = list(deliveries.find())
    deliveries_list = []

    for d in deliveries_data:
        # Rename MongoDB _id → id (safe for templates)
        d["id"] = int(d["_id"])  # keep numeric if needed
        deliveries_list.append(d)

    context = {"deliveries": deliveries_list}
    return render(request, "deliveries/list.html", context)

@login_required
def deliveries_detail(request, delivery_id):
    delivery = deliveries.find_one({"_id": int(delivery_id)})
    if not delivery:
        return HttpResponseNotFound("Delivery not found.")
    return render(request, "deliveries/detail.html", {"delivery": delivery})


@login_required
def deliveries_create(request):
    """Create a new delivery"""
    if request.method == "POST":
        data = {
            "recipient": request.POST.get("recipient"),
            "address": request.POST.get("address"),
            "status": request.POST.get("status", "Pending"),
        }
        deliveries.insert_one(data)
        return redirect("deliveries_list")

    return render(request, "deliveries/create.html")

@login_required
@login_required
def deliveries_edit(request, delivery_id):
    deliveries_collection = db["deliveries"]
    delivery = deliveries_collection.find_one({"_id": delivery_id})

    if not delivery:
        return render(request, "404.html", status=404)

    if request.method == "POST":
        # Example — update fields based on your form
        updated_data = {
            "status": request.POST.get("status"),
            "destination": request.POST.get("destination"),
            "delivery_date": request.POST.get("delivery_date"),
            # Add other fields you want to allow editing
        }
        deliveries_collection.update_one({"_id": delivery_id}, {"$set": updated_data})
        return redirect("deliveries_list")

    context = {"delivery": delivery}
    return render(request, "deliveries/edit.html", context)

@login_required
def deliveries_delete(request, delivery_id):
    """Delete an existing delivery."""
    delivery = deliveries.find_one({"_id": ObjectId(delivery_id)})
    if not delivery:
        return HttpResponseNotFound("Delivery not found.")

    deliveries.delete_one({"_id": ObjectId(delivery_id)})
    return redirect("deliveries_list")

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
