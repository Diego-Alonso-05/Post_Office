from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),

    path("warehouses/", views.warehouses_list, name="warehouses-list"),
    path("vehicles/", views.vehicles_list, name="vehicles-list"),
    path("mail/", views.mail_list, name="mail-list"),
    path("mail/detail/", views.mail_detail, name="mail-detail"),
    path("deliveries/", views.deliveries_list, name="deliveries-list"),
    path("invoices/", views.invoices_list, name="invoices-list"),
    path("profile/", views.client_profile, name="client-profile"),
]
