import math

def prime_factors(n):
    factors = []

    # Step 1: Check for divisibility by 2
    while n % 2 == 0:
        factors.append(2)
        n //= 2
    
    # Step 2: Check for divisibility by odd numbers up to the square root of n
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        while n % i == 0:
            factors.append(i)
            n //= i
    
    # Step 3: If n is still greater than 2, then it is a prime factor
    if n > 2:
        factors.append(n)
    
    return factors

number = int(input("Enter a number to find its prime factors: "))

print(f"The prime factors of {number} are: {prime_factors(number)}")


