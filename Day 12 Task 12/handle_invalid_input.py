# 1 .Write a program that handles invalid input by using try and except blocks. 

try:
    num = int(input("Enter a Number : "))
    result = 5/num
    print(result)
except:
    print("Invalid Input ! Please Enter a Numeric value")
    
finally:
    print("program execution completed.")