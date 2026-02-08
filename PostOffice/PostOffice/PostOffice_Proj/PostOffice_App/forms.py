from django import forms
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import (
    InvoiceItem, User, Employee, EmployeeDriver, EmployeeStaff,
    Warehouse, Vehicle, Invoice, Route, Delivery
)


# ==========================================================
#  USER FORMS
# ==========================================================

#
# These forms were previously used with Django ORM (.save()).
# They are now deprecated because:
# - USER creation/update is handled via PostgreSQL stored procedures
#   (sp_create_user, sp_update_user)
# - Validation is done using plain forms.Form instead
# - No ORM writes are allowed by project rules
#

# class CustomUserCreationForm(UserCreationForm):
#     class Meta:
#         model = User
#         fields = [
#             "username", "full_name", "email", "contact", "address",
#             "tax_id", "role", "password1", "password2"
#         ]


# class CustomUserChangeForm(UserChangeForm):
#     class Meta:
#         model = User
#         fields = [
#             "username", "full_name", "email", "contact", "address",
#             "tax_id", "role"
#         ]


USER_ROLE_CHOICES = [
    ("admin", "Admin"),
    ("client", "Client"),
    ("driver", "Driver"),
    ("staff", "Staff"),
    ("manager", "Manager"),
]


class UserForm(forms.Form):
    """
    Generic USER form.
    Used only for validation and cleaned_data.
    DB persistence is done via stored procedures.
    """

    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        help_text="Required only when creating a new user",
    )

    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)

    contact = forms.CharField(max_length=20, required=False)
    address = forms.CharField(max_length=255, required=False)

    role = forms.ChoiceField(choices=USER_ROLE_CHOICES)
    is_active = forms.BooleanField(required=False, initial=True)
# ==========================================================
#  EMPLOYEE FORMS (Driver / Staff specialization)
# ==========================================================

# ==========================================================
#  ❌ EMPLOYEE FORMS (ORM-based) — DEPRECATED
# ==========================================================
# These forms were originally implemented using Django ORM
# (ModelForm + .save()).
#
# ❌ They must NOT be used anymore because:
# - Employee, EmployeeDriver, EmployeeStaff are no longer ORM models
# - All persistence is handled by PostgreSQL stored procedures
# - Using .save() would bypass DB business rules and triggers
#
# ✅ Validation is now done with plain forms.Form
# ✅ Persistence is done via CALL sp_create_employee / sp_update_employee
#
# Kept commented for academic reference only.
# ==========================================================

# class EmployeeForm(forms.ModelForm):
#     # Expose the related user so the user assignment can be handled via the form
#     user = forms.ModelChoiceField(
#         queryset=User.objects.exclude(role__in=["admin", "client"]),
#         required=True,
#         label="User",
#     )
#
#     class Meta:
#         model = Employee
#         fields = [
#             "user", "position", "schedule", "wage",
#             "is_active", "hire_date"
#         ]
#         widgets = {
#             "hire_date": forms.DateInput(attrs={"type": "date"}),
#         }
#
#     def clean_user(self):
#         user = self.cleaned_data.get("user")
#         # Ensure the selected user does not already have an employee record
#         if user and hasattr(user, "employee") and (not self.instance.pk or user.employee.pk != self.instance.pk):
#             raise forms.ValidationError("This user is already assigned to an employee record.")
#         return user
#
#     def clean_wage(self):
#         wage = self.cleaned_data.get("wage")
#         if wage is not None and wage < 0:
#             raise forms.ValidationError("Wage must be a positive number.")
#         return wage
#
#
# class EmployeeDriverForm(forms.ModelForm):
#     class Meta:
#         model = EmployeeDriver
#         fields = [
#             "license_number", "license_category",
#             "license_expiry_date", "driving_experience_years",
#             "driver_status"
#         ]
#         widgets = {
#             "license_expiry_date": forms.DateInput(attrs={"type": "date"}),
#         }
#
#     def clean(self):
#         cleaned_data = super().clean()
#         expiry = cleaned_data.get("license_expiry_date")
#         experience = cleaned_data.get("driving_experience_years")
#         if expiry and expiry <= timezone.now().date():
#             self.add_error("license_expiry_date", "License expiry date must be in the future.")
#         if experience is not None and experience < 0:
#             self.add_error("driving_experience_years", "Driving experience must be non-negative.")
#         return cleaned_data
#
#
# class EmployeeStaffForm(forms.ModelForm):
#     class Meta:
#         model = EmployeeStaff
#         fields = [
#             "department"
#         ]













