from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from django.db.models import Count, Sum
from django.utils import timezone
import csv
import json

from .models import (
    CounsellingSettings, 
    Payment, 
    Allocation, 
    AllocationStatistics
)
from accounts.models import StudentProfile
from colleges.models import Course
from students.models import StudentPreference


def is_super_admin(user):
    """Check if user is super admin"""
    return user.is_authenticated and user.user_type == 'super_admin'


def is_student(user):
    """Check if user is student"""
    return user.is_authenticated and user.user_type == 'student'


@login_required
@user_passes_test(is_super_admin)
def admin_dashboard(request):
    """Simplified admin dashboard with real-time stats"""
    settings = CounsellingSettings.get_settings()
    stats = AllocationStatistics.calculate_stats()
    
    # Recent payments
    recent_payments = Payment.objects.filter(status='completed').order_by('-payment_date')[:10]
    
    # Course-wise allocation summary
    course_stats = Course.objects.annotate(
        allocated_seats=Count('allocations')
    ).values(
        'course_name', 'college__college_name', 'total_seats', 'allocated_seats'
    )
    
    context = {
        'settings': settings,
        'stats': stats,
        'recent_payments': recent_payments,
        'course_stats': course_stats,
        'utilization_percentage': (stats.seats_filled / stats.total_seats * 100) if stats.total_seats > 0 else 0,
        'payment_percentage': (stats.students_paid / stats.total_students * 100) if stats.total_students > 0 else 0,
        'preference_percentage': (stats.students_with_preferences / stats.total_students * 100) if stats.total_students > 0 else 0,
    }
    return render(request, 'counselling/admin_dashboard.html', context)


@login_required
@user_passes_test(is_super_admin)
def run_allocation(request):
    """Run the seat allocation algorithm"""
    if request.method == 'POST':
        settings = CounsellingSettings.get_settings()
        
        if settings.allocation_completed:
            messages.error(request, "Allocation has already been completed!")
            return redirect('counselling:admin_dashboard')
        
        try:
            with transaction.atomic():
                # Clear existing allocations
                Allocation.objects.all().delete()
                
                # Get all students with completed payments and preferences
                eligible_students = StudentProfile.objects.filter(
                    payment__status='completed',
                    preferences__isnull=False
                ).distinct().order_by('rank')
                
                allocated_count = 0
                
                for student in eligible_students:
                    # Get student's preferences in order
                    preferences = StudentPreference.objects.filter(
                        student=student
                    ).order_by('preference_order')
                    
                    for pref in preferences:
                        course = pref.course
                        # Check if seats available
                        current_allocations = Allocation.objects.filter(course=course).count()
                        
                        if current_allocations < course.total_seats:
                            # Allocate seat
                            Allocation.objects.create(
                                student=student,
                                course=course,
                                preference_number=pref.preference_order
                            )
                            allocated_count += 1
                            break  # Student allocated, move to next student
                
                # Mark allocation as completed
                settings.allocation_completed = True
                settings.save()
                
                # Update statistics
                AllocationStatistics.calculate_stats()
                
                messages.success(request, f"Allocation completed successfully! {allocated_count} students allocated.")
                
        except Exception as e:
            messages.error(request, f"Error during allocation: {str(e)}")
    
    return redirect('counselling:admin_dashboard')


@login_required
@user_passes_test(is_super_admin)
def reset_system(request):
    """Reset the entire system for demo purposes"""
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Clear allocations and payments
                Allocation.objects.all().delete()
                Payment.objects.all().delete()
                
                # Reset settings
                settings = CounsellingSettings.get_settings()
                settings.allocation_completed = False
                settings.registration_open = True
                settings.preference_submission_open = True
                settings.save()
                
                # Update statistics
                AllocationStatistics.calculate_stats()
                
                messages.success(request, "System reset successfully!")
                
        except Exception as e:
            messages.error(request, f"Error during reset: {str(e)}")
    
    return redirect('counselling:admin_dashboard')


@login_required
@user_passes_test(is_super_admin)
def export_results(request):
    """Export allocation results as CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="allocation_results.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Student Name', 'Email', 'Rank', 'Allocated College', 'Allocated Course', 'Preference Number', 'Allocation Date'])
    
    allocations = Allocation.objects.select_related('student__user', 'course__college').order_by('student__rank')
    
    for allocation in allocations:
        writer.writerow([
            allocation.student.user.get_full_name(),
            allocation.student.user.email,
            allocation.student.rank,
            allocation.course.college.name,
            allocation.course.name,
            allocation.preference_number,
            allocation.allocated_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response


@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    """Student dashboard showing payment status, preferences, and allocation"""
    student = get_object_or_404(StudentProfile, user=request.user)
    settings = CounsellingSettings.get_settings()
    
    # Get payment status
    try:
        payment = Payment.objects.get(student=student)
    except Payment.DoesNotExist:
        payment = None
    
    # Get preferences
    preferences = StudentPreference.objects.filter(student=student).order_by('preference_order')
    
    # Get allocation
    try:
        allocation = Allocation.objects.get(student=student)
    except Allocation.DoesNotExist:
        allocation = None
    
    context = {
        'student': student,
        'settings': settings,
        'payment': payment,
        'preferences': preferences,
        'allocation': allocation,
        'can_submit_preferences': settings.preference_submission_open and payment and payment.status == 'completed',
        'can_make_payment': settings.payment_required and (not payment or payment.status != 'completed'),
    }
    return render(request, 'counselling/student_dashboard.html', context)


@login_required
@user_passes_test(is_student)
def make_payment(request):
    """Handle student payment"""
    student = get_object_or_404(StudentProfile, user=request.user)
    settings = CounsellingSettings.get_settings()
    
    # Check if payment already exists
    try:
        payment = Payment.objects.get(student=student)
        if payment.status == 'completed':
            messages.info(request, "Payment already completed!")
            return redirect('counselling:student_dashboard')
    except Payment.DoesNotExist:
        payment = None
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        if not payment:
            # Create new payment
            payment = Payment.objects.create(
                student=student,
                amount=settings.counselling_fee,
                payment_method=payment_method
            )
        
        # Process payment (mock)
        success = payment.process_payment()
        
        if success:
            messages.success(request, f"Payment of ₹{payment.amount} completed successfully! Transaction ID: {payment.transaction_id}")
        else:
            messages.error(request, f"Payment failed: {payment.failure_reason}")
        
        return redirect('counselling:student_dashboard')
    
    context = {
        'student': student,
        'settings': settings,
        'payment': payment,
    }
    return render(request, 'counselling/make_payment.html', context)


@login_required
@user_passes_test(is_super_admin)
def dashboard_api(request):
    """API endpoint for real-time dashboard updates"""
    stats = AllocationStatistics.calculate_stats()
    settings = CounsellingSettings.get_settings()
    
    data = {
        'total_students': stats.total_students,
        'students_paid': stats.students_paid,
        'students_with_preferences': stats.students_with_preferences,
        'students_allocated': stats.students_allocated,
        'total_seats': stats.total_seats,
        'seats_filled': stats.seats_filled,
        'utilization_percentage': round((stats.seats_filled / stats.total_seats * 100) if stats.total_seats > 0 else 0, 2),
        'payment_percentage': round((stats.students_paid / stats.total_students * 100) if stats.total_students > 0 else 0, 2),
        'preference_percentage': round((stats.students_with_preferences / stats.total_students * 100) if stats.total_students > 0 else 0, 2),
        'allocation_completed': settings.allocation_completed,
        'last_updated': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    return JsonResponse(data)
