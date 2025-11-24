from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'), # <-- ADD THIS LINE
    path('register/', views.register_view, name='register'),
    path('dashboard/admin/', views.admin_dashboard_view, name='admin_dashboard'),
    path('dashboard/doctor/', views.doctor_dashboard_view, name='doctor_dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('register/doctor/', views.doctor_register_view, name='doctor_register'),
    path('dashboard/patient/', views.patient_dashboard_view, name='patient_dashboard'),
    path('dashboard/labworker/', views.labworker_dashboard_view, name='labworker_dashboard'),
    path('dashboard/pharmacist/', views.pharmacist_dashboard_view, name='pharmacist_dashboard'),
    path('dashboard/admin/', views.admin_dashboard_view, name='admin_dashboard'),
]