from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('warehouses/', views.warehouses_list, name='warehouses_list'),
    path('vehicles/', views.vehicles_list, name='vehicles_list'),
    path('vehicles/create/', views.vehicles_create, name='vehicles_create'),
    path('vehicles/<int:vehicle_id>/edit/', views.vehicles_edit, name='vehicles_edit'),


    path('logout/', views.logout_view, name='logout'),
    path('mail/', views.mail_list, name='mail_list'),
    path('mail/<str:mail_id>/', views.mail_detail, name='mail_detail'),
    path('deliveries/', views.deliveries_list, name='deliveries_list'),
    path('deliveries/create/', views.deliveries_create, name='deliveries_create'),
    path('deliveries/edit/<str:delivery_id>/', views.deliveries_edit, name='deliveries_edit'),
    path('deliveries/delete/<str:delivery_id>/', views.deliveries_delete, name='deliveries_delete'),
    path("deliveries/<str:delivery_id>/", views.deliveries_detail, name="deliveries_detail"),

    path('profile/', views.client_profile, name='client_profile'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('warehouses/create/', views.warehouses_create, name='warehouses_create'),
    path('warehouses/edit/<str:warehouse_id>/', views.warehouses_edit, name='warehouses_edit'),
    path('warehouses/delete/<str:warehouse_id>/', views.warehouses_delete, name='warehouses_delete'),
    path('profile/', views.client_profile, name='client_profile'),

    path('invoices/', views.invoice_list, name='invoice_list'),


]