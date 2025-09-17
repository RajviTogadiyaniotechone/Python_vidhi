# 2.Create a program that divides two numbers and handles division by zero.

num1 = float(input("Enter a first number::"))
num2 = float(input("Enter a second number::"))

try:
    result = num1 / num2 
    
    print("Answer :",result)
except  ZeroDivisionError:
    print("Division by zero is not allowed.")
except ValueError:
    print("Invalid Input! Please Enter Valid Number")
