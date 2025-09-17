#write a program that checks if a given year is a leap year.

year = int (input("Entre a year :"))

if year % 400 == 0:
    print(f"This {year} is leap year")
elif year % 100 == 0:
    print(f"This {year} is not leap year")
elif year % 4 == 0:
    print(f"This {year} is  leap year")
else :
    print(f"This {year} is not leap year")