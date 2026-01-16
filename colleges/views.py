from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course
from accounts.models import CollegeProfile
from counselling.models import Allocation

@login_required
def college_dashboard(request):
    """College admin dashboard"""
    if request.user.user_type != 'college_admin':
        return redirect('home')
    
    college = get_object_or_404(CollegeProfile, user=request.user)
    courses = Course.objects.filter(college=college)
    
    context = {
        'college': college,
        'courses': courses,
        'total_courses': courses.count(),
        'total_seats': sum(course.total_seats for course in courses),
        'seats_filled': sum(course.seats_filled for course in courses),
    }
    return render(request, 'colleges/dashboard.html', context)

@login_required
def course_list(request):
    """List all courses for college"""
    if request.user.user_type != 'college_admin':
        return redirect('home')
    
    college = get_object_or_404(CollegeProfile, user=request.user)
    courses = Course.objects.filter(college=college)
    
    return render(request, 'colleges/course_list.html', {'courses': courses})

@login_required
def add_course(request):
    """Add new course"""
    if request.user.user_type != 'college_admin':
        return redirect('home')
    
    if request.method == 'POST':
        college = get_object_or_404(CollegeProfile, user=request.user)
        
        course = Course.objects.create(
            college=college,
            course_name=request.POST['course_name'],
            course_code=request.POST['course_code'],
            department=request.POST['department'],
            degree_type=request.POST['degree_type'],
            duration_years=request.POST['duration_years'],
            total_seats=request.POST['total_seats'],
            fee_per_year=request.POST['fee_per_year'],
        )
        
        messages.success(request, f'Course {course.course_name} added successfully!')
        return redirect('colleges:course_list')
    
    return render(request, 'colleges/add_course.html')

@login_required
def course_analytics(request, course_id):
    """Course-specific analytics"""
    if request.user.user_type != 'college_admin':
        return redirect('home')
    
    course = get_object_or_404(Course, id=course_id, college__user=request.user)
    allocations = Allocation.objects.filter(course=course)
    
    context = {
        'course': course,
        'allocations': allocations,
        'total_allocations': allocations.count(),
        'allocated_count': allocations.filter(status='ALLOCATED').count(),
    }
    return render(request, 'colleges/course_analytics.html', context)
