from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # These are the different roles a user can have
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('DOCTOR', 'Doctor'),
        ('PATIENT', 'Patient'),
        ('PHARMACIST', 'Pharmacist'),
        ('LABWORKER', 'Lab Worker'),
    )
    
    # We add a 'role' field to the default User
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='PATIENT')

    # You could add other fields here common to all users, like:
    # profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    # phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"