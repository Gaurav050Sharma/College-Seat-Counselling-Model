from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
import uuid

User = get_user_model()

class CounsellingSettings(models.Model):
    """Simple counselling system settings"""
    
    registration_open = models.BooleanField(default=True)
    preference_submission_open = models.BooleanField(default=True)
    payment_required = models.BooleanField(default=True)
    allocation_completed = models.BooleanField(default=False)
    counselling_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    class Meta:
        verbose_name = "Counselling Settings"
        verbose_name_plural = "Counselling Settings"
    
    def __str__(self):
        return "Counselling System Settings"
    
    @classmethod
    def get_settings(cls):
        """Get or create settings instance"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class Payment(models.Model):
    """Simplified payment system - mock payment gateway"""
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('net_banking', 'Net Banking'),
        ('upi', 'UPI'),
        ('wallet', 'Digital Wallet'),
    ]
    
    student = models.OneToOneField('accounts.StudentProfile', on_delete=models.CASCADE, related_name='payment')
    transaction_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Mock payment gateway fields
    gateway_reference = models.CharField(max_length=100, blank=True)
    failure_reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.transaction_id} - {self.student.user.username} - {self.status}"
    
    def process_payment(self):
        """Mock payment processing - simulates payment gateway"""
        import random
        
        if self.status != 'pending':
            return False
            
        self.status = 'processing'
        self.save()
        
        # Simulate payment processing (90% success rate)
        success = random.random() < 0.9
        
        if success:
            self.status = 'completed'
            self.payment_date = timezone.now()
            self.gateway_reference = f"GW{random.randint(100000, 999999)}"
        else:
            self.status = 'failed'
            self.failure_reason = "Insufficient funds or card declined"
            
        self.save()
        return success


class Allocation(models.Model):
    """Final seat allocation result"""
    
    STATUS_CHOICES = [
        ('ALLOCATED', 'Allocated'),
        ('CONFIRMED', 'Confirmed'),
        ('WITHDRAWN', 'Withdrawn'),
    ]
    
    student = models.OneToOneField('accounts.StudentProfile', on_delete=models.CASCADE, related_name='allocation')
    course = models.ForeignKey('colleges.Course', on_delete=models.CASCADE, related_name='allocations')
    preference_number = models.IntegerField(default=1)  # Which preference got allocated (1st, 2nd, etc.)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ALLOCATED')
    allocated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['student__rank']
    
    def __str__(self):
        return f"{self.student.user.username} -> {self.course.course_name} ({self.course.college.college_name})"


class AllocationStatistics(models.Model):
    """Simple statistics for admin dashboard"""
    
    total_students = models.IntegerField(default=0)
    students_paid = models.IntegerField(default=0)
    students_with_preferences = models.IntegerField(default=0)
    students_allocated = models.IntegerField(default=0)
    total_seats = models.IntegerField(default=0)
    seats_filled = models.IntegerField(default=0)
    allocation_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Allocation Statistics"
        verbose_name_plural = "Allocation Statistics"
    
    def __str__(self):
        return f"Statistics - {self.students_allocated}/{self.total_students} allocated"
    
    @classmethod
    def calculate_stats(cls):
        """Calculate and update statistics"""
        from accounts.models import StudentProfile
        from colleges.models import Course
        from students.models import StudentPreference
        
        stats, created = cls.objects.get_or_create(pk=1)
        
        stats.total_students = StudentProfile.objects.count()
        stats.students_paid = Payment.objects.filter(status='completed').count()
        stats.students_with_preferences = StudentPreference.objects.values('student').distinct().count()
        stats.students_allocated = Allocation.objects.count()
        stats.total_seats = Course.objects.aggregate(total=models.Sum('total_seats'))['total'] or 0
        stats.seats_filled = Allocation.objects.count()
        
        settings = CounsellingSettings.get_settings()
        if settings.allocation_completed:
            stats.allocation_date = timezone.now()
            
        stats.save()
        return stats
