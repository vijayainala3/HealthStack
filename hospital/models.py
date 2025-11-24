from django.db import models
from accounts.models import User  # <-- Import our custom User model

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    specialty = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True)
    # --- ADD THIS LINE ---
    is_approved = models.BooleanField(default=False)
    # --- END OF ADDED LINE ---

    def __str__(self):
        approval_status = "(Approved)" if self.is_approved else "(Pending)"
        return f"Dr. {self.user.first_name} {self.user.last_name} ({self.specialty}) {approval_status}"
    
# --- ADD THIS NEW MODEL ---
class Patient(models.Model):
    # Link to the User account
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    
    # Patient-specific fields
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    # Add more fields as needed:
    # medical_history = models.TextField(blank=True)

    def __str__(self):
        return f"Patient: {self.user.first_name} {self.user.last_name} ({self.user.username})"
    
# ... (keep your User, Doctor, and Patient models) ...

# --- ADD THIS NEW MODEL ---
class Appointment(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Cancelled', 'Cancelled'),
    )

    # --- Foreign Keys ---
    # We use ForeignKey here, not OneToOne, because one patient can have MANY appointments
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    
    # --- Appointment Details ---
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    # --- Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Appointment for {self.patient.user.username} with {self.doctor.user.username} on {self.appointment_date}"

    class Meta:
        # This ensures a doctor can't be double-booked at the exact same date and time
        unique_together = ('doctor', 'appointment_date', 'appointment_time')

# --- ADD THIS NEW MODEL ---
class Prescription(models.Model):
    # --- Foreign Keys ---
    # One patient can have many prescriptions
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='prescriptions')
    
    # We can also link it to the specific appointment
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    
    # --- Prescription Details ---
    prescription_text = models.TextField(help_text="e.g., Paracetamol 500mg - 1 tablet 3 times a day for 5 days")
    date_prescribed = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for {self.patient.user.username} from {self.doctor.user.username} on {self.date_prescribed}"

# --- ADD THIS NEW MODEL ---
class LabWorker(models.Model):
    # Link to the User account
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    
    # Add lab worker specific fields (optional for now)
    department = models.CharField(max_length=100, blank=True)
    employee_id = models.CharField(max_length=50, blank=True, unique=True, null=True) 

    def __str__(self):
        return f"Lab Worker: {self.user.first_name} {self.user.last_name} ({self.user.username})"
    
class Pharmacist(models.Model):
    # Link to the User account
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    
    # Add pharmacist specific fields (optional for now)
    license_number = models.CharField(max_length=100, blank=True, unique=True, null=True)
    years_experience = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"Pharmacist: {self.user.first_name} {self.user.last_name} ({self.user.username})"
class Medicine(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    manufacturer = models.CharField(max_length=100, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per unit (e.g., tablet, bottle)")
    stock_quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.manufacturer})"

# --- ADD LAB TEST MODEL ---
class LabTest(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    # Could add fields like 'requires_fasting', 'sample_type' later

    def __str__(self):
        return self.name
    
class Invoice(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Cancelled', 'Cancelled'),
    )

    # Link to the patient being billed
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, related_name='invoices')
    # Could also link to a specific appointment if needed
    # appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)

    # Invoice Details
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    notes = models.TextField(blank=True, help_text="Details about the charges, e.g., consultation fee, lab tests.")

    def __str__(self):
        return f"Invoice #{self.id} for {self.patient.user.username} - Amount: ${self.total_amount}"

    class Meta:
        ordering = ['-issue_date'] # Show newest invoices first