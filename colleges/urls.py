from django.urls import path
from . import views

app_name = 'colleges'

urlpatterns = [
    path('dashboard/', views.college_dashboard, name='college_dashboard'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/add/', views.add_course, name='add_course'),
    path('courses/<int:course_id>/analytics/', views.course_analytics, name='course_analytics'),
]
