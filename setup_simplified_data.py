#!/usr/bin/env python
"""
Quick setup script for simplified counselling system
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'counselling_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import StudentProfile, CollegeProfile
from colleges.models import Course
from counselling.models import CounsellingSettings

User = get_user_model()

def create_sample_data():
    """Create basic sample data for testing"""
    
    # Create counselling settings
    settings = CounsellingSettings.get_settings()
    settings.registration_open = True
    settings.preference_submission_open = True
    settings.payment_required = True
    settings.allocation_completed = False
    settings.counselling_fee = 500.00
    settings.save()
    print("✅ Counselling settings created")
    
    # Create a college admin user
    if not User.objects.filter(username='college_admin').exists():
        college_admin_user = User.objects.create_user(
            username='college_admin',
            email='college@test.com',
            password='admin123',
            first_name='College',
            last_name='Admin',
            user_type='college_admin'
        )
        print("✅ College admin user created")
    else:
        college_admin_user = User.objects.get(username='college_admin')
        
    # Create college profile if it doesn't exist
    if not CollegeProfile.objects.filter(user=college_admin_user).exists():
        CollegeProfile.objects.create(
            user=college_admin_user,
            college_name='ABC Engineering College',
            college_code='ABC',
            address='Mumbai, Maharashtra',
            established_year=2000
        )
        print("✅ College profile created")
    
    # Create sample students
    student_data = [
        {'username': 'student1', 'first_name': 'John', 'last_name': 'Doe', 'rank': 1},
        {'username': 'student2', 'first_name': 'Jane', 'last_name': 'Smith', 'rank': 2},
        {'username': 'student3', 'first_name': 'Bob', 'last_name': 'Johnson', 'rank': 3},
    ]
    
    for data in student_data:
        if not User.objects.filter(username=data['username']).exists():
            user = User.objects.create_user(
                username=data['username'],
                email=f"{data['username']}@test.com",
                password='student123',
                first_name=data['first_name'],
                last_name=data['last_name'],
                user_type='student'
            )
            StudentProfile.objects.create(
                user=user,
                roll_number=f"2025{data['rank']:03d}",
                rank=data['rank'],
                category='GENERAL'
            )
            print(f"✅ Student {data['username']} created")
    
    # Create sample courses
    college = CollegeProfile.objects.first()
    if college:
        courses = [
            {'name': 'Computer Science Engineering', 'total_seats': 60},
            {'name': 'Mechanical Engineering', 'total_seats': 50},
            {'name': 'Electrical Engineering', 'total_seats': 40},
        ]
        
        for course_data in courses:
            if not Course.objects.filter(course_name=course_data['name'], college=college).exists():
                Course.objects.create(
                    college=college,
                    course_name=course_data['name'],
                    total_seats=course_data['total_seats'],
                    course_code=course_data['name'][:3].upper(),
                    department=course_data['name'].split()[0],
                    degree_type='B.Tech',
                    fee_per_year=50000.00
                )
                print(f"✅ Course {course_data['name']} created")
    
    print("\n🎉 Sample data created successfully!")
    print("\n📋 Login Credentials:")
    print("Admin: admin / admin123")
    print("College Admin: college_admin / admin123")
    print("Students: student1, student2, student3 / student123")
    print("\n🌐 Access URLs:")
    print("Home: http://127.0.0.1:8000/")
    print("Admin Dashboard: http://127.0.0.1:8000/counselling/admin/")
    print("Student Dashboard: http://127.0.0.1:8000/students/dashboard/")

if __name__ == '__main__':
    create_sample_data()
