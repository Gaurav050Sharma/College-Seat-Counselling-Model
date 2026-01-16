from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Custom User model with role-based access"""
    
    USER_TYPES = (
        ('super_admin', 'Super Admin'),
        ('college_admin', 'College Admin'),
        ('student', 'Student'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

class StudentProfile(models.Model):
    """Extended profile for students"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    roll_number = models.CharField(max_length=20, unique=True)
    rank = models.IntegerField(unique=True)
    category = models.CharField(max_length=20, choices=[
        ('GENERAL', 'General'),
        ('OBC', 'OBC'),
        ('SC', 'SC'),
        ('ST', 'ST'),
    ])
    token_paid = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['rank']
    
    def __str__(self):
        return f"{self.roll_number} - Rank {self.rank}"

class CollegeProfile(models.Model):
    """Extended profile for colleges"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='college_profile')
    college_name = models.CharField(max_length=200)
    college_code = models.CharField(max_length=10, unique=True)
    address = models.TextField()
    established_year = models.IntegerField()
    website = models.URLField(blank=True)
    
    def __str__(self):
        return self.college_name
