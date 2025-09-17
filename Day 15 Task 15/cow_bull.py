import random

def get_feedback(secret, guess):
    bulls = 0
    cows = 0
    secret_list = list(secret)
    guess_list = list(guess)
    

    for i in range(len(secret)):
        if secret[i] == guess[i]:
            bulls += 1
            secret_list[i] = None  
            guess_list[i] = None
    

    for i in range(len(secret)):
        if guess_list[i] is not None and guess_list[i] in secret_list:
            cows += 1
            secret_list[secret_list.index(guess_list[i])] = None  
    
    return bulls, cows


def is_valid_number(number):
    return len(set(number)) == len(number)


def play_game():
 
    print("Player 1, please enter a 4-digit secret code with no repeated digits:")
    while True:
        secret_code = input("Enter your secret code: ")
        if len(secret_code) == 4 and secret_code.isdigit() and is_valid_number(secret_code):
            break
        else:
            print("Invalid input. Make sure it's a 4-digit number with no repeated digits.")
    
    print("\n" + "="*40)
    
  
    attempts = 0
    while True:
        attempts += 1
        guess = input(f"Attempt {attempts}: Player 2, enter your guess (4-digit number): ")
        
        if len(guess) == 4 and guess.isdigit():
            bulls, cows = get_feedback(secret_code, guess)
            
            print(f"Bulls: {bulls}, Cows: {cows}")
            
            if bulls == 4:
                print(f"Congratulations! You've cracked the code {secret_code} in {attempts} attempts.")
                break
        else:
            print("Invalid input. Make sure to enter a 4-digit number.")
        
        print("\n" + "="*40)

if __name__ == "__main__":
    play_game()
