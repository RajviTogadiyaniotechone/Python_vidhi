#Build a simple project such as a calculator that can add, subtract, multiply, and divide numbers. 
def addition(n1,n2):
    return n1+n2

def subtraction(n1,n2):
    return n1-n2

def multiplication(n1,n2):
    return n1*n2

def division(n1,n2):
    return n1/n2


print("select operations :")
print("1. Addition (+) ")
print("2. Subtraction (-)")
print("3. Multiplication (*)")
print("4. Division (/)")

while True:
    
    choice = input("Enter a choice of operation +/-/*// : ")

    if choice in ('+', '-', '*', '/'):
        try:
            num1 = float(input("Enter  first number: "))
            num2 = float(input("Enter second number: "))
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue
        
    
    if choice == "+" :
        print(num1 ,"+", num2 , "=" , addition(num1,num2)) 
    elif choice == "-":
        print(num1 ,"-", num2 ,"=" ,subtraction(num1,num2)) 
    elif choice == "*":
        print(num1,"*",num2 ,"=" ,multiplication(num1,num2))
    elif choice == "/":
        print(num1,"/",num2,"=",division(num1,num2))
        
        next_calculation = input("Let's do next calculation? (yes/no): ")
        if next_calculation == "no":
            break
    else:
        print("Invalid Input")
        