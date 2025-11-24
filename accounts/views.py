# accounts/views.py

# --- Core Django Imports ---
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm 

# --- Date/Time Import ---
import datetime 

# --- Model Imports ---
from .models import User
# Make sure ALL relevant profile models are imported
from hospital.models import Patient, Doctor, Appointment, LabWorker, Pharmacist # <-- ADDED Pharmacist
from pharmacy.models import Order 
from chat.models import Conversation, Message 

# ==========================================================
# VIEWS START HERE
# ==========================================================

def home_view(request):
    """Renders the generic homepage, redirecting logged-in users."""
    if request.user.is_authenticated:
        if request.user.role == 'ADMIN':
            return redirect('admin_dashboard')
        elif request.user.role == 'DOCTOR':
            return redirect('doctor_dashboard')
        elif request.user.role == 'LABWORKER':
            return redirect('labworker_dashboard')
        # === ADDED PHARMACIST REDIRECT ===
        elif request.user.role == 'PHARMACIST':
            return redirect('pharmacist_dashboard')
        # === END ===
        elif request.user.role == 'PATIENT':
            return redirect('patient_dashboard')
    # If not authenticated or role unknown (shouldn't happen), show generic home
    return render(request, 'home.html') 

# --- Authentication Views ---

def login_view(request):
    """Handles user login, role-based redirects, and doctor approval checks."""
    if request.method == 'POST':
        username = request.POST.get('username')
        pass_word = request.POST.get('password')
        user = authenticate(request, username=username, password=pass_word)

        if user is not None:
            # Check Approval Status for Doctors
            if user.role == 'DOCTOR':
                try:
                    doctor_profile = user.doctor
                    if not doctor_profile.is_approved:
                        logout(request) 
                        messages.error(request, 'Your Doctor account is pending admin approval.')
                        return redirect('login')
                except Doctor.DoesNotExist:
                    logout(request)
                    messages.error(request, 'Doctor profile not found. Please contact admin.')
                    return redirect('login')
            
            # Log in and Redirect based on role
            login(request, user)
            
            if user.role == 'ADMIN':
                return redirect('admin_dashboard')
            elif user.role == 'DOCTOR':
                 return redirect('doctor_dashboard')
            elif user.role == 'LABWORKER':
                 # Message moved to dashboard
                 return redirect('labworker_dashboard')
            # === ADDED PHARMACIST REDIRECT ===
            elif user.role == 'PHARMACIST':
                 messages.success(request, f'Welcome, Pharmacist {user.username}!')
                 return redirect('pharmacist_dashboard')
            # === END ===
            else: # PATIENT (Default if role doesn't match others)
                 return redirect('patient_dashboard')

        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'login.html') 

    return render(request, 'login.html')

def logout_view(request):
    """Logs the user out."""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login') 

# --- Registration Views ---

def register_view(request):
    """Handles patient registration."""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        pass_word = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken. Please choose a different one.')
            return redirect('register')

        try:
            user = User.objects.create_user(
                username=username, password=pass_word, first_name=first_name,
                last_name=last_name, email=email, role='PATIENT'
            )
            Patient.objects.create(user=user) 
            messages.success(request, f'Account created successfully for {username}! Please log in.')
            return redirect('login')

        except Exception as e:
            messages.error(request, f'Error creating account: {e}')
            return redirect('register')

    return render(request, 'register.html')

def doctor_register_view(request):
    """Handles doctor registration (requires admin approval)."""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        pass_word = request.POST.get('password')
        specialty = request.POST.get('specialty') 
        phone = request.POST.get('phone_number') 

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken.')
            return redirect('doctor_register')

        try:
            user = User.objects.create_user(
                username=username, password=pass_word, first_name=first_name,
                last_name=last_name, email=email, role='DOCTOR'
            )
            Doctor.objects.create(
                user=user, specialty=specialty, phone_number=phone, is_approved=False 
            )
            messages.success(request, f'Registration successful, Dr. {username}! Your account is pending admin approval.')
            return redirect('login') 

        except Exception as e:
            messages.error(request, f'Error creating account: {e}')
            return redirect('doctor_register')

    return render(request, 'doctor_register.html')

# --- Dashboard Views ---

@login_required(login_url='login')
def admin_dashboard_view(request):
    """Displays the admin dashboard with system metrics."""
    if request.user.role != 'ADMIN':
        messages.error(request, 'Access denied.')
        return redirect('home')

    total_conversations = Conversation.objects.count()
    context = {'total_conversations': total_conversations}
    return render(request, 'admin_dashboard.html', context)

