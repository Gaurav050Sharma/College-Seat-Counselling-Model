from django.urls import path
from . import views

app_name = 'counselling'

urlpatterns = [
    # Admin Dashboard
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/run-allocation/', views.run_allocation, name='run_allocation'),
    path('admin/reset-system/', views.reset_system, name='reset_system'),
    path('admin/export-results/', views.export_results, name='export_results'),
    path('admin/api/dashboard/', views.dashboard_api, name='dashboard_api'),
    
    # Student Dashboard
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('student/payment/', views.make_payment, name='make_payment'),
]
