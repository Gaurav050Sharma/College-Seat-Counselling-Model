from django.contrib import admin
from .models import (
    CounsellingSettings,
    Payment,
    Allocation,
    AllocationStatistics
)

@admin.register(CounsellingSettings)
class CounsellingSettingsAdmin(admin.ModelAdmin):
    list_display = ('registration_open', 'preference_submission_open', 'payment_required', 'allocation_completed', 'counselling_fee')
    readonly_fields = ('created_at', 'updated_at')
    
    def has_add_permission(self, request):
        # Only allow one settings instance
        return not CounsellingSettings.objects.exists()

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'payment_method', 'status', 'payment_date', 'transaction_id')
    list_filter = ('status', 'payment_method', 'payment_date')
    search_fields = ('student__user__username', 'student__user__email', 'transaction_id')
    readonly_fields = ('transaction_id', 'created_at', 'updated_at', 'gateway_reference')
    ordering = ['-created_at']

@admin.register(Allocation)
class AllocationAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'preference_number', 'allocated_at')
    list_filter = ('preference_number', 'allocated_at', 'course__college')
    search_fields = ('student__user__username', 'student__user__email', 'course__name', 'course__college__name')
    ordering = ['student__rank']

@admin.register(AllocationStatistics)
class AllocationStatisticsAdmin(admin.ModelAdmin):
    list_display = ('total_students', 'students_paid', 'students_with_preferences', 'students_allocated', 'seats_filled', 'total_seats')
    readonly_fields = ('total_students', 'students_paid', 'students_with_preferences', 'students_allocated', 'seats_filled', 'total_seats', 'allocation_date', 'created_at', 'updated_at')
    
    def has_add_permission(self, request):
        # Only allow one statistics instance
        return not AllocationStatistics.objects.exists()
