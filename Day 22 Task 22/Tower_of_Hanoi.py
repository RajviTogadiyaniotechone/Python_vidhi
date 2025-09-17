#Tower of Hanoi (Recursive Solution)

def tower_of_hanoi(n, source, target, auxiliary):

    if n == 1:
        print(f"Move disk 1 from {source} to {target}")
        return
    # Recursive case: Move n-1 disks from source to auxiliary
    tower_of_hanoi(n - 1, source, auxiliary, target)
    
    # Move the nth disk from source to target
    print(f"Move disk {n} from {source} to {target}")
    
    # Move the n-1 disks from auxiliary to target
    tower_of_hanoi(n - 1, auxiliary, target, source)


n = int(input("Enter the number of disks: "))

tower_of_hanoi(n, 'A', 'C', 'B')





