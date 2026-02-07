# # ==========================================================
# #  EMPLOYEES
# # ==========================================================
# from datetime import datetime
# from decimal import Decimal
# import json
# from pyexpat.errors import messages
# from django.db import connection
# from django.shortcuts import render, get_object_or_404, redirect
# from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
# from ..models import Employee, Invoice, User
# from ..forms import EmployeeDriverForm, EmployeeForm, EmployeeStaffForm, InvoiceForm
# from .decorators import role_required
# from django.contrib.auth.decorators import login_required
# from django.core.paginator import Paginator
from django.db import connection
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .decorators import role_required


# @login_required
# @role_required(["admin"])
# def employees_list(request):
#     employees_qs = Employee.objects.select_related("user").all()
#     paginator = Paginator(employees_qs, 10)
#     page_number = request.GET.get("page")
#     employees_page = paginator.get_page(page_number)
#     return render(request, "core/employees_list.html", {"employees": employees_page})



@login_required
@role_required(["admin", "manager"])
def employees_list(request):
    """
    Admin / Manager list of all employees.
    Data is read from SQL VIEW v_employees_full.
    """

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT *
            FROM v_employees_full
            ORDER BY full_name
        """)
        columns = [col[0] for col in cursor.description]
        employees = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return render(
        request,
        "core/employees_list.html",
        {"employees": employees},
    )


# @login_required
# @role_required(["admin"])
# def employees_form(request, employee_id=None):
#     if employee_id:
#         employee = get_object_or_404(Employee, pk=employee_id)
#     else:
#         employee = None

#     if request.method == "POST":
#         user_id = request.POST.get("user_id")
#         if not user_id:
#             return HttpResponseBadRequest("Missing user selection for employee.")
#         user = get_object_or_404(User, pk=user_id)

#         if employee is None and user.role in {"admin", "client"}:
#             return HttpResponseBadRequest("Selected user cannot become an employee.")
#         if employee is None and hasattr(user, "employee"):
#             return HttpResponseBadRequest("User is already assigned to an employee record.")
#         if employee is not None and employee.user_id != user.pk:
#             return HttpResponseBadRequest("User mismatch: cannot reassign existing employee to a different user.")

#         if employee is None:
#             employee = Employee(user=user)

#         old_position = employee.position if employee.pk else None
#         emp_form = EmployeeForm(request.POST, instance=employee)

#         position = request.POST.get("position")
#         driver_form = staff_form = None
#         if position == "Driver":
#             driver_info = getattr(employee, "driver_info", None)
#             driver_form = EmployeeDriverForm(request.POST, instance=driver_info)
#         elif position == "Staff":
#             staff_info = getattr(employee, "staff_info", None)
#             staff_form = EmployeeStaffForm(request.POST, instance=staff_info)

#         forms_valid = emp_form.is_valid()
#         if driver_form:
#             forms_valid = forms_valid and driver_form.is_valid()
#         if staff_form:
#             forms_valid = forms_valid and staff_form.is_valid()

#         if forms_valid:
#             saved_employee = emp_form.save()

#             if old_position and old_position != position:
#                 try:
#                     if old_position == "Driver" and hasattr(saved_employee, "driver_info"):
#                         saved_employee.driver_info.delete()
#                     if old_position == "Staff" and hasattr(saved_employee, "staff_info"):
#                         saved_employee.staff_info.delete()
#                 except Exception:
#                     pass

#             if position == "Driver" and driver_form:
#                 driver_model = driver_form.save(commit=False)
#                 driver_model.employee = saved_employee
#                 driver_model.save()
#                 saved_employee.user.role = "driver"
#                 saved_employee.user.save(update_fields=["role"])
#             elif position == "Staff" and staff_form:
#                 staff_model = staff_form.save(commit=False)
#                 staff_model.employee = saved_employee
#                 staff_model.save()
#                 saved_employee.user.role = "staff"
#                 saved_employee.user.save(update_fields=["role"])

#             return redirect("employees_list")
#     else:
#         emp_form = EmployeeForm(instance=employee)
#         driver_info = getattr(employee, "driver_info", None) if employee else None
#         staff_info = getattr(employee, "staff_info", None) if employee else None

#         driver_form = EmployeeDriverForm(instance=driver_info) if driver_info else EmployeeDriverForm()
#         staff_form = EmployeeStaffForm(instance=staff_info) if staff_info else EmployeeStaffForm()

#     return render(
#         request,
#         "core/employees_form.html",
#         {
#             "employee_form": emp_form,
#             "driver_form": driver_form,
#             "staff_form": staff_form,
#             "employee": employee,
#         },
#     )





@login_required
@role_required(["admin", "manager"])
def employees_form(request, employee_id=None):
    """
    Create or edit an employee (driver or staff).
    - CREATE  -> sp_create_employee
    - UPDATE  -> sp_update_employee
    All business logic is enforced at DB level.
    """

    is_edit = employee_id is not None

    if request.method == "POST":
        data = request.POST

        with connection.cursor() as cursor:
            if is_edit:
                # =========================
                # UPDATE EXISTING EMPLOYEE
                # =========================
                cursor.execute(
                    """
                    CALL sp_update_employee(
                        %s,  -- employee id

                        -- USER fields
                        %s, %s, %s, %s, %s,

                        -- EMPLOYEE fields
                        %s, %s, %s, %s, %s,

                        -- DRIVER fields
                        %s, %s, %s, %s, %s,

                        -- STAFF fields
                        %s
                    )
                    """,
                    [
                        employee_id,

                        # USER
                        data.get("email"),
                        data.get("first_name"),
                        data.get("last_name"),
                        data.get("contact"),
                        data.get("address"),

                        # EMPLOYEE
                        data.get("war_id"),
                        data.get("emp_position"),      # driver / staff
                        data.get("schedule"),
                        data.get("wage"),
                        data.get("is_active") == "on",

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

            else:
                # =========================
                # CREATE NEW EMPLOYEE
                # =========================
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
                        data["password"],          # hashed before or academic
                        data.get("first_name"),
                        data.get("last_name"),
                        data.get("contact"),
                        data.get("address"),

                        # EMPLOYEE
                        data["war_id"],
                        data["emp_position"],      # driver / staff
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

    return render(
        request,
        "employees/employees_form.html",
        {
            "is_edit": is_edit,
            "employee_id": employee_id,
        },
    )
