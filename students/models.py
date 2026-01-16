from django.db import models
from accounts.models import StudentProfile
from colleges.models import Course

class StudentPreference(models.Model):
    """Student course preferences"""
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='preferences')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    preference_order = models.IntegerField()  # 1 = highest priority
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'course']
        ordering = ['student', 'preference_order']
    
    def __str__(self):
        return f"{self.student.roll_number} - {self.preference_order}. {self.course.course_name}"
