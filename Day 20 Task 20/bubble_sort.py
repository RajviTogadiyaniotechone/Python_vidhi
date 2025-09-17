#Bubble sort

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr


user_input = input("Enter numbers to sort (comma-separated): ").split(',')
arr = [int(x) for x in user_input] 

print("Before sorting:", arr)
arr = bubble_sort(arr)
print("After sorting:", arr)