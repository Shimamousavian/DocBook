from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from .models import Doctor, Appointment, Notification, Schedule, Patient
from .serializers import AppointmentSerializer, DoctorSerializer, ReviewSerializer
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.contrib import messages
from .forms import UserRegistrationForm


def index(request):
    return render(request, 'booking/index.html')

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Doctor, Patient, Appointment

def user_registration(request):
    """Handles user registration for doctors and patients."""
    if request.method == 'POST':
        # Extract form data
        user_type = request.POST.get('user_type')  # "doctor" or "patient"
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        # Validation: Check if username is already taken
        if User.objects.filter(username=username).exists():
            messages.error(request, 'This username is already taken!')
            return render(request, 'booking/register.html', {'user_type': user_type})

        # Validation: Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords don't match!")
            return render(request, 'booking/register.html', {'user_type': user_type})

        # Create user
        user = User.objects.create_user(username=username, password=password)

        # Create doctor or patient profile based on user_type
        if user_type == 'doctor':
            specialization = request.POST.get('specialization', '').strip()
            if not specialization:
                messages.error(request, 'Specialization is required for doctors!')
                user.delete()  # Rollback user creation
                return render(request, 'booking/register.html', {'user_type': user_type})
            Doctor.objects.create(user=user, specialization=specialization)

        elif user_type == 'patient':
            medical_history = request.POST.get('medical_history', '').strip()
            Patient.objects.create(user=user, medical_history=medical_history)

        # Success message and redirect
        messages.success(request, 'Your account has been created successfully!')
        return redirect('login')

    return render(request, 'booking/register.html')


def login_view(request):
    """Handles user login."""
    if request.method == 'POST':
        # Extract credentials
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('user_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'booking/login.html')


@login_required
def user_dashboard(request):
    query = request.GET.get('q', '')
    search_results = []

    if query:
        search_results = Doctor.objects.filter(
            (Q(user__username__icontains=query) | Q(specialization__icontains=query)) & Q(user__isnull=False)
        )

    appointments = []
    if hasattr(request.user, 'patient'):
        # If the logged-in user is a patient, fetch their appointments
        appointments = Appointment.objects.filter(patient=request.user.patient).order_by('date_time')
        user_role = 'patient'
    elif hasattr(request.user, 'doctor'):
        # If the logged-in user is a doctor, fetch their appointments
        appointments = Appointment.objects.filter(doctor=request.user.doctor).order_by('date_time')
        user_role = 'doctor'
    else:
        appointments = []
        user_role = 'unknown'

    return render(request, 'booking/user_dashboard.html', {
        'appointments': appointments,
        'search_results': search_results,
        'user_role': user_role,
    })



@login_required
def doctor_details(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    user = request.user

    # Time slots & days for the schedule table
    days_of_week = ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday']
    time_slots = [f'{hour:02d}:{minute:02d}' for hour in range(16, 22) for minute in [0, 30]]

    if request.method == "POST":
        selected_time = request.POST.get("selected_time")
        if not selected_time:
            return JsonResponse({"success": False, "message": "No time selected."})

        try:
            # The selected time will come in format "Day Hour:Minute"
            day, time = selected_time.split()

            # Combine the day and time into a string like "2025-01-06 16:00"
            today = datetime.now()
            day_mapping = {
                "Saturday": 5,
                "Sunday": 6,
                "Monday": 0,
                "Tuesday": 1,
                "Wednesday": 2,
            }
            target_day = today + timedelta(days=(day_mapping[day] - today.weekday()) % 7)
            appointment_datetime_str = f"{target_day.date()} {time}"

            # Parse the appointment datetime string
            appointment_time = datetime.strptime(appointment_datetime_str, "%Y-%m-%d %H:%M")

            # Check if the user already has a reserved slot
            if Appointment.objects.filter(patient__user=user, doctor=doctor).exists():
                return JsonResponse({"success": False, "message": "You already have a slot reserved with this doctor."})

            # Check if the slot is already reserved by someone else
            if Appointment.objects.filter(doctor=doctor, date_time=appointment_time).exists():
                return JsonResponse({"success": False, "message": "This slot is already reserved."})

            if Appointment.objects.filter(patient__user=user, date_time=appointment_time).exists():
                return JsonResponse({"success": False, "message": "You cannot reserve appointments with two doctors at the same time."})

            # Create the appointment if all validations pass
            patient = Patient.objects.get(user=user)
            Appointment.objects.create(doctor=doctor, patient=patient, date_time=appointment_time, status="Confirmed")

            return JsonResponse({
                "success": True,
                "message": f"{user.username}, you reserved {time} on {day} with Dr. {doctor.user.username}.",
            })

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    appointments = Appointment.objects.filter(doctor=doctor)
    slot_table = []

    for day in days_of_week:
        row = {"day": day, "slots": []}
        for time in time_slots:
            is_reserved = False
            is_reserved_by_user = False

            for appointment in appointments:
                appointment_day = appointment.date_time.strftime("%A")
                appointment_time = appointment.date_time.strftime("%H:%M")
                if appointment_day == day and appointment_time == time:
                    is_reserved = True
                    if appointment.patient.user == user:
                        is_reserved_by_user = True
                    break

            row["slots"].append({
                "time": time,
                "is_reserved": is_reserved,
                "is_reserved_by_user": is_reserved_by_user,
            })
        slot_table.append(row)

    return render(request, 'booking/doctor_details.html', {
        'doctor': doctor,
        'slot_table': slot_table,
    })



@api_view(['GET'])
def doctor_list(request):
    doctors = Doctor.objects.all()
    serializer = DoctorSerializer(doctors, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def appointment_list(request):
    appointments = Appointment.objects.filter(patient=request.user.patient)
    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def book_appointment(request):
    doctor_id = request.data.get('doctor_id')
    selected_time = request.data.get('selected_time')

    # Check if the doctor exists
    doctor = get_object_or_404(Doctor, id=doctor_id)

    # Check if the patient already has an appointment at the selected time
    if Appointment.objects.filter(patient=request.user.patient, date_time=selected_time).exists():
        return Response({'error': 'You already have an appointment at this time.'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the selected time slot is already booked for this doctor
    if Appointment.objects.filter(doctor=doctor, date_time=selected_time).exists():
        return Response({'error': 'Slot already booked'}, status=status.HTTP_400_BAD_REQUEST)

    # Create the appointment if no conflicts
    appointment = Appointment.objects.create(
        patient=request.user.patient,
        doctor=doctor,
        date_time=selected_time,
        status='Pending'
    )

    # Create a notification for the patient
    Notification.objects.create(
        user=request.user,
        message=f'Your appointment with Dr. {doctor.user.username} on {selected_time} is confirmed.'
    )

    return Response({'message': 'Appointment booked successfully'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_review(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    serializer = ReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(doctor=doctor)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_doctors(request):
    query = request.query_params.get('q', '')
    if not query:
        doctors = Doctor.objects.all()
    else:
        doctors = Doctor.objects.filter(
            Q(user__username__icontains=query) | Q(specialization__icontains=query)
        )
    serializer = DoctorSerializer(doctors, many=True)
    return Response(serializer.data)


def logout_view(request):
    logout(request)
    return redirect('login')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_slots(request, doctor_id):
    doctor = Doctor.objects.get(id=doctor_id)
    available_slots = doctor.get_available_slots()
    slots_data = []
    for day, slots in available_slots.items():
        for slot in slots:
            slots_data.append(slot.isoformat())
    return Response({"available_slots": slots_data})
