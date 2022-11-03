mylist = [8, 3, 5, 2, 1, 4, 9, 7, 6]

# sorted = mylist[0]

# for n,x in enumerate(mylist, start=0):
#     print(n, x)
#     for position in range(n, 0):
#         print(position)
#         if mylist[position] > x:
#             sorted = mylist[position]
#     print(mylist)

for step in range(1, len(mylist)):
    # At each iteration, the key is the number
    # At each step
    key = mylist[step]
    j = step - 1
    # At each step, the value of j is the value
    # of step - 1

    # Compare key with each element on the left until 
    # An element smaller than it is found
    while j >= 0 and key < mylist[j]:
        mylist[j + 1] = mylist[j]
        j = j - 1

    # Place key after the element just smaller than it
    mylist[j + 1] = key

    print(mylist)