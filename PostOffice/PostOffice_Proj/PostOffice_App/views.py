from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import (
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponseBadRequest,
)
from django.shortcuts import render, redirect, get_object_or_404
from datetime import time

from pymongo import MongoClient  # kept ONLY for notifications

from .models import (
    User,
    Employee,
    Warehouse,
    Vehicle,
    Invoice,
    Route,
    Delivery,
)
from .forms import (
    CustomUserCreationForm,
    CustomUserChangeForm,
    EmployeeForm,
    EmployeeDriverForm,
    EmployeeStaffForm,
    WarehouseForm,
    VehicleForm,
    InvoiceForm,
    RouteForm,
    DeliveryForm,
    VehicleImportForm,  
    WarehouseImportForm,
    DeliveryImportForm,
    RouteImportForm, 
)


# ==========================================================
#  MONGO: NOTIFICATIONS ONLY
# ==========================================================

mongo_client = MongoClient("mongodb://localhost:27017")
mongo_db = mongo_client["postoffice"]
notifications_collection = mongo_db["notifications"]  # still in MongoDB

# Helper to record notifications in MongoDB.
# Wrap insertion in a simple function to allow optional use later
def create_notification(notification_type, recipient_contact, subject, message, status="pending"):
    """Insert a notification document into MongoDB.

    Parameters
    ----------
    notification_type : str
        A short tag describing the notification purpose.
    recipient_contact : str
        Contact details for the recipient (email/phone).
    subject : str
        Subject line or title for the notification.
    message : str
        Full notification body.
    status : str, optional
        Initial status of the notification, defaulting to ``pending``.
    """
    try:
        notifications_collection.insert_one(
            {
                "notification_type": notification_type,
                "recipient_contact": recipient_contact,
                "subject": subject,
                "message": message,
                "status": status,
                "created_at": timezone.now(),
            }
        )
    except Exception:
        # Swallow Mongo exceptions to avoid impacting main flow
        pass


# ==========================================================
#  ROLE-BASED ACCESS DECORATOR
# ==========================================================

