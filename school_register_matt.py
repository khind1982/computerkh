noOfStudents = int(input("How many students are in your class today?"))

classlist = []
for counter in range(noOfStudents):
    newStudent = input('Enter student name: ')
    classlist.append(newStudent)

file = open('test.txt', 'w')
for person in classlist:
    file.write(person + "\n")
file.close()