# forms.py
from django import forms

class EmployeeForm(forms.Form):
    # ---------- USER ----------
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    contact = forms.CharField(max_length=20, required=False)
    address = forms.CharField(max_length=255, required=False)

    # ---------- EMPLOYEE ----------
    war_id = forms.IntegerField()
    emp_position = forms.ChoiceField(
        choices=[
            ("driver", "Driver"),
            ("staff", "Staff"),
        ]
    )
    schedule = forms.CharField(required=False)
    wage = forms.DecimalField(required=False, min_value=0)
    hire_date = forms.DateField(required=False)
    is_active = forms.BooleanField(required=False)


class EmployeeDriverForm(forms.Form):
    license_number = forms.CharField(required=False)
    license_category = forms.ChoiceField(
        choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")],
        required=False,
    )
    license_expiry = forms.DateField(required=False)
    driving_experience = forms.IntegerField(required=False, min_value=0)
    driver_status = forms.ChoiceField(
        choices=[
            ("available", "Available"),
            ("on_duty", "On duty"),
            ("off_duty", "Off duty"),
            ("on_break", "On break"),
        ],
        required=False,
    )


class EmployeeStaffForm(forms.Form):
    department = forms.ChoiceField(
        choices=[
            ("customer_service", "Customer service"),
            ("sorting", "Sorting"),
            ("administration", "Administration"),
        ],
        required=False,
    )













# ==========================================================
#  WAREHOUSE FORM
# ==========================================================

"""
class WarehouseForm(forms.ModelForm):
    # Formulario Django para el modelo Warehouse (Almacén)
    # Proporciona una interfaz para crear/editar almacenes con validación personalizada
    
    class Meta:
        # Configuración del formulario basado en el modelo Warehouse
        model = Warehouse  # Modelo de base de datos para almacenes
        
        # Campos del modelo que se mostrarán en el formulario
        fields = [
            "name",  # Nombre del almacén (campo de texto)
            "address",  # Dirección física del almacén
            "contact",  # Información de contacto (email/teléfono)
            "po_schedule_open",  # Hora de apertura para órdenes de compra
            "po_schedule_close",  # Hora de cierre para órdenes de compra
            "maximum_storage_capacity"  # Capacidad máxima en unidades/palets
        ]
        
        # Personalización de cómo se muestran los campos en HTML
        widgets = {
            # Usa el input type="time" nativo de HTML5 para selección de hora
            "po_schedule_open": forms.TimeInput(attrs={"type": "time"}),
            "po_schedule_close": forms.TimeInput(attrs={"type": "time"}),
        }

    def clean(self):
        # Método de validación personalizado que se ejecuta automáticamente
        # Valida relaciones entre campos y reglas de negocio
        
        # Primero obtiene los datos limpios del formulario base
        cleaned_data = super().clean()
        
        # Extrae los valores de los campos relevantes para validación
        open_time = cleaned_data.get("po_schedule_open")
        close_time = cleaned_data.get("po_schedule_close")
        capacity = cleaned_data.get("maximum_storage_capacity")
        
        # Validación 1: La hora de cierre debe ser posterior a la de apertura
        # Ejemplo inválido: apertura=17:00, cierre=16:00
        # Ejemplo válido: apertura=09:00, cierre=17:00
        if open_time and close_time and close_time <= open_time:
            self.add_error(
                "po_schedule_close", 
                "Closing time must be after opening time."
            )
        
        # Validación 2: La capacidad máxima debe ser un número positivo
        # Ejemplo inválido: 0 o -100
        # Ejemplo válido: 1000
        if capacity is not None and capacity <= 0:
            self.add_error(
                "maximum_storage_capacity", 
                "Maximum storage capacity must be positive."
            )
        
        # Devuelve los datos limpios (con posibles errores añadidos)
        return cleaned_data
"""




