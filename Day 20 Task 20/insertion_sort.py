#insertion sort
def insertion_sort(array):
    n = len(array)
    
    if n <= 1:
        return # If the array has 0 or 1 element, it is already sorted, so return

    for i in range (1,n):
        
        temp = array[i]
        
        j = i - 1
        
        while j >= 0 and temp < array[j]:
            array[j+1] = array[j]
            j -= 1
        array[j+1] =temp

user_input = input("Enter the elements of the array: ")
# Converting input to a list of integers
array = list(map(int, user_input.split(',')))

# Calling the InsertionSort function
insertion_sort(array)


print("sorted array :")
print(array)