@login_required(login_url='login')
def doctor_dashboard_view(request):
    """Displays the doctor dashboard with appointments and message count."""
    try:
        doctor = request.user.doctor
    except (Doctor.DoesNotExist, AttributeError): 
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('home')

    # Chat Count Logic
    doctor_conversations = Conversation.objects.filter(participants=request.user)
    unread_message_count = Message.objects.filter(
        conversation__in=doctor_conversations
    ).exclude(sender=request.user).count() 

    # Appointment Logic
    pending_appointments = Appointment.objects.filter(
        doctor=doctor, status='Pending'
    ).order_by('appointment_date', 'appointment_time')
    
    approved_appointments = Appointment.objects.filter(
        doctor=doctor, status='Approved'
    ).order_by('appointment_date', 'appointment_time')

    context = {
        'pending_appointments': pending_appointments,
        'approved_appointments': approved_appointments,
        'pending_count': pending_appointments.count(),
        'unread_message_count': unread_message_count, 
    }
    return render(request, 'doctor_dashboard.html', context)

@login_required(login_url='login')
def patient_dashboard_view(request):
    """Displays the patient dashboard with appointments and orders."""
    if request.user.role != 'PATIENT':
        messages.error(request, 'Access denied.')
        if request.user.role == 'ADMIN': return redirect('admin_dashboard')
        if request.user.role == 'DOCTOR': return redirect('doctor_dashboard')
        if request.user.role == 'LABWORKER': return redirect('labworker_dashboard') # Added LabWorker redirect
        if request.user.role == 'PHARMACIST': return redirect('pharmacist_dashboard') # Added Pharmacist redirect
        return redirect('home') 

    try:
        patient = request.user.patient
    except Patient.DoesNotExist:
        patient = Patient.objects.create(user=request.user) 

    today = datetime.date.today() 

    upcoming_appointments = Appointment.objects.filter(
        patient=patient,
        status='Approved',
        appointment_date__gte=today 
    ).order_by('appointment_date', 'appointment_time')[:3]

    recent_orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')[:3]

    context = {
        'upcoming_appointments': upcoming_appointments,
        'recent_orders': recent_orders,
    }
    return render(request, 'patient_dashboard.html', context)

# --- Profile Management Views ---

@login_required(login_url='login')
def profile_view(request):
    """Allows patients to view and edit their profile."""
    if request.user.role != 'PATIENT':
         messages.error(request, 'Only patients can edit profiles here.')
         return redirect('home') 

    try:
        patient = request.user.patient 
    except Patient.DoesNotExist:
        patient = Patient.objects.create(user=request.user)
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone_number')
        blood_group = request.POST.get('blood_group')
        dob_str = request.POST.get('date_of_birth') 
        address = request.POST.get('address')
        
        try:
            # Update User
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.email = email
            request.user.save()
            
            # Update Patient
            patient.phone_number = phone
            patient.blood_group = blood_group
            patient.date_of_birth = datetime.datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None
            patient.address = address
            patient.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
            
        except ValueError: 
             messages.error(request, 'Invalid date format. Please use YYYY-MM-DD.')
        except Exception as e:
            messages.error(request, f'Error updating profile: {e}')
            
    context = {'patient': patient}
    return render(request, 'profile.html', context)

@login_required(login_url='login')
def change_password_view(request):
    """Allows logged-in users to change their password."""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save() 
            update_session_auth_hash(request, user) 
            messages.success(request, 'Your password was successfully updated!')
            # Redirect based on role
            if request.user.role == 'PATIENT': return redirect('patient_dashboard')
            if request.user.role == 'DOCTOR': return redirect('doctor_dashboard')
            if request.user.role == 'ADMIN': return redirect('admin_dashboard')
            if request.user.role == 'LABWORKER': return redirect('labworker_dashboard') # Added LabWorker redirect
            if request.user.role == 'PHARMACIST': return redirect('pharmacist_dashboard') # Added Pharmacist redirect
            return redirect('home') 
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = PasswordChangeForm(request.user)
        
    return render(request, 'change_password.html', {'form': form})


# --- Lab Worker Dashboard View ---
@login_required(login_url='login')
def labworker_dashboard_view(request):
    """Displays the lab worker dashboard."""
    if request.user.role != 'LABWORKER':
        messages.error(request, 'Access denied.')
        if request.user.role == 'ADMIN': return redirect('admin_dashboard')
        if request.user.role == 'DOCTOR': return redirect('doctor_dashboard')
        if request.user.role == 'PATIENT': return redirect('patient_dashboard')
        if request.user.role == 'PHARMACIST': return redirect('pharmacist_dashboard') # Added Pharmacist redirect
        return redirect('home') 

    context = {}
    return render(request, 'labworker_dashboard.html', context)

# --- Pharmacist Dashboard View ---
@login_required(login_url='login')
def pharmacist_dashboard_view(request):
    """Displays the pharmacist dashboard."""
    if request.user.role != 'PHARMACIST':
        messages.error(request, 'Access denied.')
        if request.user.role == 'ADMIN': return redirect('admin_dashboard')
        if request.user.role == 'DOCTOR': return redirect('doctor_dashboard')
        if request.user.role == 'PATIENT': return redirect('patient_dashboard')
        if request.user.role == 'LABWORKER': return redirect('labworker_dashboard') # Added LabWorker redirect
        return redirect('home') 

    context = {}
    return render(request, 'pharmacist_dashboard.html', context)