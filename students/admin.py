from django.contrib import admin
from .models import StudentPreference

@admin.register(StudentPreference)
class StudentPreferenceAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'preference_order', 'created_at')
    list_filter = ('preference_order', 'course__college')
    search_fields = ('student__roll_number', 'course__course_name')
    ordering = ('student', 'preference_order')
