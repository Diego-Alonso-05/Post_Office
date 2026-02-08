from django.urls import path

from .views import users, warehouses, employees, deliveries
# Si tienes dashboard en otro módulo, cámbialo aquí.
# Ej: from .views import dashboard

urlpatterns = [
    # ==================================================
    # AUTH (VUESTRAS VIEWS, NO DJANGO AUTH)
    # ==================================================
    path("login/", users.login_view, name="login"),
    path("logout/", users.logout_view, name="logout"),
    path("register/", users.register_view, name="register"),

    # ==================================================
    # DASHBOARD (ADMIN)
    # ==================================================
    # Puedes ponerlo en users.py o en dashboard.py, lo importante es que exista.
    path("dashboard/", users.dashboard, name="dashboard"),

    # ==================================================
    # HOME
    # ==================================================
    path("", deliveries.deliveries_list, name="home"),

    # ==================================================
    # USERS / CLIENTS
    # ==================================================
    path("users/", users.users_list, name="users_list"),

    path("clients/", users.clients_list, name="clients_list"),
    path("clients/new/", users.clients_form, name="clients_create"),
    path("clients/<int:user_id>/edit/", users.clients_form, name="clients_edit"),

    path("profile/", users.client_profile, name="client_profile"),

    # ==================================================
    # WAREHOUSES (CRUD + JSON/CSV)
    # ==================================================
    path("warehouses/", warehouses.warehouses_list, name="warehouses_list"),
    path("warehouses/new/", warehouses.warehouses_create, name="warehouses_create"),
    path("warehouses/<int:warehouse_id>/edit/", warehouses.warehouses_edit, name="warehouses_edit"),
    path("warehouses/<int:warehouse_id>/delete/", warehouses.warehouses_delete, name="warehouses_delete"),

    path("warehouses/import/json/", warehouses.warehouses_import_json, name="warehouses_import_json"),
    path("warehouses/export/json/", warehouses.warehouses_export_json, name="warehouses_export_json"),
    path("warehouses/export/csv/", warehouses.warehouses_export_csv, name="warehouses_export_csv"),

    # ==================================================
    # EMPLOYEES
    # ==================================================
    path("employees/", employees.employees_list, name="employees_list"),
    path("employees/new/", employees.employees_form, name="employees_create"),
    path("employees/<int:employee_id>/edit/", employees.employees_form, name="employees_edit"),

    # ==================================================
    # DELIVERIES (CRUD + TRACKING + JSON/CSV)
    # ==================================================
    path("deliveries/", deliveries.deliveries_list, name="deliveries_list"),
    path("deliveries/new/", deliveries.deliveries_create, name="deliveries_create"),
    path("deliveries/<int:delivery_id>/", deliveries.deliveries_detail, name="deliveries_detail"),
    path("deliveries/<int:delivery_id>/edit/", deliveries.deliveries_edit, name="deliveries_edit"),
    path("deliveries/<int:delivery_id>/status/", deliveries.deliveries_update_status, name="deliveries_update_status"),
    path("deliveries/<int:delivery_id>/delete/", deliveries.deliveries_delete, name="deliveries_delete"),

    path("tracking/<str:tracking_number>/", deliveries.deliveries_tracking, name="deliveries_tracking"),
    path("deliveries/<int:delivery_id>/tracking/", deliveries.delivery_tracking_view, name="delivery_tracking_view"),

    path("deliveries/import/json/", deliveries.deliveries_import_json, name="deliveries_import_json"),
    path("deliveries/export/json/", deliveries.deliveries_export_json, name="deliveries_export_json"),
    path("deliveries/export/csv/", deliveries.deliveries_export_csv, name="deliveries_export_csv"),
]
