def is_num_divisible_3(num):
    if num % 3 == 0 :
        return True
    else:
        return False
    
number = int(input("Enter a number :"))

if is_num_divisible_3(number):
    print(f"{number} is divisible by 3")
else:
    print(f"{number} is not divisible by 3")
    