from functools import wraps
from datetime import date, time, timedelta, datetime
import json
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import (
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponseBadRequest,
    JsonResponse,
)
from django.shortcuts import render, redirect, get_object_or_404

from .models import (
    User,
    Employee,
    EmployeeDriver,
    EmployeeStaff,
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

from .notifications import create_notification

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

# ========================= =================================
#  NOTIFICATIONS - USES MONGODB ONLY
# ==========================================================
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
# Import notification helper functions from notifications.py
from .notifications import get_user_notifications, mark_as_read

@login_required
def get_notifications(request):
    """
    API endpoint to retrieve ALL notifications for the currently logged-in user.
    Only returns notifications from the last 2 minutes.

    Returns:
        JsonResponse: JSON object containing array of user's recent notifications
    """
    # Get the email of the currently logged-in user
    user_email = request.user.email

    # Fetch ALL notifications from the last 2 minutes
    data = get_user_notifications(user_email)

    # Return notifications as JSON response
    return JsonResponse({"notifications": data})

@login_required
def mark_notification_read(request, notif_id):
    """
    API endpoint to mark a specific notification as read.
    Args:
        notif_id (str): MongoDB ObjectId as a string from URL parameter
    Returns:
        JsonResponse: JSON object with status "ok" or "error"
    """
    # Attempt to mark the notification as read using helper function
    success = mark_as_read(notif_id)
    # Return success or error status
    if success:
        return JsonResponse({"status": "ok"})
    else:
        return JsonResponse({"status": "error"})


# ==========================================================
#  DASHBOARD
# ==========================================================
@login_required
def dashboard(request):
    role = request.user.role

    if role == "admin":
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
        my_deliveries = Delivery.objects.filter(driver=employee) if employee else Delivery.objects.none()
        stats = {"my_deliveries": my_deliveries}
    else:  # client, staff, manager
        stats = {"my_deliveries": Delivery.objects.filter(client=request.user)}

    return render(request, "dashboard/admin.html", {"stats": stats, "role": role})


# ==========================================================
#  HOME
# ==========================================================
def home(request):
    return render(request, "core/home.html")


# ==========================================================
#  USER & CLIENT MANAGEMENT
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
            form.save()
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
#  EMPLOYEES
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
    if employee_id:
        employee = get_object_or_404(Employee, pk=employee_id)
    else:
        employee = None

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        if not user_id:
            return HttpResponseBadRequest("Missing user selection for employee.")
        user = get_object_or_404(User, pk=user_id)

        if employee is None and user.role in {"admin", "client"}:
            return HttpResponseBadRequest("Selected user cannot become an employee.")
        if employee is None and hasattr(user, "employee"):
            return HttpResponseBadRequest("User is already assigned to an employee record.")
        if employee is not None and employee.user_id != user.pk:
            return HttpResponseBadRequest("User mismatch: cannot reassign existing employee to a different user.")

        if employee is None:
            employee = Employee(user=user)

        old_position = employee.position if employee.pk else None
        emp_form = EmployeeForm(request.POST, instance=employee)

        position = request.POST.get("position")
        driver_form = staff_form = None
        if position == "Driver":
            driver_info = getattr(employee, "driver_info", None)
            driver_form = EmployeeDriverForm(request.POST, instance=driver_info)
        elif position == "Staff":
            staff_info = getattr(employee, "staff_info", None)
            staff_form = EmployeeStaffForm(request.POST, instance=staff_info)

        forms_valid = emp_form.is_valid()
        if driver_form:
            forms_valid = forms_valid and driver_form.is_valid()
        if staff_form:
            forms_valid = forms_valid and staff_form.is_valid()

        if forms_valid:
            saved_employee = emp_form.save()

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
#  WAREHOUSES
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
            # Save the warehouse and get the instance
            warehouse = form.save()

            # Create notification for the admin who created it
            create_notification(
                notification_type="warehouse_created",
                recipient_contact=request.user.email,  # Send to current admin
                subject="Warehouse Created",
                message=f"Successfully created warehouse: {warehouse.name}",
                status="sent"
            )

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
            # Save the updated warehouse
            form.save()

            # Create notification for the user who edited it
            create_notification(
                notification_type="warehouse_updated",
                recipient_contact=request.user.email,  # Send to current user (admin/staff)
                subject="Warehouse Updated",
                message=f"Successfully updated warehouse: {warehouse.name}",
                status="sent"
            )

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
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method for deletion.")

    warehouse = get_object_or_404(Warehouse, pk=warehouse_id)
    # Store the warehouse name before deleting
    warehouse_name = warehouse.name

    try:
        warehouse.delete()

        # Create notification after successful deletion
        create_notification(
            notification_type="warehouse_deleted",
            recipient_contact=request.user.email,  # Send to admin who deleted it
            subject="Warehouse Deleted",
            message=f"Successfully deleted warehouse: {warehouse_name}",
            status="sent"
        )

        messages.success(request, "Warehouse deleted successfully.")
    except Exception:
        messages.error(request, "An error occurred while deleting the warehouse.")

    return redirect("warehouses_list")

# ==========================================================
#  VEHICLES
# ==========================================================
@login_required
@role_required(["admin", "manager"])
def vehicles_create(request):
    if request.method == "POST":
        form = VehicleForm(request.POST)
        if form.is_valid():
            # Save the vehicle and get the instance
            vehicle = form.save()

            # Create notification for the user who created it
            create_notification(
                notification_type="vehicle_created",
                recipient_contact=request.user.email,  # Send to current admin/manager
                subject="Vehicle Created",
                message=f"Successfully created vehicle: {vehicle.plate_number} ({vehicle.brand} {vehicle.model})",
                status="sent"
            )

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
    return render(request, "vehicles/list.html", {"vehicles": vehicles_page})


@login_required
@role_required(["admin", "manager"])
def vehicles_edit(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
    if request.method == "POST":
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            # Save the updated vehicle
            form.save()

            # Create notification for the user who edited it
            create_notification(
                notification_type="vehicle_updated",
                recipient_contact=request.user.email,  # Send to current admin/manager
                subject="Vehicle Updated",
                message=f"Successfully updated vehicle: {vehicle.plate_number} ({vehicle.brand} {vehicle.model})",
                status="sent"
            )

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
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method for deletion.")

    vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
    # Store vehicle info before deleting
    vehicle_info = f"{vehicle.plate_number} ({vehicle.brand} {vehicle.model})"

    try:
        vehicle.delete()

        # Create notification after successful deletion
        create_notification(
            notification_type="vehicle_deleted",
            recipient_contact=request.user.email,  # Send to admin who deleted it
            subject="Vehicle Deleted",
            message=f"Successfully deleted vehicle: {vehicle_info}",
            status="sent"
        )

        messages.success(request, "Vehicle deleted successfully.")
    except Exception:
        messages.error(request, "An error occurred while deleting the vehicle.")

    return redirect("vehicles_list")


# ==========================================================
#  ROUTES
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
            # Save the route and get the instance
            route = form.save()

            # Create notification for the admin who created it
            create_notification(
                notification_type="route_created",
                recipient_contact=request.user.email,  # Send to current admin
                subject="Route Created",
                message=f"Successfully created route: {route.origin_name} → {route.destination_name}",
                status="sent"
            )

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
            # Save the updated route
            form.save()

            # Create notification for the admin who edited it
            create_notification(
                notification_type="route_updated",
                recipient_contact=request.user.email,  # Send to current admin
                subject="Route Updated",
                message=f"Successfully updated route: {route.origin_name} → {route.destination_name}",
                status="sent"
            )

            return redirect("routes_list")
    else:
        form = RouteForm(instance=route)
    return render(request, "routes/edit.html", {"form": form, "route": route})


@login_required
@role_required(["admin"])
def routes_delete(request, route_id):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method for deletion.")

    route = get_object_or_404(Route, pk=route_id)
    # Store route info before deleting
    route_info = f"{route.origin_name} → {route.destination_name}"

    try:
        route.delete()

        # Create notification after successful deletion
        create_notification(
            notification_type="route_deleted",
            recipient_contact=request.user.email,  # Send to admin who deleted it
            subject="Route Deleted",
            message=f"Successfully deleted route: {route_info}",
            status="sent"
        )

        messages.success(request, "Route deleted successfully.")
    except Exception:
        messages.error(request, "An error occurred while deleting the route.")

    return redirect("routes_list")


# ==========================================================
#  DELIVERIES
# ==========================================================
@login_required
@role_required(["driver", "admin", "client", "staff", "manager"])
def deliveries_list(request):
    role = request.user.role
    if role in {"admin", "manager", "staff"}:
        deliveries_qs = Delivery.objects.select_related("driver", "client", "route").all()
    elif role == "driver":
        employee = getattr(request.user, "employee", None)
        deliveries_qs = Delivery.objects.filter(driver=employee) if employee else Delivery.objects.none()
    else:  # client
        deliveries_qs = Delivery.objects.filter(client=request.user)
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
            # Save the delivery and get the instance
            new_delivery = form.save()

            # Notification for the recipient (client/customer) - existing logic
            recipient = None
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

            # Notification for the admin/staff who created it
            create_notification(
                notification_type="delivery_created_admin",
                recipient_contact=request.user.email,  # Send to current admin/staff
                subject="Delivery Created",
                message=f"Successfully created delivery: {new_delivery.tracking_number} ({new_delivery.recipient_name})",
                status="sent"
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
            # Save the updated delivery
            form.save()

            # Create notification for the admin/staff who edited it
            create_notification(
                notification_type="delivery_updated",
                recipient_contact=request.user.email,  # Send to current admin/staff
                subject="Delivery Updated",
                message=f"Successfully updated delivery: {delivery.tracking_number} ({delivery.recipient_name})",
                status="sent"
            )

            return redirect("deliveries_list")
    else:
        form = DeliveryForm(instance=delivery)
    return render(request, "deliveries/edit.html", {"form": form, "delivery": delivery})


@login_required
@role_required(["admin"])
def deliveries_delete(request, delivery_id):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method for deletion.")

    delivery = get_object_or_404(Delivery, pk=delivery_id)
    # Store delivery info before deleting
    delivery_info = f"{delivery.tracking_number} ({delivery.recipient_name})"

    try:
        delivery.delete()

        # Create notification after successful deletion
        create_notification(
            notification_type="delivery_deleted",
            recipient_contact=request.user.email,  # Send to admin who deleted it
            subject="Delivery Deleted",
            message=f"Successfully deleted delivery: {delivery_info}",
            status="sent"
        )

        messages.success(request, "Delivery deleted successfully.")
    except Exception:
        messages.error(request, "An error occurred while deleting the delivery.")

    return redirect("deliveries_list")


# ==========================================================
#  CLIENT PROFILE
# ==========================================================
@login_required
@role_required(["client", "admin"])
def client_profile(request):
    if request.user.role == "client":
        my_deliveries = Delivery.objects.filter(client=request.user)
        user_obj = request.user
    else:
        my_deliveries = Delivery.objects.none()
        user_obj = request.user

    return render(
        request,
        "clients/profile.html",
        {"deliveries": my_deliveries, "user": user_obj},
    )


# ==========================================================
#  SIMPLE MAIL PAGES
# ==========================================================
def mail_list(request):
    return render(request, "mail/list.html")


def mail_detail(request, mail_id):
    return render(request, "mail/detail.html", {"mail_id": mail_id})


# ==========================================================
#  JSON EXPORTS (Django side) + IMPORTS
# ==========================================================
# ==================== VEHICLES ====================

@login_required
@role_required(["admin", "manager", "staff"])
def vehicles_export_json(request):
    vehicles = list(Vehicle.objects.all().values())
    cleaned = []
    for v in vehicles:
        v = dict(v)
        lm = v.get("last_maintenance_date")
        if isinstance(lm, (date, datetime)):
            v["last_maintenance_date"] = lm.isoformat()
        cleaned.append(v)

    json_data = json.dumps(cleaned, indent=4)
    response = HttpResponse(json_data, content_type="application/json")
    response["Content-Disposition"] = 'attachment; filename="vehicles_export.json"'

    # Create notification for the user who exported
    create_notification(
        notification_type="vehicles_exported",
        recipient_contact=request.user.email,
        subject="Vehicles Exported",
        message=f"Successfully exported {len(cleaned)} vehicles to JSON",
        status="sent"
    )

    return response


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

            if not isinstance(data, list):
                messages.error(request, "JSON must contain a list of vehicles.")
                return redirect("vehicles_import_json")

            count = 0

            for item in data:
                if not isinstance(item, dict):
                    continue

                # 🔥 REMOVE ID ALWAYS — IMPORTER WILL BREAK WITHOUT THIS
                if "id" in item:
                    del item["id"]

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

            # Create notification for the user who imported
            create_notification(
                notification_type="vehicles_imported",
                recipient_contact=request.user.email,
                subject="Vehicles Imported",
                message=f"Successfully imported {count} vehicles from JSON",
                status="sent"
            )

            messages.success(request, f"Imported {count} vehicles successfully.")
            return redirect("vehicles_list")

    else:
        form = VehicleImportForm()

    return render(request, "vehicles/import.html", {"form": form})


# ==================== WAREHOUSES ====================

@login_required
@role_required(["admin", "manager"])
def warehouses_export_json(request):
    warehouses = list(
        Warehouse.objects.all().values(
            "id",
            "name",
            "address",
            "contact",
            "po_schedule_open",
            "po_schedule_close",
            "maximum_storage_capacity",
        )
    )

    cleaned = []
    for w in warehouses:
        w = dict(w)
        for field in ("po_schedule_open", "po_schedule_close"):
            val = w.get(field)
            if isinstance(val, time):
                w[field] = val.strftime("%H:%M:%S")
        cleaned.append(w)

    json_data = json.dumps(cleaned, indent=4)
    response = HttpResponse(json_data, content_type="application/json")
    response["Content-Disposition"] = 'attachment; filename="warehouses_export.json"'

    # Create notification for the user who exported
    create_notification(
        notification_type="warehouses_exported",
        recipient_contact=request.user.email,
        subject="Warehouses Exported",
        message=f"Successfully exported {len(cleaned)} warehouses to JSON",
        status="sent"
    )

    return response


@login_required
@role_required(["admin"])
def warehouses_import_json(request):
    if request.method == "POST":
        form = WarehouseImportForm(request.POST, request.FILES)

        if form.is_valid():
            file = request.FILES["file"]

            # Load JSON safely
            try:
                data = json.load(file)
            except Exception:
                messages.error(request, "Invalid JSON file.")
                return redirect("warehouses_import_json")

            if not isinstance(data, list):
                messages.error(request, "JSON must contain a list of warehouses.")
                return redirect("warehouses_import_json")

            count = 0

            for raw in data:
                if not isinstance(raw, dict):
                    continue

                item = dict(raw)  # isolate mutation

                # =====================================================
                # 1. STRIP ANY PRIMARY KEY FIELD (absolute protection)
                # =====================================================
                for key in list(item.keys()):
                    if "id" in key.lower():
                        item.pop(key, None)

                # =====================================================
                # 2. MAP BOTH IMPORT & EXPORT FIELD NAMES
                # =====================================================
                name = item.get("name")

                address = (
                    item.get("address")
                    or item.get("location")
                )

                contact = item.get("contact")

                po_open = item.get("po_schedule_open")
                po_close = item.get("po_schedule_close")

                max_capacity = (
                    item.get("maximum_storage_capacity")
                    or item.get("capacity")
                )

                # =====================================================
                # 3. VALIDATE required NOT NULL fields manually
                # =====================================================
                if not name or not address:
                    continue

                # =====================================================
                # 4. CREATE SAFE NEW WAREHOUSE ENTRY
                # =====================================================
                Warehouse.objects.create(
                    name=name,
                    address=address,
                    contact=contact,
                    po_schedule_open=po_open,
                    po_schedule_close=po_close,
                    maximum_storage_capacity=max_capacity,
                )

                count += 1

            # Create notification for the user who imported
            create_notification(
                notification_type="warehouses_imported",
                recipient_contact=request.user.email,
                subject="Warehouses Imported",
                message=f"Successfully imported {count} warehouses from JSON",
                status="sent"
            )

            messages.success(request, f"Imported {count} warehouses successfully.")
            return redirect("warehouses_list")

    else:
        form = WarehouseImportForm()

    return render(request, "warehouses/import.html", {"form": form})


# ==================== DELIVERIES ====================

@login_required
@role_required(["admin", "manager"])
def deliveries_export_json(request):
    deliveries = Delivery.objects.all().values()

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

    # Create notification for the user who exported
    create_notification(
        notification_type="deliveries_exported",
        recipient_contact=request.user.email,
        subject="Deliveries Exported",
        message=f"Successfully exported {len(cleaned)} deliveries to JSON",
        status="sent"
    )

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

                # Debug print – REMOVE AFTER TESTING
                print("IMPORT ITEM BEFORE CLEAN:", item)

                # Remove ANY key that looks like an id
                for key in list(item.keys()):
                    if key.lower() == "id":
                        item.pop(key)

                # Debug print – REMOVE AFTER TESTING
                print("IMPORT ITEM AFTER CLEAN:", item)

                Delivery.objects.create(
                    tracking_number=item.get("tracking_number"),
                    description=item.get("description"),
                    sender_name=item.get("sender_name"),
                    sender_address=item.get("sender_address"),
                    sender_phone=item.get("sender_phone"),
                    sender_email=item.get("sender_email"),
                    recipient_name=item.get("recipient_name"),
                    recipient_address=item.get("recipient_address"),
                    recipient_phone=item.get("recipient_phone"),
                    recipient_email=item.get("recipient_email"),
                    item_type=item.get("item_type"),
                    weight=item.get("weight"),
                    dimensions=item.get("dimensions"),
                    status=item.get("status"),
                    priority=item.get("priority"),
                    destination=item.get("destination"),
                    delivery_date=item.get("delivery_date"),

                    # Foreign keys
                    driver_id=item.get("driver_id"),
                    client_id=item.get("client_id"),
                    route_id=item.get("route_id"),
                    invoice_id=item.get("invoice_id"),
                )

                count += 1

            # Create notification for the user who imported
            create_notification(
                notification_type="deliveries_imported",
                recipient_contact=request.user.email,
                subject="Deliveries Imported",
                message=f"Successfully imported {count} deliveries from JSON",
                status="sent"
            )

            messages.success(request, f"Imported {count} deliveries successfully.")
            return redirect("deliveries_list")

    else:
        form = DeliveryImportForm()

    return render(request, "deliveries/import.html", {"form": form})


# ==================== ROUTES ====================

@login_required
@role_required(["admin", "manager"])
def routes_import_json(request):
    if request.method == "POST":
        file = request.FILES.get("file")

        if not file:
            messages.error(request, "You must upload a JSON file.")
            return redirect("routes_import_json")

        try:
            data = json.load(file)
        except Exception:
            messages.error(request, "Invalid JSON file.")
            return redirect("routes_import_json")

        if not isinstance(data, list):
            messages.error(request, "JSON must contain a list of routes.")
            return redirect("routes_import_json")

        count = 0

        for item in data:

            # Always remove id to avoid IntegrityError
            if "id" in item:
                del item["id"]

            # Create the route safely
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

        # Create notification for the user who imported
        create_notification(
            notification_type="routes_imported",
            recipient_contact=request.user.email,
            subject="Routes Imported",
            message=f"Successfully imported {count} routes from JSON",
            status="sent"
        )

        messages.success(request, f"Imported {count} routes successfully.")
        return redirect("routes_list")

    return render(request, "routes/import.html")


@login_required
@role_required(["admin", "manager"])
def routes_export_json(request):
    routes = list(
        Route.objects.all().values(
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
        )
    )

    for r in routes:
        if isinstance(r["delivery_date"], date):
            r["delivery_date"] = r["delivery_date"].strftime("%Y-%m-%d")

        if isinstance(r["delivery_start_time"], time):
            r["delivery_start_time"] = r["delivery_start_time"].strftime("%H:%M:%S")

        if isinstance(r["delivery_end_time"], time):
            r["delivery_end_time"] = r["delivery_end_time"].strftime("%H:%M:%S")

        if isinstance(r["expected_duration"], timedelta):
            total_seconds = int(r["expected_duration"].total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            r["expected_duration"] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    json_data = json.dumps(routes, indent=4)
    response = HttpResponse(json_data, content_type="application/json")
    response["Content-Disposition"] = 'attachment; filename="routes_export.json"'

    # Create notification for the user who exported
    create_notification(
        notification_type="routes_exported",
        recipient_contact=request.user.email,
        subject="Routes Exported",
        message=f"Successfully exported {len(routes)} routes to JSON",
        status="sent"
    )

    return response


# ==================== INVOICES ====================
@login_required
@role_required(["admin", "manager"])
def invoices_export_json(request):
    invoices = list(
        Invoice.objects.all().values(
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
        )
    )

    for inv in invoices:
        dt = inv.get("invoice_datetime")
        if isinstance(dt, datetime):
            inv["invoice_datetime"] = dt.strftime("%Y-%m-%d %H:%M:%S")

        cost = inv.get("cost")
        if isinstance(cost, Decimal):
            inv["cost"] = float(cost)

        qty = inv.get("quantity")
        if isinstance(qty, Decimal):
            inv["quantity"] = float(qty)

    json_data = json.dumps(invoices, indent=4)
    response = HttpResponse(json_data, content_type="application/json")
    response["Content-Disposition"] = 'attachment; filename="invoices_export.json"'

    # Create notification for the user who exported
    create_notification(
        notification_type="invoices_exported",
        recipient_contact=request.user.email,
        subject="Invoices Exported",
        message=f"Successfully exported {len(invoices)} invoices to JSON",
        status="sent"
    )

    return response


# ==========================================================
#  CSV EXPORTS (PostgreSQL functions)
# ==========================================================

@login_required
@role_required(["admin", "manager"])
def vehicles_export_csv(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM export_vehicles_csv();")
        rows = cursor.fetchall()

    header = "id,plate_number,model,brand,vehicle_status,year,fuel_type,capacity,last_maintenance_date\n"
    csv_data = header + "\n".join(r[0] for r in rows)

    response = HttpResponse(csv_data, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="vehicles_export.csv"'

    # Create notification for the user who exported
    create_notification(
        notification_type="vehicles_exported_csv",
        recipient_contact=request.user.email,
        subject="Vehicles Exported",
        message=f"Successfully exported {len(rows)} vehicles to CSV",
        status="sent"
    )

    return response


@login_required
@role_required(["admin", "manager"])
def warehouses_export_csv(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM export_warehouses_csv();")
        rows = cursor.fetchall()

    header = "id,name,address,contact,po_schedule_open,po_schedule_close,maximum_storage_capacity\n"
    csv_data = header + "\n".join(r[0] for r in rows)

    response = HttpResponse(csv_data, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="warehouses_export.csv"'

    # Create notification for the user who exported
    create_notification(
        notification_type="warehouses_exported_csv",
        recipient_contact=request.user.email,
        subject="Warehouses Exported",
        message=f"Successfully exported {len(rows)} warehouses to CSV",
        status="sent"
    )

    return response


@login_required
@role_required(["admin", "manager"])
def deliveries_export_csv(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM export_deliveries_csv();")
        rows = cursor.fetchall()

    header = (
        "id,tracking_number,description,"
        "sender_name,sender_address,sender_phone,sender_email,"
        "recipient_name,recipient_address,recipient_phone,recipient_email,"
        "item_type,weight,dimensions,status,priority,"
        "registered_at,updated_at,in_transition,destination,delivery_date,"
        "driver_id,invoice_id,route_id,client_id\n"
    )
    csv_data = header + "\n".join(r[0] for r in rows)

    response = HttpResponse(csv_data, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="deliveries_export.csv"'

    # Create notification for the user who exported
    create_notification(
        notification_type="deliveries_exported_csv",
        recipient_contact=request.user.email,
        subject="Deliveries Exported",
        message=f"Successfully exported {len(rows)} deliveries to CSV",
        status="sent"
    )

    return response


@login_required
@role_required(["admin", "manager"])
def routes_export_csv(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM export_routes_csv();")
        rows = cursor.fetchall()

    header = (
        "id,description,delivery_status,"
        "vehicle_id,driver_id,"
        "origin_name,origin_address,origin_contact,"
        "destination_name,destination_address,destination_contact,"
        "delivery_date,delivery_start_time,delivery_end_time,"
        "kms_travelled,expected_duration,driver_notes\n"
    )
    csv_data = header + "\n".join(r[0] for r in rows)

    response = HttpResponse(csv_data, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="routes_export.csv"'

    # Create notification for the user who exported
    create_notification(
        notification_type="routes_exported_csv",
        recipient_contact=request.user.email,
        subject="Routes Exported",
        message=f"Successfully exported {len(rows)} routes to CSV",
        status="sent"
    )

    return response


@login_required
@role_required(["admin", "manager"])
def invoices_export_csv(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM export_invoices_csv();")
        rows = cursor.fetchall()

    header = (
        "id_invoice,invoice_status,invoice_type,quantity,"
        "invoice_datetime,cost,paid,payment_method,"
        "name,address,contact,user_id\n"
    )
    csv_data = header + "\n".join(r[0] for r in rows)

    response = HttpResponse(csv_data, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="invoices_export.csv"'

    # Create notification for the user who exported
    create_notification(
        notification_type="invoices_exported_csv",
        recipient_contact=request.user.email,
        subject="Invoices Exported",
        message=f"Successfully exported {len(rows)} invoices to CSV",
        status="sent"
    )

    return response