class WarehouseForm(forms.Form):
    name = forms.CharField(max_length=100)
    address = forms.CharField(max_length=255)
    contact = forms.CharField(max_length=100, required=False)

    po_schedule_open = forms.TimeField(required=False)
    po_schedule_close = forms.TimeField(required=False)

    maximum_storage_capacity = forms.IntegerField(min_value=1)
    is_active = forms.BooleanField(required=False)

    def clean(self):
        cleaned_data = super().clean()

        open_time = cleaned_data.get("po_schedule_open")
        close_time = cleaned_data.get("po_schedule_close")
        capacity = cleaned_data.get("maximum_storage_capacity")

        if open_time and close_time and close_time <= open_time:
            self.add_error(
                "po_schedule_close",
                "Closing time must be after opening time."
            )

        if capacity is not None and capacity <= 0:
            self.add_error(
                "maximum_storage_capacity",
                "Maximum storage capacity must be positive."
            )

        return cleaned_data

# ==========================================================
#  VEHICLE FORM
# ==========================================================

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            "vehicle_type", "plate_number", "capacity",
            "brand", "model", "vehicle_status",
            "year", "fuel_type", "last_maintenance_date"
        ]
        widgets = {
            "last_maintenance_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_capacity(self):
        capacity = self.cleaned_data.get("capacity")
        if capacity is not None and capacity <= 0:
            raise forms.ValidationError("Capacity must be a positive number.")
        return capacity

    def clean_year(self):
        year = self.cleaned_data.get("year")
        if year is not None and (year < 1900 or year > 2100):
            raise forms.ValidationError("Year must be between 1900 and 2100.")
        return year


# ==========================================================
#  INVOICE FORM
# ==========================================================

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            "user", "invoice_status", "invoice_type",
            "quantity", "invoice_datetime", "cost",
            "paid", "payment_method",
            "name", "address", "contact",
        ]
        widgets = {
            "invoice_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ["shipment_type", "weight", "delivery_speed", "quantity", "unit_price", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 2}),
        }


# ==========================================================
#  ROUTE FORM
# ==========================================================

class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = [
            "description", "delivery_status",
            "delivery_date", "delivery_start_time",
            "delivery_end_time", "expected_duration",
            "kms_travelled", "driver_notes",
            "driver", "vehicle", "warehouse"
        ]
        widgets = {
            "delivery_date": forms.DateInput(attrs={"type": "date"}),
            "delivery_start_time": forms.TimeInput(attrs={"type": "time"}),
            "delivery_end_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("delivery_start_time")
        end = cleaned_data.get("delivery_end_time")
        duration = cleaned_data.get("expected_duration")
        if start and end and end <= start:
            self.add_error("delivery_end_time", "End time must be after start time.")
        if duration is not None and duration.total_seconds() <= 0:
            self.add_error("expected_duration", "Expected duration must be positive.")
        return cleaned_data


# ==========================================================
#  DELIVERY FORM
# ==========================================================

class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = [
            "invoice",
            "tracking_number", "description",

            # SENDER
            "sender_name", "sender_address",
            "sender_phone", "sender_email",

            # RECIPIENT
            "recipient_name", "recipient_address",
            "recipient_phone", "recipient_email",

            "item_type", "weight", "dimensions",

            "status", "priority",
            "updated_at",
            "in_transition",

            "delivery_date",

            "driver", "client", "route"
        ]
        widgets = {
            "updated_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "delivery_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        weight = cleaned_data.get("weight")
        if weight is not None and weight <= 0:
            self.add_error("weight", "Weight must be a positive number.")
        return cleaned_data


class VehicleImportForm(forms.Form):
    file = forms.FileField(label="Select JSON file")


class WarehouseImportForm(forms.Form):
    file = forms.FileField()


class DeliveryImportForm(forms.Form):
    file = forms.FileField()

class RouteImportForm(forms.Form):
    file = forms.FileField()