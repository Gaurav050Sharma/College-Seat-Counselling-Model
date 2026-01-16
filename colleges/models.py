from django.db import models
from accounts.models import CollegeProfile

class Course(models.Model):
    """Course offered by colleges"""
    
    college = models.ForeignKey(CollegeProfile, on_delete=models.CASCADE, related_name='courses')
    course_name = models.CharField(max_length=200)
    course_code = models.CharField(max_length=20)
    department = models.CharField(max_length=100)
    degree_type = models.CharField(max_length=50, choices=[
        ('B.Tech', 'Bachelor of Technology'),
        ('B.E.', 'Bachelor of Engineering'),
        ('B.Sc', 'Bachelor of Science'),
        ('M.Tech', 'Master of Technology'),
        ('M.E.', 'Master of Engineering'),
        ('M.Sc', 'Master of Science'),
    ])
    duration_years = models.IntegerField(default=4)
    total_seats = models.IntegerField()
    seats_filled = models.IntegerField(default=0)
    fee_per_year = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['college', 'course_code']
        ordering = ['college', 'course_name']
    
    def __str__(self):
        return f"{self.college.college_name} - {self.course_name}"
    
    @property
    def available_seats(self):
        return self.total_seats - self.seats_filled
    
    @property
    def is_seats_available(self):
        return self.available_seats > 0
