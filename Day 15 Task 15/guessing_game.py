#Write a number guessing game that generates a random number and asks the user to guess it.

import random

no_to_guess = random.randint(1,100)
attempt = 0

print("welcome to Number guessing game!")

while True :
    try:
        user_guess = int(input("Enter a number you want to guess::"))
        attempt += 1
        
        if user_guess < no_to_guess:
            print("low number! Try again")
        elif user_guess > no_to_guess:
            print("high number! Try again")
        else:
            print(f"Congratulations! You've guessed the correct number {no_to_guess} in {attempt} attempts.")
            break
    except ValueError:
        print("please Enter a valid number")