from django.contrib import admin
from .models import Course

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_name', 'college', 'course_code', 'total_seats', 'seats_filled', 'available_seats', 'is_active')
    list_filter = ('degree_type', 'is_active', 'college')
    search_fields = ('course_name', 'course_code', 'college__college_name')
    readonly_fields = ('available_seats',)
