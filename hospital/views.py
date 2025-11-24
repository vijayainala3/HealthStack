import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.models import User  # Import the User model 
from .models import Doctor, Patient, Appointment, Prescription, LabWorker, Medicine, LabTest, Invoice, Pharmacist  # Import models
from django.contrib.auth.decorators import login_required
from .decorators import admin_required
from django.db.models import Count


@login_required(login_url='login')
@admin_required 
def add_doctor_view(request):
    # (We should also add a check here to ensure user is an Admin)
    if request.method == 'POST':
        # Get all the data from the form
        username = request.POST.get('username')
        pass_word = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        
        specialty = request.POST.get('specialty')
        phone = request.POST.get('phone_number')

        try:
            # 1. Create the User object
            user = User.objects.create_user(
                username=username,
                password=pass_word,
                first_name=first_name,
                last_name=last_name,
                email=email,
                role='DOCTOR'  # Set the role to DOCTOR
            )
            
            # 2. Create the Doctor object linked to the user
            Doctor.objects.create(
                user=user,
                specialty=specialty,
                phone_number=phone
            )
            
            messages.success(request, f'Doctor account created for {username}!')
            return redirect('admin_dashboard') # Redirect to admin dashboard on success

        except Exception as e:
            messages.error(request, f'Error creating account: {e}')
            return redirect('add_doctor')

    # If it's a GET request, just show the form
    return render(request, 'add_doctor.html')


@login_required(login_url='login') # <-- SECURITY FIX
def doctor_list_view(request):
    # Fetch all objects from the Doctor model
    doctors = Doctor.objects.all()
    
    # Pass the list of doctors to the template
    context = {
        'doctors': doctors
    }
    return render(request, 'doctor_list.html', context)


@login_required(login_url='login') # <-- SECURITY FIX
def delete_doctor_view(request, pk):
    try:
        # Find the Doctor object by its primary key (pk)
        user = User.objects.get(pk=pk)
        
        # Check if the user is actually a Doctor before deleting
        if user.role == 'DOCTOR':
            user.delete()
            messages.success(request, f'Doctor {user.username} has been deleted.')
        else:
            messages.error(request, 'This user is not a doctor.')
            
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
    except Exception as e:
        messages.error(request, f'An error occurred: {e}')
    
    # Send the admin back to the doctor list
    return redirect('doctor_list')


@login_required(login_url='login') # <-- SECURITY FIX
def edit_doctor_view(request, pk):
    try:
        # Get the Doctor object we want to edit
        doctor = Doctor.objects.get(user__pk=pk)
        # Get the linked User object
        user = doctor.user 
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor not found.')
        return redirect('doctor_list')
    except Exception as e:
        messages.error(request, f'An error occurred: {e}')
        return redirect('doctor_list')

    # Now, check if the form was submitted
    if request.method == 'POST':
        # Get the data from the form
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        specialty = request.POST.get('specialty')
        phone = request.POST.get('phone_number')

        try:
            # --- Save the changes ---
            # 1. Update the User model
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()

            # 2. Update the Doctor model
            doctor.specialty = specialty
            doctor.phone_number = phone
            doctor.save()

            messages.success(request, f'Doctor {user.username} updated successfully!')
            return redirect('doctor_list') # Go back to the list
        except Exception as e:
            messages.error(request, f'Error updating account: {e}')
            # We'll fall through and re-render the form with the error

    # This context will be used for both GET and POST (on error)
    context = {
        'doctor': doctor
    }
    
    # If it's a GET request (or a POST that failed), show the pre-filled form
    return render(request, 'edit_doctor.html', context)


