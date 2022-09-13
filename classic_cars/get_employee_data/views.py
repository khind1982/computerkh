import os
import sqlite3

from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

# names = {'name' : 'Kevin'}
db = sqlite3.connect("/home/khind/git/computerkh/db/classic_models.db")
cursor = db.cursor()
cursor.execute("SELECT * FROM employees")
employees = [i for i in cursor]

def say_hello(request):
    return render(request, 'mypage.html')

# Any string-based dataset
# Could read in data from a DB
def retrieve_employee_data(request):
    return render(request, 'employee_tracker.html', {'data': employees})
