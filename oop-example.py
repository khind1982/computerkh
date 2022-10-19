class Person:
    # Create members (attributes) of the class
    def __init__(self, firstname, surname, age):
        # Each person must have a firstname, surname, and age
        # Using double underscore protects the attributes
        self.__firstname = firstname
        self.__surname = surname
        self.__age = age
    
    # Use 'gettr' and 'settr' methods to obtain methods
    def get_firstname(self):
        return self.__firstname

    # Use setter to set attribute value
    def set_firstname(self, newname):
        self.__firstname = newname

    #Polymorphism example
    def display_person(self):
        print(self.__firstname)
        print(self.__surname)
        print(self.__age)


class Student(Person):
    def __init__(self, firstname, surname, age, year, subject):
        Person.__init__(self, firstname, surname, age)
        self.__year = year
        self.__subject = subject

    def get_year(self):
        return self.__year

    def set_year(self):
        self.__year = newyear

person1 = Person('Matt', 'Lyons', '32')
print(person1)
# Breaks rule of encapsulation
# Don't call a class attribute outside the class
# print(person1.firstname)
# person1.firstname = 'Bob'
# print(person1.firstname)
print(person1.get_firstname())
person1.set_firstname('Bobby')
print(person1.get_firstname())

person1.display_person()

# Could create as many people as we wanted
mystudent = Student('Matt', 'Lyons', 32, 11, 'Computer Science')
print(mystudent.get_year())