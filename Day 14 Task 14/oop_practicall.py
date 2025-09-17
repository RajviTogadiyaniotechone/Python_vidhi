"""- Create a class called Car with attributes like make, model, and year. 
- Write methods in the class to display the car’s details. 
- Create a subclass ElectricCar that inherits from Car and adds an additional battery_size attribute."""

class car:
    def __init__(self,make,model,year):
        self.make = make
        self.model = model
        self.year = year
        
    def display_detail(self):
        print(f"car detail is :: {self.make} {self.model} {self.year}")
    
class ElectricCar(car):

    def __init__(self, make, model, year,battery_size):
        super().__init__(make, model, year)
        self.battery_size = battery_size
        
    def e_display_detail(self):
        super().display_detail()
        print(f"Battery size is :: {self.battery_size}")

my_car = ElectricCar("Toyota","corolla",2020,100)
my_car.display_detail()

my_car.e_display_detail()
print("------------------")
my_e_car = ElectricCar("Tesla","model s",2022,200)
my_e_car.e_display_detail()