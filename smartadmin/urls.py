from django.urls import path
from .views import *

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('schools/', schools, name='schools'),
    path('users/', users, name='users'),
    path('documents/', documents, name='documents'),
    path('analytics/', analytics, name='analytics'),
    path('schools/approve/<int:school_id>/', approve_school, name='approve_school'),
    path('schools/reject/<int:school_id>/', reject_school, name='reject_school'),
    path('schools/delete/<int:school_id>/', delete_school, name='delete_school'),
]
