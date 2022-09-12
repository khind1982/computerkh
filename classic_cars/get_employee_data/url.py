from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.say_hello),
    path('employees/', views.retrieve_employee_data),
]