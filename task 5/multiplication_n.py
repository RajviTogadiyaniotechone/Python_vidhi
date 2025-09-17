#Write a for loop that prints a multiplication table for a given number.
number = int(input("Enter a number :"))
print(number)
for i in range(1,11):
    print(number,"x",i,"=",number*i)