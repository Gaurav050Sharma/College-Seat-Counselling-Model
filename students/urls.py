from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('preferences/', views.fill_preferences, name='fill_preferences'),
    path('payment/', views.make_payment, name='make_payment'),
]
