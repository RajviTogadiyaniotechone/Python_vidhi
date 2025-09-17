#Palindrome Check (Dynamic Programming)
def is_palindrome(s: str) -> bool:
    n = len(s)
    if n == 0:
        return True  
    
    # Initialize DP table
    dp = [[False] * n for _ in range(n)]

    # Every single character is a palindrome
    for i in range(n):
        dp[i][i] = True

    # Check substrings of length 2 or more
    for length in range(2, n + 1):  # Length of substring
        for i in range(n - length + 1):
            j = i + length - 1  # End index of substring
            
            if s[i] == s[j]:
                if length == 2:
                    dp[i][j] = True  # Two-character substrings are palindromes if both characters match
                else:
                    dp[i][j] = dp[i + 1][j - 1]  # Check inner substring

    return dp[0][n - 1]  

s = input("Enter a string: ")

if is_palindrome(s):
    print(f'"{s}" is a palindrome.')
else:
    print(f'"{s}" is not a palindrome.')
    
