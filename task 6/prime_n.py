def is_prime(number):
    if number <= 1:
        return False  # Numbers less than or equal to 1 are not prime
    for i in range(2, int(number ** 0.5) + 1):  # Check divisibility from 2 to sqrt(number)
        if number % i == 0:
            return False  # If divisible, it's not a prime number
    return True  # If no divisors found, it's a prime number


number = int(input("Enter a number: "))
if is_prime(number):
    print(f"{number} is a prime number.")
else:
    print(f"{number} is not a prime number.")
