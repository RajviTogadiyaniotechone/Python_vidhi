#Fibonacci Sequence

def fibMem(n, fibdict):
    if n in fibdict:
        return fibdict[n]  
    else:
        fibdict[n] = fibMem(n - 1, fibdict) + fibMem(n - 2, fibdict)
        return fibdict[n]

n = int(input("Enter a number for Fibonacci calculation: "))
fibdict = {0: 0, 1: 1}      

print(fibMem(n, fibdict))

for i in range(n + 1):
    print(fibMem(i, fibdict), end=" ")
    
print("\ndictionary ::" ,fibdict)