def role_required(allowed_roles):
    """
    Restrict access to users whose User.role is in allowed_roles.
    Example: @login_required @role_required(["admin", "client"])
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("login")

            if request.user.role not in allowed_roles:
                return HttpResponseForbidden("You do not have permission to view this page.")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ==========================================================
#  AUTH VIEWS (login / register / logout)
# ==========================================================

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            # role is stored on User model now; no need to fetch from Mongo
            request.session["role"] = user.role
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "auth/login.html")


def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = CustomUserCreationForm()
    return render(request, "auth/register.html", {"form": form})


def logout_view(request):
    auth_logout(request)
    request.session.flush()
    return redirect("login")


# ==========================================================
#  DASHBOARD
# ==========================================================

@login_required
def dashboard(request):
    role = request.user.role

    if role == "admin":
        # Provide a richer overview for administrators.  Include employees,
        # invoices and route/delivery breakdowns.  Completed and cancelled routes
        # are excluded from the active count.
        stats = {
            "total_vehicles": Vehicle.objects.count(),
            "total_deliveries": Delivery.objects.count(),
            "total_clients": User.objects.filter(role="client").count(),
            "total_employees": Employee.objects.count(),
            "active_routes": Route.objects.exclude(delivery_status__in=["Completed", "Cancelled"]).count(),
            "pending_deliveries": Delivery.objects.filter(status="Pending").count(),
            "total_invoices": Invoice.objects.count(),
        }
    elif role == "driver":
        employee = getattr(request.user, "employee", None)
        if employee:
            my_deliveries = Delivery.objects.filter(driver=employee)
        else:
            my_deliveries = Delivery.objects.none()
        stats = {
            "my_deliveries": my_deliveries,
        }
    else:  # client, staff, manager etc. -> show client deliveries
        stats = {
            "my_deliveries": Delivery.objects.filter(client=request.user),
        }

    return render(request, "dashboard/admin.html", {"stats": stats, "role": role})


# ==========================================================
#  HOME (from views1.py)
# ==========================================================

def home(request):
    return render(request, "core/home.html")


# ==========================================================
#  USER & CLIENT MANAGEMENT (in spirit of views1.py)
# ==========================================================

@login_required
@role_required(["admin"])
def users_list(request):
    users = User.objects.all().order_by("username")
    paginator = Paginator(users, 10)
    page_number = request.GET.get("page")
    users_page = paginator.get_page(page_number)
    return render(request, "core/users_list.html", {"users": users_page})


@login_required
@role_required(["admin"])
def users_form(request, user_id=None):
    if user_id:
        user = get_object_or_404(User, pk=user_id)
        FormClass = CustomUserChangeForm
    else:
        user = None
        FormClass = CustomUserCreationForm

    if request.method == "POST":
        form = FormClass(request.POST, instance=user)
        if form.is_valid():
            saved_user = form.save()
            # if creating, we might want a default role; leave as chosen in form
            return redirect("users_list")
    else:
        form = FormClass(instance=user)

    return render(request, "core/users_form.html", {"form": form})


@login_required
@role_required(["admin"])
def clients_list(request):
    clients_qs = User.objects.filter(role="client").order_by("username")
    paginator = Paginator(clients_qs, 10)
    page_number = request.GET.get("page")
    clients_page = paginator.get_page(page_number)
    return render(request, "core/clients.html", {"clients": clients_page})


@login_required
@role_required(["admin"])
def clients_form(request, user_id=None):
    if user_id:
        user = get_object_or_404(User, pk=user_id, role="client")
        FormClass = CustomUserChangeForm
    else:
        user = None
        FormClass = CustomUserCreationForm

    if request.method == "POST":
        form = FormClass(request.POST, instance=user)
        if form.is_valid():
            client = form.save(commit=False)
            client.role = "client"
            client.save()
            return redirect("clients_list")
    else:
        form = FormClass(instance=user)

    return render(request, "core/clients_form.html", {"form": form})


# ==========================================================
#  EMPLOYEES (list only; CRUD can be done in admin for now)
#  Keeps spirit of views1.py but adapted to new models
# ==========================================================

@login_required
@role_required(["admin"])
def employees_list(request):
    employees_qs = Employee.objects.select_related("user").all()
    paginator = Paginator(employees_qs, 10)
    page_number = request.GET.get("page")
    employees_page = paginator.get_page(page_number)
    return render(request, "core/employees_list.html", {"employees": employees_page})


@login_required
@role_required(["admin"])
def employees_form(request, employee_id=None):
    """
    Basic employee + driver/staff creation/edit.
    Assumes the User already exists and is linked.
    For simplicity, expect a 'user_id' hidden/choice field in the template.
    """
    if employee_id:
        employee = get_object_or_404(Employee, pk=employee_id)
    else:
        employee = None

    if request.method == "POST":
        # Expect a user_id in POST to attach this employee to a User.  Validate
        # both existence and role suitability.  Only non-client and non-admin
        # users may be converted into employees.  For edits, ensure the
        # provided user matches the current employee.
        user_id = request.POST.get("user_id")
        if not user_id:
            return HttpResponseBadRequest("Missing user selection for employee.")
        user = get_object_or_404(User, pk=user_id)
        # Reject attempts to tie an employee to a user with an unsuitable role
        if employee is None and user.role in {"admin", "client"}:
            return HttpResponseBadRequest("Selected user cannot become an employee.")
        # Prevent multiple Employee records for the same user
        if employee is None and hasattr(user, "employee"):
            return HttpResponseBadRequest("User is already assigned to an employee record.")
        # If editing, ensure the provided user matches the existing record
        if employee is not None and employee.user_id != user.pk:
            return HttpResponseBadRequest("User mismatch: cannot reassign existing employee to a different user.")

        # Create new Employee instance if necessary
        if employee is None:
            employee = Employee(user=user)

        # Keep track of the original position in case it changes
        old_position = employee.position if employee.pk else None
        emp_form = EmployeeForm(request.POST, instance=employee)

        # Decide which specialized form to use based on requested position
        position = request.POST.get("position")
        driver_form = staff_form = None
        if position == "Driver":
            driver_info = getattr(employee, "driver_info", None)
            driver_form = EmployeeDriverForm(request.POST, instance=driver_info)
        elif position == "Staff":
            staff_info = getattr(employee, "staff_info", None)
            staff_form = EmployeeStaffForm(request.POST, instance=staff_info)

        # Validate base and specialized forms
        forms_valid = emp_form.is_valid()
        if driver_form:
            forms_valid = forms_valid and driver_form.is_valid()
        if staff_form:
            forms_valid = forms_valid and staff_form.is_valid()

        if forms_valid:
            # Save the base employee record
            saved_employee = emp_form.save()

            # If the role changed between driver and staff, clean up the old
            # specialized record to avoid orphans
            if old_position and old_position != position:
                try:
                    if old_position == "Driver" and hasattr(saved_employee, "driver_info"):
                        saved_employee.driver_info.delete()
                    if old_position == "Staff" and hasattr(saved_employee, "staff_info"):
                        saved_employee.staff_info.delete()
                except Exception:
                    pass

            if position == "Driver" and driver_form:
                driver_model = driver_form.save(commit=False)
                driver_model.employee = saved_employee
                driver_model.save()
                # synchronize the associated user role
                saved_employee.user.role = "driver"
                saved_employee.user.save(update_fields=["role"])
            elif position == "Staff" and staff_form:
                staff_model = staff_form.save(commit=False)
                staff_model.employee = saved_employee
                staff_model.save()
                saved_employee.user.role = "staff"
                saved_employee.user.save(update_fields=["role"])

            return redirect("employees_list")
    else:
        # For GET requests, provide initial forms.  Pre-populate specialized
        # forms if they exist on the employee instance.
        emp_form = EmployeeForm(instance=employee)
        driver_info = getattr(employee, "driver_info", None) if employee else None
        staff_info = getattr(employee, "staff_info", None) if employee else None

        driver_form = EmployeeDriverForm(instance=driver_info) if driver_info else EmployeeDriverForm()
        staff_form = EmployeeStaffForm(instance=staff_info) if staff_info else EmployeeStaffForm()

    return render(
        request,
        "core/employees_form.html",
        {
            "employee_form": emp_form,
            "driver_form": driver_form,
            "staff_form": staff_form,
            "employee": employee,
        },
    )


# ==========================================================
#  INVOICES
# ==========================================================

@login_required
@role_required(["admin", "client"])
def invoice_list(request):
    if request.user.role == "client":
        invoices_qs = Invoice.objects.filter(user=request.user).order_by("-invoice_datetime")
    else:
        invoices_qs = Invoice.objects.select_related("user").all().order_by("-invoice_datetime")
    paginator = Paginator(invoices_qs, 10)
    page_number = request.GET.get("page")
    invoices_page = paginator.get_page(page_number)
    return render(request, "invoices/invoice.html", {"transactions": invoices_page})


@login_required
@role_required(["admin"])
def invoice_form(request, invoice_id=None):
    if invoice_id:
        invoice = get_object_or_404(Invoice, pk=invoice_id)
    else:
        invoice = None

    if request.method == "POST":
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            invoice_obj = form.save()
            # Notify the user associated with the invoice, if any
            if invoice_obj.user and invoice_obj.user.contact:
                create_notification(
                    notification_type="invoice_updated" if invoice_id else "invoice_created",
                    recipient_contact=invoice_obj.user.contact,
                    subject="Invoice notification",
                    message=f"Invoice {invoice_obj.id_invoice} has been {'updated' if invoice_id else 'created'}.",
                )
            return redirect("invoice_list")
    else:
        form = InvoiceForm(instance=invoice)

    return render(request, "invoices/invoice_form.html", {"form": form})


# ==========================================================
#  WAREHOUSES (SQL instead of Mongo)
# ==========================================================

@login_required
@role_required(["admin"])
def warehouses_list(request):
    warehouses_qs = Warehouse.objects.all()
    paginator = Paginator(warehouses_qs, 10)
    page_number = request.GET.get("page")
    warehouses_page = paginator.get_page(page_number)
    return render(request, "warehouses/list.html", {"warehouses": warehouses_page})


@login_required
@role_required(["admin"])
def warehouses_create(request):
    if request.method == "POST":
        form = WarehouseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("warehouses_list")
    else:
        form = WarehouseForm()

    return render(request, "warehouses/create.html", {"form": form})


@login_required
@role_required(["admin", "staff"])
def warehouses_edit(request, warehouse_id):
    warehouse = get_object_or_404(Warehouse, pk=warehouse_id)

    if request.method == "POST":
        form = WarehouseForm(request.POST, instance=warehouse)
        if form.is_valid():
            form.save()
            messages.success(request, "Warehouse updated successfully.")
            return redirect("warehouses_list")
    else:
        form = WarehouseForm(instance=warehouse)

    return render(
        request,
        "warehouses/edit.html",
        {"form": form, "warehouse_id": warehouse_id},
    )


@login_required
@role_required(["admin"])
def warehouses_delete(request, warehouse_id):
    """Delete a warehouse.  Requires a POST request to prevent CSRF via GET.

    If a non-POST request is received, a 400 response is returned.  A
    confirmation template could be implemented separately if desired.
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method for deletion.")
    warehouse = get_object_or_404(Warehouse, pk=warehouse_id)
    try:
        warehouse.delete()
        messages.success(request, "Warehouse deleted successfully.")
    except Exception:
        messages.error(request, "An error occurred while deleting the warehouse.")
    return redirect("warehouses_list")


