from django.urls import path
from . import views

urlpatterns = [
    path('add-doctor/', views.add_doctor_view, name='add_doctor'),
    path('doctor-list/', views.doctor_list_view, name='doctor_list'),
    path('delete-doctor/<int:pk>/', views.delete_doctor_view, name='delete_doctor'),
    path('edit-doctor/<int:pk>/', views.edit_doctor_view, name='edit_doctor'),
    path('book-appointment/', views.book_appointment_view, name='book_appointment'),
    path('approve-appointment/<int:pk>/', views.approve_appointment_view, name='approve_appointment'),
    path('reject-appointment/<int:pk>/', views.reject_appointment_view, name='reject_appointment'),
    path('my-appointments/', views.patient_appointments_view, name='my_appointments'),
    path('create-prescription/<int:appt_pk>/', views.create_prescription_view, name='create_prescription'),
    path('my-prescriptions/', views.my_prescriptions_view, name='my_prescriptions'),
    path('admin/pending-doctors/', views.pending_doctors_view, name='pending_doctors'),
    path('admin/approve-doctor/<int:pk>/', views.approve_doctor_view, name='approve_doctor'),
    path('admin/reject-doctor/<int:pk>/', views.reject_doctor_view, name='reject_doctor'),
    path('admin/add-lab-worker/', views.add_lab_worker_view, name='add_lab_worker'),
    path('admin/add-pharmacist/', views.add_pharmacist_view, name='add_pharmacist'),
    path('admin/medicines/', views.medicine_list_view, name='medicine_list'),
    path('admin/medicines/add/', views.add_medicine_view, name='add_medicine'),
    path('admin/lab-tests/', views.lab_test_list_view, name='lab_test_list'),
    path('admin/lab-tests/add/', views.add_lab_test_view, name='add_lab_test'),
    path('admin/create-invoice/', views.create_invoice_view, name='create_invoice'),
    path('admin/invoices/', views.invoice_list_view, name='invoice_list'),
    path('admin/patients/', views.patient_list_view, name='patient_list'),
    path('admin/reports/appointments/', views.appointment_report_view, name='report_appointments'),
]
