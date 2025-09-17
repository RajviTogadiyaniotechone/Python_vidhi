def fact(n):
    if n==1 or n==0:
        return 1
    else :
        return n * fact(n-1)
    
user_input = input("enter a number:")

if user_input.isdigit():  
    num = int(user_input)  
    f = fact(num)          
    print(f"Factorial of {num} is {f}")
else:
    print("Invalid input! Please enter a valid non-negative integer.")
