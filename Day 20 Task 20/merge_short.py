#merge short
def merge_sort(arr, left, right):
    if left < right:
        mid = (left + right) // 2
        merge_sort(arr, left, mid)
        merge_sort(arr, mid + 1, right)
        merge(arr, left, right, mid)

def merge(arr, left, right, mid):
    n1 = arr[left:mid + 1]  # left subarray
    n2 = arr[mid + 1:right + 1]  # right subarray
    
    i = 0  # index for n1
    j = 0  # index for n2
    k = left  # index for the main array
    
    # Merge the two subarrays into arr
    while i < len(n1) and j < len(n2):
        if n1[i] <= n2[j]:
            arr[k] = n1[i]
            i += 1
        else:
            arr[k] = n2[j]
            j += 1
        k += 1
        
    # Copy any remaining elements of n1
    while i < len(n1):
        arr[k] = n1[i]
        i += 1
        k += 1
        
    # Copy any remaining elements of n2
    while j < len(n2):
        arr[k] = n2[j]
        j += 1
        k += 1


user_input = input("Enter numbers of list you want to sort separated by commas: ")
numbers = list(map(int, user_input.split(',')))

merge_sort(numbers, 0, len(numbers) - 1)

print("Sorted array:", numbers)