# ==========================================================
#  VEHICLES (SQL instead of Mongo)
# ==========================================================

@login_required
@role_required(["admin", "manager"])
def vehicles_create(request):
    if request.method == "POST":
        form = VehicleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("vehicles_list")
    else:
        form = VehicleForm()

    return render(request, "vehicles/create.html", {"form": form})


@login_required
@role_required(["admin", "manager", "staff"])
def vehicles_list(request):
    vehicles_qs = Vehicle.objects.all()
    paginator = Paginator(vehicles_qs, 10)
    page_number = request.GET.get("page")
    vehicles_page = paginator.get_page(page_number)
    # templates can use vehicle.id directly
    return render(request, "vehicles/list.html", {"vehicles": vehicles_page})


@login_required
@role_required(["admin", "manager"])
def vehicles_edit(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id)

    if request.method == "POST":
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            return redirect("vehicles_list")
    else:
        form = VehicleForm(instance=vehicle)

    return render(
        request,
        "vehicles/edit.html",
        {"vehicle": vehicle, "vehicle_id": vehicle_id, "form": form},
    )


@login_required
@role_required(["admin"])
def vehicles_delete(request, vehicle_id):
    """Delete a vehicle.  Must be invoked via POST for CSRF safety."""
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method for deletion.")
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
    try:
        vehicle.delete()
        messages.success(request, "Vehicle deleted successfully.")
    except Exception:
        messages.error(request, "An error occurred while deleting the vehicle.")
    return redirect("vehicles_list")


