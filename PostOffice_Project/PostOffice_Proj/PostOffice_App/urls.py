from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('warehouses/', views.warehouses_list, name='warehouses_list'),
    path('vehicles/', views.vehicles_list, name='vehicles_list'),

    path('vehicles/create/', views.vehicles_create, name='vehicles_create'),
    path('vehicles/edit/<str:vehicle_id>/', views.vehicles_edit, name='vehicles_edit'),
    path('logout/', views.logout_view, name='logout'),
    path('mail/', views.mail_list, name='mail_list'),
    path('mail/<str:mail_id>/', views.mail_detail, name='mail_detail'),
    path('deliveries/', views.deliveries_list, name='deliveries_list'),
    path('profile/', views.client_profile, name='client_profile'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
]