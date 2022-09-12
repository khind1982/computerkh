from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

# names = {'name' : 'Kevin'}

def say_hello(request):
    return render(request, 'mypage.html')

# Any string-based dataset
# Could read in data from a DB
def retrieve_employee_data(request):
    return render(request, 'employee_tracker.html', {'name':'Kevin'})
