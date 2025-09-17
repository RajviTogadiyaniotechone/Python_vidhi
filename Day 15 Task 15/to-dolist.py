#Create a To-Do list application where users can add, edit, and delete tasks

class TodoList():
    def __init__(self):
        self.tasks = []
        
    def display_task(self):
        if not self.tasks:
            print("No task in list")
        else:
            print("/n your to-do list")
            for i,task in enumerate(self.tasks,1):
                print(f"{i}.{task}")
        
    def add_task(self):
        task = input("Enter a Task ::")
        self.tasks.append(task)
        print("Task added successfuly")
    
    def edit_task(self):
        if self.tasks:
            self.display_task()
            try :
                task_index = int(input("\n Enter the number of the task you want to edit::"))
                if task_index <= 0 or task_index > len(self.tasks):
                    print("Invalid Task Number!")
                else:
                    new_task = input("Enter a update task :")
                    self.tasks[task_index - 1] = new_task
                    print("Task edied successfuly")
                        
            except ValueError :
                print("Please Enter a valid number")
    
    def delete_task(self):
        if self.tasks:
            self.display_task()
            try:
                task_index = int(input("Enter a number you want to delete the task ::"))
                if task_index <= 0 or task_index > len(self.tasks):
                    print("invalid number!")
                else:
                    self.tasks.pop(task_index - 1)
                    print("task deleted!")
            except ValueError:
                print("Please enter a valid number")
        else:
            print("No task avaliable to delete")
            
    def run(self):
        
        while True:
            print("\n To-Do List Menu")
            print("1.Display Task")
            print("2.Add Task")
            print("3.Edit Task")
            print("4.Delete Task")
            print("5.Exit")            
        
            choice = input("\nEnter a option :")
            
            if choice == '1':
                self.display_task()
            elif choice == '2':
                self.add_task()
            elif choice == '3':
                self.edit_task()
            elif choice == '4':
                self.delete_task()
            elif choice == '5':
                print("Exiting the application GoodBye!")
                break
            else:
                print("Invalid choice! Please choose a valid option.")
                
to_do_list = TodoList()
to_do_list.run()