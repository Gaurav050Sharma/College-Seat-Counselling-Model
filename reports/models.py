from django.db import models

class Report(models.Model):
    """Generated reports"""
    
    REPORT_TYPES = [
        ('student_analytics', 'Student Analytics'),
        ('college_analytics', 'College Analytics'),
        ('round_summary', 'Round Summary'),
        ('seat_matrix', 'Seat Matrix'),
    ]
    
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    file_path = models.CharField(max_length=500, blank=True)
    generated_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_report_type_display()}"