# --- This is the view with the BUG FIX ---
@login_required(login_url='login')
def book_appointment_view(request):
    # We need the Patient object for the logged-in user
    try:
        patient = request.user.patient
    except Patient.DoesNotExist:
        messages.error(request, 'You must be a patient to book an appointment.')
        return redirect('home') # Send them home if they're not a patient

    if request.method == 'POST':
        # Get data from the form
        doctor_id = request.POST.get('doctor')
        app_date = request.POST.get('appointment_date')
        app_time = request.POST.get('appointment_time')
        reason = request.POST.get('reason')
        
        doctor = None # Initialize doctor variable

        try:
            # Get the Doctor object from the ID
            doctor_user = User.objects.get(pk=doctor_id)
            doctor = doctor_user.doctor
            
            # Create the appointment
            Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                appointment_date=app_date,
                appointment_time=app_time,
                reason=reason,
                status='Pending' # Default status
            )
            
            messages.success(request, 'Your appointment has been booked and is pending approval.')
            return redirect('home') # Or redirect to an 'my_appointments' page later
            
        except User.DoesNotExist:
            messages.error(request, 'Selected doctor does not exist.')
        except Doctor.DoesNotExist:
            messages.error(request, 'Selected user is not a doctor.')
        except Exception as e:
            # This will catch the 'unique_together' error if the slot is taken
            if 'UNIQUE constraint' in str(e):
                doc_name = "the selected doctor"
                if doctor: # Check if doctor object was successfully fetched
                    doc_name = f"Dr. {doctor.user.username}"
                messages.error(request, f'This time slot with {doc_name} is already taken.')
            else:
                messages.error(request, f'An error occurred: {e}')

    # --- This is for the GET request (or if POST fails) ---
    # Fetch all doctors to show in the dropdown
    doctors = Doctor.objects.all()
    
    context = {
        'doctors': doctors
    }
    return render(request, 'booking.html', context)

@login_required(login_url='login')
def approve_appointment_view(request, pk):
    try:
        # Get the specific appointment by its ID (pk)
        appointment = Appointment.objects.get(pk=pk)
        
        # Check if the logged-in user is the correct doctor
        if request.user == appointment.doctor.user:
            appointment.status = 'Approved'
            appointment.save()
            messages.success(request, f'Appointment for {appointment.patient.user.username} approved.')
        else:
            messages.error(request, 'You are not authorized to approve this appointment.')
            
    except Appointment.DoesNotExist:
        messages.error(request, 'Appointment not found.')
    except Exception as e:
        messages.error(request, f'An error occurred: {e}')
        
    return redirect('doctor_dashboard')


@login_required(login_url='login')
def reject_appointment_view(request, pk):
    try:
        appointment = Appointment.objects.get(pk=pk)
        
        # Check if the logged-in user is the correct doctor
        if request.user == appointment.doctor.user:
            # You could also delete it: appointment.delete()
            # But changing status to 'Cancelled' is better for record-keeping
            appointment.status = 'Cancelled' 
            appointment.save()
            messages.success(request, f'Appointment for {appointment.patient.user.username} cancelled.')
        else:
            messages.error(request, 'You are not authorized to reject this appointment.')
            
    except Appointment.DoesNotExist:
        messages.error(request, 'Appointment not found.')
    except Exception as e:
        messages.error(request, f'An error occurred: {e}')
        
    return redirect('doctor_dashboard')

# --- ADD THIS NEW VIEW FOR PATIENTS ---
@login_required(login_url='login')
def patient_appointments_view(request):
    try:
        # Get the Patient object for the logged-in user
        patient = request.user.patient
    except Patient.DoesNotExist:
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('home')

    # Get all appointments for this patient, ordered by date
    appointments = Appointment.objects.filter(patient=patient).order_by('appointment_date', 'appointment_time')

    context = {
        'appointments': appointments,
    }
    return render(request, 'my_appointments.html', context)

# --- ADD THIS NEW VIEW ---
@login_required(login_url='login')
def create_prescription_view(request, appt_pk):
    try:
        # Get the appointment this prescription is for
        appointment = Appointment.objects.get(pk=appt_pk)
        
        # Security check: Ensure the logged-in user is the correct doctor
        if request.user != appointment.doctor.user:
            messages.error(request, 'You are not authorized to write this prescription.')
            return redirect('doctor_dashboard')
            
    except Appointment.DoesNotExist:
        messages.error(request, 'Appointment not found.')
        return redirect('doctor_dashboard')

    if request.method == 'POST':
        prescription_text = request.POST.get('prescription_text')
        
        if not prescription_text:
            messages.error(request, 'Prescription cannot be empty.')
        else:
            try:
                # Create the new prescription
                Prescription.objects.create(
                    patient=appointment.patient,
                    doctor=appointment.doctor,
                    appointment=appointment,
                    prescription_text=prescription_text
                )
                messages.success(request, 'Prescription saved successfully.')
                return redirect('doctor_dashboard') # Go back to the dashboard
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')
    
    # For a GET request, pass the appointment details to the template
    context = {
        'appointment': appointment
    }
    return render(request, 'create_prescription.html', context)