# ==========================================================
#  ROUTES (SQL instead of Mongo)
# ==========================================================

@login_required
def routes_list(request):
    routes_qs = Route.objects.select_related("driver", "vehicle").all()
    paginator = Paginator(routes_qs, 10)
    page_number = request.GET.get("page")
    routes_page = paginator.get_page(page_number)
    return render(request, "routes/list.html", {"routes": routes_page})


@login_required
@role_required(["admin"])
def routes_create(request):
    if request.method == "POST":
        form = RouteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("routes_list")
    else:
        form = RouteForm()

    return render(request, "routes/create.html", {"form": form})


@login_required
@role_required(["admin"])
def routes_edit(request, route_id):
    route = get_object_or_404(Route, pk=route_id)

    if request.method == "POST":
        form = RouteForm(request.POST, instance=route)
        if form.is_valid():
            form.save()
            return redirect("routes_list")
    else:
        form = RouteForm(instance=route)

    return render(request, "routes/edit.html", {"form": form, "route": route})


@login_required
@role_required(["admin"])
def routes_delete(request, route_id):
    """Delete a route.  Requires a POST request to avoid accidental deletion."""
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method for deletion.")
    route = get_object_or_404(Route, pk=route_id)
    try:
        route.delete()
        messages.success(request, "Route deleted successfully.")
    except Exception:
        messages.error(request, "An error occurred while deleting the route.")
    return redirect("routes_list")


