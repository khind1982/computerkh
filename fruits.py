# Classes always defined with a capital letter
class Fruit:
    # A constructor is called automatically when called
    def __init__(self, name, colour):
        print("Fruit's constructor called")
        # 'self' refers to the object itself as 'self'
        # Calling a new object will use __init__ parameters
        self.name = name
        self.colour = colour

    def set_make(self, make):
        self.__make = make

    def get_make(self):
        print(self.__make)

    # Need to be able to set the value of an attribute


fruit1 = Fruit("Banana", "Yellow")
print(fruit1.name)
print(fruit1.colour)

# To print an object's attribute
# Create a 'car' class
# Add attributes the same as we used for a dictionary
# Need to look at car program
# Create 2 different instances of car
# Print the objects themselves
# Print each attributes of the cars

cars = [
    {"brand": "Ford", "model": "Mustang", "year": 1964},
    {"brand": "Toyota", "model": "Supra", "year": 1993},
    {"brand": "Fiat", "model": "500", "year": 2010}
    ]

class Car:
    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year

mustang = Car("Ford", "Mustang", 1964)
supra = Car("Toyota", "Supra", 1993)
fiat500 = Car("Fiat", "500", 2010)

# for car in [mustang, supra, fiat500]:
#     # Printing the object and the memory address of the object
#     print(car, car.make, car.model, car.year)

x = 13
y = x

print(x)
print(y)

x = 23

print(x)
print(y)

# Create a car3 that is the same as car1
# Print the makes of car3 and car1
# Change the make of car1
#print again

car1 = Car("Ford", "Mustang", 1964)
car2 = Car("Toyota", "Supra", 1993)
car3 = Car("Ford", "Mustang", 1964)

# Overrides your definition of car3 above
car3 = car1

print(car1.make)
print(car3.make)

car1model = "Renault"
# Pointer to the place in memory is copied
#

print(car1.make)
print(car3.make)

class Car:
    def __init__(self, make, model, year):
        self.__make = make
        self.__model = model
        self.__year = year

    def set_make(self, make):
        self.__make = make

    def get_make(self):
        print(self.__make)

    def how_long(self):
        print(2022 - self.__year)

car1 = Car("Ford", "Mustang", 1964)
car2 = Car("Toyota", "Supra", 1993)

car1.set_make("changed")
car1.get_make()

# Could just add these to a list
my_cars = []
my_cars.append(Car("Ford", "Mustang", 1964))
my_cars.append(Car("Toyota", "Supra", 1993))

my_cars[0].get_make()
