#3.Write a program to generate a random password using the string and random modules.
import string
import random 

all_characters = string.ascii_letters + string.digits + string.punctuation

length = int(input("Enter a length of password :"))

password = ''.join(random.choices(all_characters,k=length))

print("your password is ::",password)