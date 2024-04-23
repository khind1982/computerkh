def LinearSearch(searchList, searchItem):
    for num,counter in enumerate(range(0, len(searchList)), start=1):
        if searchList[counter] == searchItem:
            return num, counter
    return num, -1

myList = [5,12,24,36,40,51,68,72,84,104,115,121,136,145,152,167,174,99,189]

target = 99

result = LinearSearch(myList, target)

if result[1] == -1:
    print("Item not found.", result[0], " comparisons were made.")
else:
    print(target, " was found at index number ", result[1], ". ", result[0], " comparisons were made.")