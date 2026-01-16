from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, StudentProfile, CollegeProfile

class CustomUserAdmin(UserAdmin):
    """Custom admin for User model"""
    list_display = ('username', 'email', 'user_type', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_active', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone')}),
    )

class StudentProfileAdmin(admin.ModelAdmin):
    """Admin for Student Profile"""
    list_display = ('roll_number', 'user', 'rank', 'category', 'token_paid')
    list_filter = ('category', 'token_paid')
    search_fields = ('roll_number', 'user__username')
    ordering = ('rank',)

class CollegeProfileAdmin(admin.ModelAdmin):
    """Admin for College Profile"""
    list_display = ('college_name', 'college_code', 'user', 'established_year')
    search_fields = ('college_name', 'college_code')

admin.site.register(User, CustomUserAdmin)
admin.site.register(StudentProfile, StudentProfileAdmin)
admin.site.register(CollegeProfile, CollegeProfileAdmin)
