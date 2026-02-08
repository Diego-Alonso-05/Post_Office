from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


# ==========================================================
#  DELIVERIES FORMS (SQL-FIRST, NO ORM)
#  Matches david_objects.sql procedures:
#   - sp_create_delivery(... p_weight INT, p_delivery_date TIMESTAMPTZ, ...)
#   - sp_update_delivery(... p_weight INT, p_delivery_date TIMESTAMPTZ, ...)
# ==========================================================

DELIVERY_STATUS_CHOICES = [
    ("registered", "Registered"),
    ("ready", "Ready"),
    ("pending", "Pending"),
    ("in_transit", "In transit"),
    ("completed", "Completed"),
    ("cancelled", "Cancelled"),
    # ("delayed", "Delayed"),  # only keep if your DB allows it (your workflow doesn't mention it)
]

DELIVERY_PRIORITY_CHOICES = [
    ("low", "Low"),
    ("normal", "Normal"),
    ("high", "High"),
    ("urgent", "Urgent"),
]


class DeliveryCreateForm(forms.Form):
    # --- FKs / references (IDs) ---
    driver_id = forms.IntegerField(required=False, min_value=1, label="Driver ID")
    route_id = forms.IntegerField(required=False, min_value=1, label="Route ID")
    inv_id = forms.IntegerField(required=False, min_value=1, label="Invoice ID")
    client_id = forms.IntegerField(required=False, min_value=1, label="Client ID")
    war_id = forms.IntegerField(required=False, min_value=1, label="Warehouse ID")

    # --- delivery basic fields ---
    tracking_number = forms.CharField(required=False, max_length=50, label="Tracking number")
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}), label="Description")

    # --- sender ---
    sender_name = forms.CharField(required=False, max_length=100, label="Sender name")
    sender_address = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}), label="Sender address")
    sender_phone = forms.CharField(required=False, max_length=20, label="Sender phone")
    sender_email = forms.EmailField(required=False, label="Sender email")

    # --- recipient ---
    recipient_name = forms.CharField(required=False, max_length=100, label="Recipient name")
    recipient_address = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}), label="Recipient address")
    recipient_phone = forms.CharField(required=False, max_length=20, label="Recipient phone")
    recipient_email = forms.EmailField(required=False, label="Recipient email")

    # --- package ---
    item_type = forms.CharField(required=False, max_length=20, label="Item type")

    # DB/SP expect INT and SP enforces >= 1 if provided
    weight = forms.IntegerField(required=False, min_value=1, label="Weight")

    dimensions = forms.CharField(required=False, max_length=50, label="Dimensions")

    # --- status / priority / dates ---
    # In DB sp_create_delivery default is 'registered' if you pass NULL
    status = forms.ChoiceField(required=False, choices=DELIVERY_STATUS_CHOICES, initial="registered", label="Status")
    priority = forms.ChoiceField(required=False, choices=DELIVERY_PRIORITY_CHOICES, initial="normal", label="Priority")

    # DB expects TIMESTAMPTZ. Your template currently uses <input type="date">,
    # so accept both date-only and datetime-local formats.
    delivery_date = forms.DateTimeField(
        required=False,
        input_formats=[
            "%Y-%m-%d",          # from <input type="date">
            "%Y-%m-%dT%H:%M",    # from <input type="datetime-local">
            "%Y-%m-%d %H:%M:%S",
        ],
        label="Delivery date",
    )


class DeliveryEditForm(forms.Form):
    # same as update SP fields (no status here)
    driver_id = forms.IntegerField(required=False, min_value=1, label="Driver ID")
    route_id = forms.IntegerField(required=False, min_value=1, label="Route ID")
    inv_id = forms.IntegerField(required=False, min_value=1, label="Invoice ID")
    client_id = forms.IntegerField(required=False, min_value=1, label="Client ID")
    war_id = forms.IntegerField(required=False, min_value=1, label="Warehouse ID")

    tracking_number = forms.CharField(required=False, max_length=50, label="Tracking number")
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}), label="Description")

    sender_name = forms.CharField(required=False, max_length=100, label="Sender name")
    sender_address = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}), label="Sender address")
    sender_phone = forms.CharField(required=False, max_length=20, label="Sender phone")
    sender_email = forms.EmailField(required=False, label="Sender email")

    recipient_name = forms.CharField(required=False, max_length=100, label="Recipient name")
    recipient_address = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}), label="Recipient address")
    recipient_phone = forms.CharField(required=False, max_length=20, label="Recipient phone")
    recipient_email = forms.EmailField(required=False, label="Recipient email")

    item_type = forms.CharField(required=False, max_length=20, label="Item type")
    weight = forms.IntegerField(required=False, min_value=1, label="Weight")
    dimensions = forms.CharField(required=False, max_length=50, label="Dimensions")

    priority = forms.ChoiceField(required=False, choices=DELIVERY_PRIORITY_CHOICES, label="Priority")
    in_transition = forms.BooleanField(required=False, label="In transition")

    delivery_date = forms.DateTimeField(
        required=False,
        input_formats=[
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%d %H:%M:%S",
        ],
        label="Delivery date",
    )


class DeliveryStatusUpdateForm(forms.Form):
    status = forms.ChoiceField(choices=DELIVERY_STATUS_CHOICES, label="Status")
    staff_id = forms.IntegerField(required=False, min_value=1, label="Staff ID")
    warehouse_id = forms.IntegerField(required=False, min_value=1, label="Warehouse ID")
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}), label="Notes")


class DeliveryImportJSONForm(forms.Form):
    file = forms.FileField(label="JSON file")
