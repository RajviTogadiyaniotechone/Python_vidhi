def is_palindrome(s: str) -> bool:
    n = len(s)
    
    # Create a 2D DP table initialized to False
    dp = [[False] * n for _ in range(n)]
    
    for i in range(n):
        dp[i][i] = True
    
    # Check for substrings of length 2
    for i in range(n - 1):
        if s[i] == s[i + 1]:
            dp[i][i + 1] = True
    
    
    for length in range(3, n + 1):  
        for i in range(n - length + 1):
            j = i + length - 1
            # A substring is a palindrome if the first and last characters are equal
            # and the inner substring is also a palindrome
            if s[i] == s[j] and dp[i + 1][j - 1]:
                dp[i][j] = True
    
    # The entire string is a palindrome if dp[0][n-1] is True
    return dp[0][n - 1]

s = input("Enter a string: ")

if is_palindrome(s):
    print(f'"{s}" is a palindrome.')
else:
    print(f'"{s}" is not a palindrome.')