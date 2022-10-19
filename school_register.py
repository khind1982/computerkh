# Ask how many students are in the class
# Ask the teacher to enter all the names one by one
# Create a text file where fname is current date and time
from datetime import datetime as datetime

number_of_students = input("How many students are in your class? ")

print(f"There are {number_of_students} student(s) in your class.")

students = []

n = 1
while n <= int(number_of_students):
    n += 1
    student = input("Enter name of student: ")
    students.append(student)

print("Maximum number of students entered.  Writing to output file...")

outstring = datetime.now().strftime('%Y%m%d-%H%M%S')
with open(f'{outstring}.txt', 'w') as outfile:
    for student in students:
        outfile.write(f'{student.strip()}\n')