#2.Use the math module to calculate the square root of a number. 

import math

def square(number):
    return math.sqrt(number)

num = int(input("Enter a number :"))
result = square(num)

print(f"The square root of {num} is {result}")