# ==========================================================
#  DELIVERIES (SQL instead of Mongo)
# ==========================================================

@login_required
@role_required(["driver", "admin", "client", "staff", "manager"])
def deliveries_list(request):
    role = request.user.role
    # Determine the base queryset according to role
    if role in {"admin", "manager", "staff"}:
        deliveries_qs = Delivery.objects.select_related("driver", "client", "route").all()
    elif role == "driver":
        employee = getattr(request.user, "employee", None)
        deliveries_qs = Delivery.objects.filter(driver=employee) if employee else Delivery.objects.none()
    else:  # client
        deliveries_qs = Delivery.objects.filter(client=request.user)
    # Paginate the deliveries so that long lists do not overload the page
    paginator = Paginator(deliveries_qs, 10)
    page_number = request.GET.get("page")
    deliveries_page = paginator.get_page(page_number)
    return render(request, "deliveries/list.html", {"deliveries": deliveries_page})


@login_required
def deliveries_detail(request, delivery_id):
    delivery = get_object_or_404(Delivery, pk=delivery_id)
    return render(request, "deliveries/detail.html", {"delivery": delivery})


@login_required
@role_required(["admin", "staff"])
def deliveries_create(request):
    if request.method == "POST":
        form = DeliveryForm(request.POST)
        if form.is_valid():
            new_delivery = form.save()
            # Optionally send a notification to the client about the new delivery
            recipient = None
            # Prefer the linked client contact if available
            if new_delivery.client and new_delivery.client.contact:
                recipient = new_delivery.client.contact
            elif new_delivery.recipient_email:
                recipient = new_delivery.recipient_email
            if recipient:
                create_notification(
                    notification_type="delivery_created",
                    recipient_contact=recipient,
                    subject="New delivery registered",
                    message=f"Delivery {new_delivery.tracking_number} has been registered.",
                )
            return redirect("deliveries_list")
    else:
        form = DeliveryForm()

    return render(request, "deliveries/create.html", {"form": form})


@login_required
@role_required(["admin", "staff"])
def deliveries_edit(request, delivery_id):
    delivery = get_object_or_404(Delivery, pk=delivery_id)

    if request.method == "POST":
        form = DeliveryForm(request.POST, instance=delivery)
        if form.is_valid():
            form.save()
            return redirect("deliveries_list")
    else:
        form = DeliveryForm(instance=delivery)

    return render(request, "deliveries/edit.html", {"form": form, "delivery": delivery})


@login_required
@role_required(["admin"])
def deliveries_delete(request, delivery_id):
    """Delete a delivery.  Only accepts POST requests to mitigate CSRF."""
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method for deletion.")
    delivery = get_object_or_404(Delivery, pk=delivery_id)
    try:
        delivery.delete()
        messages.success(request, "Delivery deleted successfully.")
    except Exception:
        messages.error(request, "An error occurred while deleting the delivery.")
    return redirect("deliveries_list")


# ==========================================================
#  CLIENT PROFILE (based on role, uses SQL instead of Mongo)
# ==========================================================

@login_required
@role_required(["client", "admin"])
def client_profile(request):
    if request.user.role == "client":
        my_deliveries = Delivery.objects.filter(client=request.user)
        user_obj = request.user
    else:
        # admin sees nothing special here unless extended with query param
        my_deliveries = Delivery.objects.none()
        user_obj = request.user

    return render(
        request,
        "clients/profile.html",
        {"deliveries": my_deliveries, "user": user_obj},
    )


# ==========================================================
#  SIMPLE MAIL PAGES (static / placeholder)
# ==========================================================

def mail_list(request):
    return render(request, "mail/list.html")


def mail_detail(request, mail_id):
    return render(request, "mail/detail.html", {"mail_id": mail_id})




# ==========================================================
#  VEHICLES EXPORT (DOWNLOAD JSON FILE)
# ==========================================================

import json
from django.http import HttpResponse
from django.db import connection

