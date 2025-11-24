from django.contrib import admin
from .models import Doctor, Patient, Appointment, Prescription, LabWorker, Pharmacist, Medicine, LabTest, Invoice

# Register your models here.
admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Appointment)
admin.site.register(Prescription)
admin.site.register(LabWorker)
admin.site.register(Pharmacist)
admin.site.register(Medicine) # <-- ADD THIS LINE
admin.site.register(LabTest)
admin.site.register(Invoice)