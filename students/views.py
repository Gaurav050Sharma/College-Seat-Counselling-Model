from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import StudentPreference
from colleges.models import Course
from accounts.models import StudentProfile
from counselling.models import Allocation, CounsellingSettings, Payment
import uuid

@login_required
def student_dashboard(request):
    """Student dashboard"""
    if request.user.user_type != 'student':
        return redirect('home')
    
    student = get_object_or_404(StudentProfile, user=request.user)
    preferences = StudentPreference.objects.filter(student=student)
    
    # Get current allocation
    current_allocation = None
    try:
        allocation = Allocation.objects.filter(student=student, status='ALLOCATED').first()
        current_allocation = allocation.course if allocation else None
    except:
        pass
    
    context = {
        'student': student,
        'preferences': preferences,
        'current_allocation': current_allocation,
        'token_paid': student.token_paid,
    }
    return render(request, 'students/dashboard.html', context)

@login_required
def fill_preferences(request):
    """Fill course preferences"""
    if request.user.user_type != 'student':
        return redirect('home')
    
    student = get_object_or_404(StudentProfile, user=request.user)
    
    if request.method == 'POST':
        # Clear existing preferences
        StudentPreference.objects.filter(student=student).delete()
        
        # Get selected courses and their order
        course_ids = request.POST.getlist('courses')
        for index, course_id in enumerate(course_ids):
            if course_id:
                course = Course.objects.get(id=course_id)
                StudentPreference.objects.create(
                    student=student,
                    course=course,
                    preference_order=index + 1
                )
        
        messages.success(request, 'Preferences saved successfully!')
        return redirect('students:student_dashboard')
    
    # Get all available courses
    courses = Course.objects.filter(is_active=True).select_related('college')
    existing_preferences = StudentPreference.objects.filter(student=student).order_by('preference_order')
    
    context = {
        'courses': courses,
        'existing_preferences': existing_preferences,
    }
    return render(request, 'students/fill_preferences.html', context)

@login_required
def make_payment(request):
    """Mock payment for allocated course"""
    if request.user.user_type != 'student':
        return redirect('home')
    
    student = get_object_or_404(StudentProfile, user=request.user)
    
    # Check if student has allocation
    allocation = Allocation.objects.filter(student=student, status='ALLOCATED').first()
    if not allocation:
        messages.error(request, 'No seat allocated yet!')
        return redirect('students:student_dashboard')
    
    if student.token_paid:
        messages.info(request, 'Payment already completed!')
        return redirect('students:student_dashboard')
    
    if request.method == 'POST':
        # Mock payment processing
        payment = Payment.objects.create(
            student=student,
            amount=5000.00,  # Mock payment amount
            payment_method=request.POST.get('payment_method', 'credit_card'),
            status='COMPLETED',
            transaction_id=str(uuid.uuid4()),
        )
        
        # Update student profile
        student.token_paid = True
        student.save()
        
        messages.success(request, f'Payment successful! Transaction ID: {payment.transaction_id}')
        return redirect('students:student_dashboard')
    
    context = {
        'allocation': allocation,
        'amount': 5000.00,
    }
    return render(request, 'students/payment.html', context)
