#Debugging Technique using pdb is Python’s built-in debugging tool.pdb is Python’s built-in debugging tool

def divide_numbers(a, b):
    import pdb; pdb.set_trace()  # Pause here
    return a / b

result = divide_numbers(10, 2)
print(result)