# --- ADD THIS NEW VIEW FOR PATIENTS ---
@login_required(login_url='login')
def my_prescriptions_view(request):
    try:
        # Get the Patient object for the logged-in user
        patient = request.user.patient
    except Patient.DoesNotExist:
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('home')

    # Get all prescriptions for this patient, ordered by date
    prescriptions = Prescription.objects.filter(patient=patient).order_by('-date_prescribed')

    context = {
        'prescriptions': prescriptions,
    }
    return render(request, 'my_prescriptions.html', context)

@login_required(login_url='login')
def pending_doctors_view(request):
    # Security Check: Only allow ADMINs to view this page
    if request.user.role != 'ADMIN':
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('home')

    # Fetch all Doctor profiles where is_approved is False
    pending_doctors = Doctor.objects.filter(is_approved=False)

    context = {
        'pending_doctors': pending_doctors
    }
    return render(request, 'pending_doctors.html', context)

# hospital/views.py
# ... (at the bottom of the file) ...

# --- ADD APPROVE VIEW ---
@login_required(login_url='login')
def approve_doctor_view(request, pk):
    if request.user.role != 'ADMIN':
        messages.error(request, 'Access denied.')
        return redirect('home')

    doctor = get_object_or_404(Doctor, user__pk=pk)
    doctor.is_approved = True
    doctor.save()

    messages.success(request, f'Doctor {doctor.user.username} has been approved.')
    return redirect('pending_doctors')


# --- ADD REJECT VIEW ---
@login_required(login_url='login')
def reject_doctor_view(request, pk):
    if request.user.role != 'ADMIN':
        messages.error(request, 'Access denied.')
        return redirect('home')

    # Rejection usually means deleting the user/profile
    user_to_delete = get_object_or_404(User, pk=pk)
    username = user_to_delete.username # Save name for message
    user_to_delete.delete()

    messages.success(request, f'Doctor application for {username} has been rejected and removed.')
    return redirect('pending_doctors')

@login_required(login_url='login')
@admin_required # Only Admins can add Lab Workers
def add_lab_worker_view(request):
    if request.method == 'POST':
        # Get data from the form
        username = request.POST.get('username')
        pass_word = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        department = request.POST.get('department') # LabWorker field
        employee_id = request.POST.get('employee_id') # LabWorker field

        # Check if username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken.')
            return redirect('add_lab_worker')

        try:
            # 1. Create the User object with LABWORKER role
            user = User.objects.create_user(
                username=username,
                password=pass_word,
                first_name=first_name,
                last_name=last_name,
                email=email,
                role='LABWORKER' # Set the role
            )
            
            # 2. Create the linked LabWorker profile
            LabWorker.objects.create(
                user=user,
                department=department,
                employee_id=employee_id
            )
            
            messages.success(request, f'Lab Worker account created for {username}!')
            return redirect('admin_dashboard') # Redirect back to admin dashboard

        except Exception as e:
            messages.error(request, f'Error creating account: {e}')
            # Stay on the same page to show the error
            return redirect('add_lab_worker')

    # If it's a GET request, just show the blank form
    return render(request, 'add_lab_worker.html')

@login_required(login_url='login')
@admin_required # Only Admins can add Pharmacists
def add_pharmacist_view(request):
    if request.method == 'POST':
        # Get data from the form
        username = request.POST.get('username')
        pass_word = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        license_number = request.POST.get('license_number') # Pharmacist field
        years_experience = request.POST.get('years_experience') # Pharmacist field

        # Check if username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken.')
            return redirect('add_pharmacist')

        try:
            # 1. Create the User object with PHARMACIST role
            user = User.objects.create_user(
                username=username,
                password=pass_word,
                first_name=first_name,
                last_name=last_name,
                email=email,
                role='PHARMACIST' # Set the role
            )

            # 2. Create the linked Pharmacist profile
            Pharmacist.objects.create(
                user=user,
                license_number=license_number,
                # Safely convert years_experience to integer
                years_experience=int(years_experience) if years_experience else None
            )

            messages.success(request, f'Pharmacist account created for {username}!')
            return redirect('admin_dashboard') # Redirect back to admin dashboard

        except ValueError: # Catch error if years_experience isn't a number
            messages.error(request, 'Years of experience must be a whole number.')
            return redirect('add_pharmacist')
        except Exception as e:
            messages.error(request, f'Error creating account: {e}')
            # Stay on the same page to show the error
            return redirect('add_pharmacist')

    # If it's a GET request, just show the blank form
    return render(request, 'add_pharmacist.html')

