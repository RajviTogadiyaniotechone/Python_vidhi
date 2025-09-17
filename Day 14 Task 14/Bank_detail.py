#Create a class representing a simple Bank Account.

class BankAccount:
    def __init__(self,account_no,balance = 0):
        self.account_no = account_no
        self.balance = balance
    
    def deposite(self,amount):
  
        if amount > 0:
            self.balance += amount
            print(f"Deposited: {amount}")
        else:   
            print("Deposit amount must be positive.")
    
    def withdraw(self,amount):
        if amount <= 0:
            print("Withdrawal amount must be positive.")
        elif amount > self.balance:
            print("Insufficient funds.")
        else:
            self.balance -= amount
            print(f"Withdrawn: {amount}")
         
  
    def get_balance(self):
        return self.balance
    

account_no = int(input("Enter your Account no ::"))
balance = float(input("Enter your balance ::"))
 
c = BankAccount(account_no , balance) 

d_amount  = float(input("Enter amount to be deposite ::"))
c.deposite(d_amount)
w_amount =  float(input("Enter amount to be withdraw ::"))
c.withdraw(w_amount)

print(f"current balance : {c.get_balance()}")
