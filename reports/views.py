from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from .models import Report
from accounts.models import StudentProfile
from colleges.models import Course
from counselling.models import Allocation
from students.models import StudentPreference
import pandas as pd
from django.conf import settings
import os
from datetime import datetime

def get_current_allocation(student):
    """Get student's current allocation"""
    try:
        allocation = Allocation.objects.filter(student=student).first()
        return allocation
    except Allocation.DoesNotExist:
        return None

@login_required
def reports_dashboard(request):
    """Simple reports dashboard"""
    context = {
        'total_students': StudentProfile.objects.count(),
        'total_allocations': Allocation.objects.count(),
        'total_courses': Course.objects.count(),
    }
    return render(request, 'reports/dashboard.html', context)

@login_required  
def export_allocations(request):
    """Export allocation results to CSV"""
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="allocations.csv"'
    
    # Write CSV data
    import csv
    writer = csv.writer(response)
    writer.writerow(['Student', 'Course', 'College', 'Preference Number', 'Allocated Date'])
    
    allocations = Allocation.objects.select_related('student__user', 'course__college')
    for allocation in allocations:
        writer.writerow([
            allocation.student.user.get_full_name(),
            allocation.course.name,
            allocation.course.college.name,
            allocation.preference_number,
            allocation.allocated_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response

# Simplified views - complex reporting disabled for now
def generate_allocation_report(request):
    """Simplified allocation report"""
    return redirect('reports:dashboard')

def generate_preference_report(request):
    """Simplified preference report"""  
    return redirect('reports:dashboard')

def generate_college_report(request):
    """Simplified college report"""
    return redirect('reports:dashboard')
