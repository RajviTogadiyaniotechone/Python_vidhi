# 1.Use the random module to simulate a dice roll. 

import random

while True :
    print("1.rool the dice")
    print("2.exit")
    
    user = int(input("select your choice :"))
    
    if user == 1:
        number = random.randint(1,6)
        print(f"you rolled a dice is {number}!")
        print("----------------------------------")
    else:
        break
    
