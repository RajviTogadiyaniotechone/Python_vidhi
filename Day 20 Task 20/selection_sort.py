#selection sort

def selection_sort (array):
    for i in range(0,len(array)-1):
        smallest = i
    
    for j in range(i+1 ,len(array)):
        if array[j] < array[smallest]:
            smallest = j
            
    array[i],array[smallest] = array[smallest],array[j]
    
array = (input("Enter a array you want to sort :").split(','))

array = [int(x) for x in array]

print("Sorted array:", sorted(array))