@login_required
@role_required(["admin", "manager", "staff"])
def vehicles_export_json(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT exportar_vehicles();")
        data = cursor.fetchone()[0]

    # Convertir en JSON bonito (indentado)
    json_data = json.dumps(data, indent=4)

    # Preparar archivo descargable
    response = HttpResponse(json_data, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="vehicles_export.json"'

    return response


# ==========================================================
#  VEHICLES IMPORT (UPLOAD JSON FILE)
# ==========================================================

import json
from django.contrib import messages

@login_required
@role_required(["admin", "manager"])
def vehicles_import_json(request):
    if request.method == "POST":
        form = VehicleImportForm(request.POST, request.FILES)

        if form.is_valid():
            file = request.FILES["file"]

            try:
                data = json.load(file)
            except Exception:
                messages.error(request, "Invalid JSON file.")
                return redirect("vehicles_import_json")

            # Validate JSON is a list
            if not isinstance(data, list):
                messages.error(request, "JSON must contain a list of vehicles.")
                return redirect("vehicles_import_json")

            count = 0

            for item in data:
                # Prevent KeyError and skip invalid objects
                if not isinstance(item, dict):
                    continue

                Vehicle.objects.create(
                    vehicle_type=item.get("vehicle_type"),
                    plate_number=item.get("plate_number"),
                    capacity=item.get("capacity"),
                    brand=item.get("brand"),
                    model=item.get("model"),
                    vehicle_status=item.get("vehicle_status"),
                    year=item.get("year"),
                    fuel_type=item.get("fuel_type"),
                    last_maintenance_date=item.get("last_maintenance_date"),
                )
                count += 1

            messages.success(request, f"Imported {count} vehicles successfully.")
            return redirect("vehicles_list")

    else:
        form = VehicleImportForm()

    return render(request, "vehicles/import.html", {"form": form})



@login_required
@role_required(["admin", "manager"])
def warehouses_export_json(request):
    warehouses = Warehouse.objects.all().values()

    cleaned_warehouses = []
    time_fields = [
        "po_schedule_open",
        "po_schedule_close",
        "deliver_schedule_open",
        "deliver_schedule_close",
    ]

    for w in warehouses:
        w = dict(w)

        # Convertir los campos time en strings
        for key in time_fields:
            value = w.get(key)
            if value is not None:
                w[key] = value.strftime("%H:%M:%S")

        cleaned_warehouses.append(w)

    json_data = json.dumps(cleaned_warehouses, indent=4)

    response = HttpResponse(json_data, content_type="application/json")
    response["Content-Disposition"] = 'attachment; filename="warehouses_export.json"'
    return response


@login_required
@role_required(["admin"])
def warehouses_import_json(request):
    if request.method == "POST":
        form = WarehouseImportForm(request.POST, request.FILES)

        if form.is_valid():
            file = request.FILES["file"]

            try:
                data = json.load(file)
            except:
                messages.error(request, "Invalid JSON file.")
                return redirect("warehouses_import_json")

            if not isinstance(data, list):
                messages.error(request, "JSON must contain a list of warehouses.")
                return redirect("warehouses_import_json")

            count = 0
            for item in data:
                if not isinstance(item, dict):
                    continue

                Warehouse.objects.create(
                    name=item.get("name", ""),
                    location=item.get("location", ""),
                    capacity=item.get("capacity", 0)
                )
                count += 1

            messages.success(request, f"Imported {count} warehouses successfully.")
            return redirect("warehouses_list")

    else:
        form = WarehouseImportForm()

    return render(request, "warehouses/import.html", {"form": form})


@login_required
@role_required(["admin", "manager"])
def deliveries_export_json(request):
    deliveries = Delivery.objects.all().values()

    # Convertir cualquier campo no serializable (fecha) a string
    cleaned = []
    for d in deliveries:
        row = {}
        for key, value in d.items():
            if hasattr(value, "isoformat"):
                row[key] = value.isoformat()
            else:
                row[key] = value
        cleaned.append(row)

    json_data = json.dumps(cleaned, indent=4)

    response = HttpResponse(json_data, content_type="application/json")
    response["Content-Disposition"] = "attachment; filename=deliveries.json"
    return response


@login_required
@role_required(["admin", "manager"])
def deliveries_import_json(request):
    if request.method == "POST":
        form = DeliveryImportForm(request.POST, request.FILES)

        if form.is_valid():
            file = request.FILES["file"]
            data = json.load(file)

            count = 0
            for item in data:

                # ⚠️ Eliminar ID si viene en el JSON
                item.pop("id", None)

                Delivery.objects.create(
                    tracking_number=item.get("tracking_number", ""),
                    description=item.get("description", ""),
                    sender_name=item.get("sender_name", ""),
                    sender_address=item.get("sender_address", ""),
                    sender_phone=item.get("sender_phone", ""),
                    sender_email=item.get("sender_email", ""),
                    recipient_name=item.get("recipient_name", ""),
                    recipient_address=item.get("recipient_address", ""),
                    recipient_phone=item.get("recipient_phone", ""),
                    recipient_email=item.get("recipient_email", ""),
                    item_type=item.get("item_type", ""),
                    weight=item.get("weight", 0),
                    dimensions=item.get("dimensions", ""),
                    status=item.get("status", ""),
                    priority=item.get("priority", ""),
                    destination=item.get("destination", ""),
                    delivery_date=item.get("delivery_date", None),
                )

                count += 1

            messages.success(request, f"Imported {count} deliveries successfully.")
            return redirect("deliveries_list")

    else:
        form = DeliveryImportForm()

    return render(request, "deliveries/import.html", {"form": form})






@login_required
@role_required(["admin", "manager"])
def routes_import_json(request):
    if request.method == "POST":
        file = request.FILES.get("file")

        if not file:
            messages.error(request, "You must upload a JSON file.")
            return redirect("routes_import_json")

        data = json.load(file)
        count = 0

        for item in data:
            Route.objects.create(
                description=item.get("description", ""),
                delivery_status=item.get("delivery_status", ""),

                vehicle_id=item.get("vehicle_id"),
                driver_id=item.get("driver_id"),

                origin_name=item.get("origin_name", ""),
                origin_address=item.get("origin_address", ""),
                origin_contact=item.get("origin_contact", ""),

                destination_name=item.get("destination_name", ""),
                destination_address=item.get("destination_address", ""),
                destination_contact=item.get("destination_contact", ""),

                delivery_date=item.get("delivery_date"),
                delivery_start_time=item.get("delivery_start_time"),
                delivery_end_time=item.get("delivery_end_time"),

                kms_travelled=item.get("kms_travelled", 0),
                expected_duration=item.get("expected_duration"),
                driver_notes=item.get("driver_notes", "")
            )
            count += 1

        messages.success(request, f"Imported {count} routes successfully.")
        return redirect("routes_list")

    return render(request, "routes/import.html")


# --- IMPORTS NECESARIOS ---
from datetime import date, time, timedelta
import json

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Route


@login_required
@role_required(["admin", "manager"])
def routes_export_json(request):

    routes = list(Route.objects.all().values(
        "id",
        "description",
        "delivery_status",

        "vehicle_id",
        "driver_id",

        "origin_name",
        "origin_address",
        "origin_contact",

        "destination_name",
        "destination_address",
        "destination_contact",

        "delivery_date",
        "delivery_start_time",
        "delivery_end_time",

        "kms_travelled",
        "expected_duration",

        "driver_notes",
    ))

    # Convert Python objects into JSON-safe strings
    for r in routes:

        # Date → YYYY-MM-DD
        if isinstance(r["delivery_date"], date):
            r["delivery_date"] = r["delivery_date"].strftime("%Y-%m-%d")

        # Time → HH:MM:SS
        if isinstance(r["delivery_start_time"], time):
            r["delivery_start_time"] = r["delivery_start_time"].strftime("%H:%M:%S")

        if isinstance(r["delivery_end_time"], time):
            r["delivery_end_time"] = r["delivery_end_time"].strftime("%H:%M:%S")

        # Timedelta → HH:MM:SS
        if isinstance(r["expected_duration"], timedelta):
            total_seconds = int(r["expected_duration"].total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            r["expected_duration"] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    # Generate JSON
    json_data = json.dumps(routes, indent=4)

    # File response
    response = HttpResponse(json_data, content_type="application/json")
    response["Content-Disposition"] = 'attachment; filename="routes_export.json"'
    return response

import json
from datetime import datetime

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from .models import Invoice


from datetime import datetime
import json
from decimal import Decimal

@login_required
@role_required(["admin", "manager"])
def invoices_export_json(request):

    invoices = list(Invoice.objects.all().values(
        "id_invoice",
        "invoice_datetime",
        "invoice_status",
        "invoice_type",
        "cost",
        "payment_method",
        "address",
        "contact",
        "quantity",
        "name",
        "paid",
        "user_id",
    ))

    for inv in invoices:

        # Convert datetime → string
        dt = inv.get("invoice_datetime")
        if isinstance(dt, datetime):
            inv["invoice_datetime"] = dt.strftime("%Y-%m-%d %H:%M:%S")

        # Convert Decimal → float
        cost = inv.get("cost")
        if isinstance(cost, Decimal):
            inv["cost"] = float(cost)

        # Convert any Decimal fields in the future
        qty = inv.get("quantity")
        if isinstance(qty, Decimal):
            inv["quantity"] = float(qty)

    json_data = json.dumps(invoices, indent=4)

    response = HttpResponse(json_data, content_type="application/json")
    response["Content-Disposition"] = 'attachment; filename=\"invoices_export.json\"'
    return response



from django.db import connection
from django.http import HttpResponse
@login_required
@role_required(["admin", "manager"])
def vehicles_export_csv(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM export_vehicles_csv();")
        rows = cursor.fetchall()

    header = "id_vehicle,plate,brand,model,capacity,available\n"
    csv_data = header + "\n".join(r[0] for r in rows)

    response = HttpResponse(csv_data, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="vehicles_export.csv"'
    return response
@login_required
@role_required(["admin", "manager"])
def warehouses_export_csv(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM export_warehouses_csv();")
        rows = cursor.fetchall()

    header = "id_warehouse,name,address,contact,capacity\n"
    csv_data = header + "\n".join(r[0] for r in rows)

    response = HttpResponse(csv_data, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="warehouses_export.csv"'
    return response
@login_required
@role_required(["admin", "manager"])
def deliveries_export_csv(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM export_deliveries_csv();")
        rows = cursor.fetchall()

    header = (
        "id_delivery,tracking_number,status,weight,type,fragile,"
        "sender_name,sender_address,sender_contact,"
        "receiver_name,receiver_address,receiver_contact,"
        "route_id,warehouse_id\n"
    )

    csv_data = header + "\n".join(r[0] for r in rows)

    response = HttpResponse(csv_data, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="deliveries_export.csv"'
    return response
@login_required
@role_required(["admin", "manager"])
def routes_export_csv_pg(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM export_routes_csv();")
        rows = cursor.fetchall()

    header = (
        "id_route,description,delivery_status,"
        "vehicle_id,driver_id,"
        "origin_name,origin_address,origin_contact,"
        "destination_name,destination_address,destination_contact,"
        "delivery_date,delivery_start_time,delivery_end_time,"
        "kms_travelled,expected_duration,driver_notes\n"
    )

    csv_data = header + "\n".join(r[0] for r in rows)

    response = HttpResponse(csv_data, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="routes_export.csv"'
    return response
@login_required
@role_required(["admin", "manager"])
def invoices_export_csv(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM export_invoices_csv();")
        rows = cursor.fetchall()

    header = (
        "id_invoice,invoice_datetime,invoice_status,invoice_type,"
        "name,address,contact,cost,quantity,paid,payment_method,user_id\n"
    )

    csv_data = header + "\n".join(r[0] for r in rows)

    response = HttpResponse(csv_data, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="invoices_export.csv"'
    return response





def invoices_export_csv(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM export_invoices_csv();")
        rows = cursor.fetchall()

    content = "id_invoice,invoice_status,invoice_type,quantity,invoice_datetime,cost,paid,payment_method,name,address,contact,user_id\n"
    content += "\n".join(row[0] for row in rows)

    response = HttpResponse(content, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="invoices.csv"'
    return response
