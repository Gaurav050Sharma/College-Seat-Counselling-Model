from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_dashboard, name='reports_dashboard'),
    path('export/', views.export_allocations, name='export_allocations'),
    path('generate/allocation/', views.generate_allocation_report, name='generate_allocation_report'),
    path('generate/preference/', views.generate_preference_report, name='generate_preference_report'),
    path('generate/college/', views.generate_college_report, name='generate_college_report'),
]
