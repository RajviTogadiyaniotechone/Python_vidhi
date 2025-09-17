#Build a simple project such as a calculator that can add, subtract, multiply, and divide numbers. 

import logging
import os
from datetime import datetime


log_dir = r'D:\vidhi\Day 16 Task 16'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
    
# Create a logger
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)

# Create a file handler that appends to an existing file (in my case it is app.log)
log_file = os.path.join(log_dir, 'calculator1.log')
handler = logging.FileHandler(log_file, mode='a')
handler.setLevel(logging.DEBUG)

# Define the logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Attach the handler to the logger-
logger.addHandler(handler)

# Append new log messages
logger.info('This message will be appended to the existing log file')

# Record the start time
start_time = datetime.now()
start_time_detail = start_time.strftime("%m/%d/%Y %I:%M:%S %p")
logger.info(f"Calculator started ")

def addition(n1,n2):
    result = n1+n2
    logger.info(f"performing addition {n1} + {n2} = {result}")
    return result

def subtraction(n1,n2):
    try:
        result = n1-n2
        logger.info(f"performing substration {n1} - {n2} = {result}")
        return result
    except ValueError as e:
        logger.error(f"error : {e}")
        return str(e)
        
def multiplication(n1,n2):
    result = n1*n2
    logger.info(f"performing multiplication {n1} * {n2}  = {result}")
    return result

def division(n1,n2):
    try:
        result = num1/num2
        logger.info(f"performing division {n1} / {n2} = {result}")
    except ZeroDivisionError as e:
        logger.error(f"ZeroDivisionError error: {e}",exc_info=True)
    else:
        return result
          

print("------------------------")
print("select operations :")
print("1. Addition (+) ")
print("2. Subtraction (-)")
print("3. Multiplication (*)")
print("4. Division (/)")
print("------------------------")

while True:
    
    choice = input("\nEnter a choice of operation +/-/*// : ")

    if choice in ('+', '-', '*', '/'):
        try:
            num1 = float(input("Enter  first number: "))
            num2 = float(input("Enter second number: "))
        except ValueError as e:
            print("Invalid input. Please enter a number.")
            logger.error(f"value error {e}")
            continue
        
        if choice == "+" :
            result = addition(num1,num2)
            print(num1 ,"+", num2 , "=" , result) 
        elif choice == "-":
            result = subtraction(num1,num2)
            print(num1 ,"-", num2 ,"=" ,result) 
        elif choice == "*":
            result = multiplication(num1,num2)
            print(num1,"*",num2 ,"=" ,result)
        elif choice == "/":
            result = division(num1,num2)
            print(num1,"/",num2,"=",result)
            
    else :
        print("Invalid choice. Please select a valid operation.")
        logger.warning(f"Invalid choice!: {choice}")
        
    next_calculation = input("Let's do the next calculation? (yes/no): ")
    if next_calculation.lower() == "no":
        print("Exiting the calculator. Goodbye!")
        break
   
        
