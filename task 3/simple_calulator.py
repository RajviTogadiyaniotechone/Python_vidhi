
def addition(n1,n2):
    return n1+n2

def subtraction(n1,n2):
    return n1-n2

def multiplication(n1,n2):
    return n1*n2

def division(n1,n2):
    return n1/n2



print("select operations :")
print("1. Addition ")
print("2. Subtraction")
print("3. Multiplication")
print("4. Division")


while True:
    
    choice = int(input("Enter a choice of operation 1/2/3/4 : "))

    if choice in ('1', '2', '3', '4'):
        try:
            num1 = float(input("Enter first number: "))
            num2 = float(input("Enter second number: "))
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

    num1 = float(input("Enter a first Number :"))
    num2 = float(input("Enter a Second Number:"))
        
    
    if choice == 1 :
        print(num1 ,"+", num2 , "=" , addition(num1,num2)) 
    elif choice == 2:
        print(num1 ,"-", num2 ,"=" ,subtraction(num1,num2)) 
    elif choice == 3:
        print(num1,"+",num2 ,"=" ,multiplication(num1,num2))
    elif choice == 4:
        print(num1,"+",num2,"=",division(num1,num2))
        
        next_calculation = input("Let's do next calculation? (yes/no): ")
        if next_calculation == "no":
            break
    else:
        print("Invalid Input")