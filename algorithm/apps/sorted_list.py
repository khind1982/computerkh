mylist = [29, 10, 14, 325, 3, -1, -42, 13, 37, 14]

sorted_list = []

while mylist:
    smallest = mylist[0]
    for number in mylist:
        if number < smallest:
            smallest = number
    sorted_list.append(smallest)
    mylist.remove(smallest)

print(sorted_list)