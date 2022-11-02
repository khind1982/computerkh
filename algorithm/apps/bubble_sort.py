mylist = [8, 3, 5, 2, 1, 4, 9, 7, 6]

swapped = True

list_positions = len(mylist) - 1

while swapped:
    swapped = False
    for i in range(0, list_positions):
        if mylist[i] > mylist[i + 1]:
            temp = mylist[i+1]
            mylist[i+1] = mylist[i]
            mylist[i] = temp
            swapped = True
            print(mylist)
print(mylist)
