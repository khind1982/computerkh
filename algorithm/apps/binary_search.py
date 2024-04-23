import math

def BinarySearch(searchList, searchItem):
    left_point = 0
    right_point = len(searchList)-1
    comparisons = 0
    while left_point <= right_point:
        comparisons += 1
        # Item won't be there if there is crossover
        mid_point = math.ceil((left_point + right_point) / 2)
        if searchList[mid_point] < searchItem:
            # This moves the left pointer if the midpoint is less than the search item.
            left_point = mid_point + 1
        elif searchList[mid_point] > searchItem:
            right_point = mid_point - 1
        else:
            # If the conditions above are false, this is the number
            return comparisons, mid_point
    # If all the searches are exhausted and there is a crossover
    return comparisons, -1

myList = [5,12,24,36,40,51,68,72,84,104,115,121,136,145,152,167,174,99,189]

target = 99

result = BinarySearch(sorted(myList), target)

if result[1] == -1:
    print("Item not found.", result[0], " comparisons were made.")
else:
    print(target, " was found at index number ", result[1], ". ", result[0], " comparisons were made.")