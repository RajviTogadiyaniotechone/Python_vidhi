import random 

name = input("Enter Your Name ::")

print("Good luck!",name)

words = ["water","rain","rainbow","computer","mouse","tablate","drink","pin","pig"
         "python","player","learn","condition","keyboard","bottle","open"]

word  = random.choice(words)

print("Guess the characters")

guess = ""
turns = 10

while turns > 0:
    failed = 0 
    
    for char in word:
        
        if char in guess:
            print(char, end="")
        else:
            print("_")
            failed += 1
    if failed == 0:
        print("\nyou win!")
        print("The word is::", word)
        break
    
    print()
    guess1 = input("guess a character:")
    
    guess += guess1
    
    if guess not in word:
        turns -= 1
        print("wrong")
        print("You have", + turns, 'more guesses')

        if turns == 0:
            print("You Loose")
    