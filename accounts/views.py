from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import User, StudentProfile, CollegeProfile

def home(request):
    """Home page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/home.html')

def user_login(request):
    """Login view for all user types"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'accounts/login.html')

@login_required
def user_logout(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')

@login_required
def dashboard(request):
    """Dashboard - redirects based on user type"""
    user = request.user
    
    if user.user_type == 'super_admin':
        # Import the required models for statistics
        from colleges.models import Course
        from counselling.models import CounsellingSettings
        from django.db.models import Sum
        
        # Get statistics for super admin dashboard
        total_students = StudentProfile.objects.count()
        paid_students = StudentProfile.objects.filter(token_paid=True).count()
        total_colleges = CollegeProfile.objects.count()
        total_courses = Course.objects.count()
        total_seats = Course.objects.aggregate(total=Sum('total_seats'))['total'] or 0

        
        # Get counselling status
        settings = CounsellingSettings.get_settings()
        if settings.allocation_completed:
            counselling_status = "Completed"
        elif settings.preference_submission_open:
            counselling_status = "In Progress"
        else:
            counselling_status = "Not Started"
        
        context = {
            'total_students': total_students,
            'paid_students': paid_students,
            'total_colleges': total_colleges,
            'total_courses': total_courses,
            'total_seats': total_seats,
            'counselling_status': counselling_status,
        }
        return render(request, 'accounts/super_admin_dashboard.html', context)
    elif user.user_type == 'college_admin':
        return render(request, 'accounts/college_dashboard.html')
    elif user.user_type == 'student':
        return render(request, 'accounts/student_dashboard.html')
    else:
        return redirect('home')

@login_required
def profile(request):
    """User profile view"""
    return render(request, 'accounts/profile.html')
