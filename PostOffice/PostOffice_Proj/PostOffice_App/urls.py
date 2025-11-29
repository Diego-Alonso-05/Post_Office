"""URL configuration for the Post Office application.

This module maps URL patterns to view functions in ``views.py``.  All IDs
have been updated to use integer types (``<int:...>``) to match the
primary keys of the PostgreSQL models.  Duplicate and unused patterns
from the MongoDB era have been removed.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Dashboard/home
    path("", views.dashboard, name="dashboard"),

    # Authentication
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),

    # User profile
    path("profile/", views.client_profile, name="client_profile"),

    # Warehouses
    path("warehouses/", views.warehouses_list, name="warehouses_list"),
    path("warehouses/export/json/", views.warehouses_export_json, name="warehouses_export_json"),
    path("warehouses/import/json/", views.warehouses_import_json, name="warehouses_import_json"),
    path("warehouses/create/", views.warehouses_create, name="warehouses_create"),
    path("warehouses/<int:warehouse_id>/edit/", views.warehouses_edit, name="warehouses_edit"),
    path("warehouses/<int:warehouse_id>/delete/", views.warehouses_delete, name="warehouses_delete"),

    # Vehicles
    path("vehicles/", views.vehicles_list, name="vehicles_list"),
    path("vehicles/export/json/", views.vehicles_export_json, name="vehicles_export_json"),
    path("vehicles/import/json/", views.vehicles_import_json, name="vehicles_import_json"),

    path("vehicles/create/", views.vehicles_create, name="vehicles_create"),
    path("vehicles/<int:vehicle_id>/edit/", views.vehicles_edit, name="vehicles_edit"),
    path("vehicles/<int:vehicle_id>/delete/", views.vehicles_delete, name="vehicles_delete"),

    # Routes
    path("routes/", views.routes_list, name="routes_list"),
    path("routes/create/", views.routes_create, name="routes_create"),
    path("routes/import/json/", views.routes_import_json, name="routes_import_json"),
    path("routes/export/json/", views.routes_export_json, name="routes_export_json"),
    path("routes/<int:route_id>/edit/", views.routes_edit, name="routes_edit"),
    path("routes/<int:route_id>/delete/", views.routes_delete, name="routes_delete"),

    # Deliveries
    path("deliveries/", views.deliveries_list, name="deliveries_list"),
    path("deliveries/export/json/", views.deliveries_export_json, name="deliveries_export_json"),
    path("deliveries/import/json/", views.deliveries_import_json, name="deliveries_import_json"),
    path("deliveries/create/", views.deliveries_create, name="deliveries_create"),
    path("deliveries/<int:delivery_id>/", views.deliveries_detail, name="deliveries_detail"),
    path("deliveries/<int:delivery_id>/edit/", views.deliveries_edit, name="deliveries_edit"),
    path("deliveries/<int:delivery_id>/delete/", views.deliveries_delete, name="deliveries_delete"),

    # Invoices
    path("invoices/", views.invoice_list, name="invoice_list"),
    path("invoices/export/json/", views.invoices_export_json, name="invoices_export_json"),
    path("invoices/create/", views.invoice_form, name="invoice_create"),
    path("invoices/<int:invoice_id>/edit/", views.invoice_form, name="invoice_edit"),


    # CSV export views (PostgreSQL functions)
    path("vehicles/export/csv/", views.vehicles_export_csv, name="vehicles_export_csv"),
    path("warehouses/export/csv/", views.warehouses_export_csv, name="warehouses_export_csv"),
    path("deliveries/export/csv/", views.deliveries_export_csv, name="deliveries_export_csv"),
    path("routes/export/csv/", views.routes_export_csv, name="routes_export_csv"),
    path("invoices/export/csv/", views.invoices_export_csv, name="invoices_export_csv"),

]
