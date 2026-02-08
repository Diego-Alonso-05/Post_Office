# ==========================================================
#  USERS / AUTH / CLIENTS / EMPLOYEES
# ==========================================================

from django.db import connection
from django.shortcuts import render, redirect
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    get_user_model,
)
from django.contrib.auth.hashers import make_password

from .decorators import role_required


# ==========================================================
#  ADMIN – USERS LIST
# ==========================================================

@login_required
@role_required(["admin"])
def users_list(request):
    """
    Admin-only list of all system users.
    Data is read from SQL VIEW v_users_admin.
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM v_users_admin")
        columns = [col[0] for col in cursor.description]
        users = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return render("core/users_list.html", {"users": users})


# ==========================================================
#  EMPLOYEES
# ==========================================================

@login_required
@role_required(["admin", "manager"])
def employees_create(request):
    """
    Create an employee (driver or staff) using sp_create_employee.
    """

    if request.method == "POST":
        data = request.POST

        with connection.cursor() as cursor:
            cursor.execute(
                """
                CALL sp_create_employee(
                    %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s
                )
                """,
                [
                    # USER
                    data["username"],
                    data["email"],
                    data["password"],
                    data.get("first_name"),
                    data.get("last_name"),
                    data.get("contact"),
                    data.get("address"),

                    # EMPLOYEE
                    data["war_id"],
                    data["emp_position"],
                    data.get("schedule"),
                    data.get("wage"),
                    data.get("hire_date"),

                    # DRIVER
                    data.get("license_number"),
                    data.get("license_category"),
                    data.get("license_expiry"),
                    data.get("driving_experience"),
                    data.get("driver_status"),

                    # STAFF
                    data.get("department"),
                ],
            )

        return redirect("employees_list")

    return render(request, "employees/employees_form.html")


# ==========================================================
#  CLIENTS – LIST
# ==========================================================

@login_required
@role_required(["admin"])
def clients_list(request):
    """
    Admin-only list of clients using v_clients view.
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM v_clients")
        columns = [col[0] for col in cursor.description]
        clients = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return render(request, "core/clients.html", {"clients": clients})


# ==========================================================
#  CLIENTS – CREATE / EDIT
# ==========================================================

@login_required
@role_required(["admin"])
def clients_form(request, user_id=None):
    """
    Create or edit a CLIENT user.
    Role is always 'client'.
    """

    is_edit = user_id is not None

    if request.method == "POST":
        data = request.POST

        with connection.cursor() as cursor:
            if is_edit:
                cursor.execute(
                    """
                    CALL sp_update_user(
                        %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    """,
                    [
                        user_id,
                        data.get("email"),
                        data.get("first_name"),
                        data.get("last_name"),
                        data.get("contact"),
                        data.get("address"),
                        "client",
                        data.get("is_active") == "on",
                    ],
                )
            else:
                cursor.execute(
                    """
                    CALL sp_create_user(
                        %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    """,
                    [
                        data["username"],
                        data["email"],
                        make_password(data["password"]),
                        data.get("first_name"),
                        data.get("last_name"),
                        data.get("contact"),
                        data.get("address"),
                        "client",
                    ],
                )

        return redirect("clients_list")

    return render(
        request,
        "core/clients_form.html",
        {"is_edit": is_edit},
    )


# ==========================================================
#  CLIENT PROFILE
# ==========================================================

@login_required
@role_required(["client", "admin"])
def client_profile(request):
    """
    Client profile page.
    """
    deliveries = []

    if request.user.role == "client":
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM fn_get_client_deliveries(%s)",
                [request.user.id],
            )
            columns = [col[0] for col in cursor.description]
            deliveries = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return render(
        request,
        "clients/profile.html",
        {
            "user": request.user,
            "deliveries": deliveries,
        },
    )


# ==========================================================
#  AUTH – LOGIN
# ==========================================================

def login_view(request):
    User = get_user_model()

    if request.method == "POST":
        username_or_email = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username_or_email or not password:
            messages.error(request, "Faltan credenciales.")
            return render(request, "auth/login.html")

        user = authenticate(request, username=username_or_email, password=password)

        if user is None:
            u = User.objects.filter(email=username_or_email).first()
            if u:
                user = authenticate(
                    request,
                    username=u.get_username(),
                    password=password,
                )

        if user is None:
            messages.error(request, "Credenciales incorrectas.")
            return render(request, "auth/login.html")

        login(request, user)
        return redirect("home")

    return render(request, "auth/login.html")


# ==========================================================
#  AUTH – LOGOUT
# ==========================================================

@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


# ==========================================================
#  AUTH – REGISTER
# ==========================================================

def register_view(request):
    User = get_user_model()

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")

        if not username or not email or not password:
            messages.error(request, "Rellena todos los campos.")
            return render(request, "auth/register.html")

        if password != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, "auth/register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Ese username ya existe.")
            return render(request, "auth/register.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Ese email ya está usado.")
            return render(request, "auth/register.html")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

        login(request, user)
        return redirect("home")

    return render(request, "auth/register.html")


# ==========================================================
#  DASHBOARD
# ==========================================================

@login_required
def dashboard(request):
    return render(request, "dashboard/admin.html")