@login_required(login_url='login')
@admin_required
def add_medicine_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        manufacturer = request.POST.get('manufacturer')
        unit_price = request.POST.get('unit_price')
        stock_quantity = request.POST.get('stock_quantity')

        try:
            Medicine.objects.create(
                name=name, description=description, manufacturer=manufacturer,
                unit_price=unit_price, stock_quantity=stock_quantity
            )
            messages.success(request, f'Medicine "{name}" added successfully.')
            return redirect('medicine_list') # Redirect to the list view
        except Exception as e:
            messages.error(request, f'Error adding medicine: {e}')
            # Stay on the form page if error
            return render(request, 'add_medicine.html')

    return render(request, 'add_medicine.html')

@login_required(login_url='login')
@admin_required
def medicine_list_view(request):
    medicines = Medicine.objects.all().order_by('name')
    context = {'medicines': medicines}
    return render(request, 'medicine_list.html', context)

# --- LAB TEST VIEWS ---

@login_required(login_url='login')
@admin_required
def add_lab_test_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        cost = request.POST.get('cost')

        try:
            LabTest.objects.create(
                name=name, description=description, cost=cost
            )
            messages.success(request, f'Lab Test "{name}" added successfully.')
            return redirect('lab_test_list') # Redirect to the list view
        except Exception as e:
            messages.error(request, f'Error adding lab test: {e}')
            return render(request, 'add_lab_test.html')

    return render(request, 'add_lab_test.html')

@login_required(login_url='login')
@admin_required
def lab_test_list_view(request):
    lab_tests = LabTest.objects.all().order_by('name')
    context = {'lab_tests': lab_tests}
    return render(request, 'lab_test_list.html', context)

@login_required(login_url='login')
@admin_required
def create_invoice_view(request):
    # Get all patients to populate the dropdown
    patients = Patient.objects.all()

    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        due_date_str = request.POST.get('due_date')
        total_amount = request.POST.get('total_amount')
        notes = request.POST.get('notes')

        try:
            patient = Patient.objects.get(user_id=patient_id) # Find patient by user ID
            
            # Convert due date string to date object (optional)
            due_date = datetime.datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None

            Invoice.objects.create(
                patient=patient,
                due_date=due_date,
                total_amount=total_amount,
                notes=notes,
                status='Pending' # Default status
            )
            messages.success(request, f'Invoice created successfully for patient {patient.user.username}.')
            return redirect('admin_dashboard') # Or redirect to an invoice list page later

        except Patient.DoesNotExist:
            messages.error(request, 'Selected patient not found.')
        except ValueError:
            messages.error(request, 'Invalid date format for due date. Please use YYYY-MM-DD.')
        except Exception as e:
            messages.error(request, f'Error creating invoice: {e}')
            # Stay on the form page if error, passing patients back
            return render(request, 'create_invoice.html', {'patients': patients})

    # If GET request, just show the blank form with patients
    context = {'patients': patients}
    return render(request, 'create_invoice.html', context)

@login_required(login_url='login')
@admin_required
def invoice_list_view(request):
    invoices = Invoice.objects.all().select_related('patient__user').order_by('-issue_date') # Optimize
    context = {'invoices': invoices}
    return render(request, 'invoice_list.html', context)

@login_required(login_url='login')
@admin_required
def patient_list_view(request):
    patients = Patient.objects.all().select_related('user').order_by('user__last_name', 'user__first_name') # Optimize
    context = {'patients': patients}
    return render(request, 'patient_list.html', context)

@login_required(login_url='login')
@admin_required
def appointment_report_view(request):
    # --- Basic Report Logic: Count appointments by status ---
    
    # Use annotation to count appointments grouped by status
    status_counts = Appointment.objects.values('status').annotate(count=Count('status')).order_by('status')
    
    # Convert the queryset result into a more usable dictionary
    report_data = {item['status']: item['count'] for item in status_counts}
    
    # Get total count as well
    total_appointments = Appointment.objects.count()

    context = {
        'report_data': report_data,
        'total_appointments': total_appointments,
        # We can add date filters later
    }
    return render(request, 'report_appointment_summary.html', context)