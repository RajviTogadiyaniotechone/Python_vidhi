#Sudoku Solver (Backtracking) 

def print_grid(arr):
    for i in range(9):
        for j in range(9):
            print(arr[i][j],end=" ")
        print()
        
def slove(grid,row,col,num):
   
    for x in range(9):
        if grid[row][x] == num :
            return False
           
    for x in range(9):
        if grid[x][col] == num:
            return False
        
    start_row = 3*(row//3)
    start_col = 3*(col//3)
    for i in range(3):
        for j in range(3):
            if grid[i + start_row][j + start_col] == num:
                return False
    return True
  
def sudoku(grid):
    for row in range(9):
        for col in range(9):
            if grid[row][col] == 0:
                # Try numbers from 1 to 9
                for num in range(1, 10):
                    if slove(grid, row, col, num):
                        grid[row][col] = num
                        
                        # Recursively try to solve the rest of the grid
                        if sudoku(grid):
                            return True
                        
                        # Backtrack if placing the number didn't work
                        grid[row][col] = 0
                
                # If no number works, return False
                return False
    
    # If the grid is completely filled, return True
    return True

grid =[
    [2, 5, 0, 0, 3, 0, 9, 0, 1],
    [0, 1, 0, 0, 0, 4, 0, 0, 0],
    [4, 0, 7, 0, 0, 0, 2, 0, 8],
    [0, 0, 5, 2, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 9, 8, 1, 0, 0],
    [0, 4, 0, 0, 0, 3, 0, 0, 0],
    [0, 0, 0, 3, 6, 0, 0, 7, 2],
    [0, 7, 0, 0, 0, 0, 0, 0, 3],
    [9, 0, 3, 0, 0, 0, 6, 0, 4]
]

print(grid)     
if sudoku(grid):
    print("\nSudoku solved:")
    print_grid(grid)
else:
    print("No solution exists.")
       
       

"""
Explaination of this code 
Sudoku solved:
5 3 4 6 7 8 9 1 2
6 7 2 1 9 5 3 4 8
1 9 8 3 4 2 5 6 7
8 5 9 7 6 1 4 2 3
4 2 6 8 5 3 7 9 1
7 1 3 9 2 4 8 5 6
9 6 1 5 3 7 2 8 4
2 8 7 4 1 9 6 3 5
3 4 5 2 8 6 1 7 9"""

"""Function Definitions
1. print_grid(arr)

def print_grid(arr):
    for i in range(9):
        for j in range(9):
            print(arr[i][j], end=" ")
        print()
Purpose: This function prints the Sudoku grid in a readable format.
Explanation:
for i in range(9): Loops through each row.
for j in range(9): Loops through each column in the current row.
print(arr[i][j], end=" "): Prints the current cell value, followed by a space, so that the numbers are in a grid format.
print(): Adds a new line after each row to properly display the Sudoku grid.
2. slove(grid, row, col, num)

def slove(grid, row, col, num):
    for x in range(9):
        if grid[row][x] == num:
            return False
           
    for x in range(9):
        if grid[x][col] == num:
            return False
        
    start_row = 3 * (row // 3)
    start_col = 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if grid[i + start_row][j + start_col] == num:
                return False
    return True
Purpose: This function checks whether placing a number (num) in a specific cell (row, col) is valid according to Sudoku rules.
Explanation:
Row Check: The first for loop iterates over all columns in the specified row to see if the number already exists in that row. If it does, return False.
Column Check: The second for loop iterates over all rows in the specified column to check if the number is already present. If it is, return False.
Subgrid Check:
start_row and start_col calculate the starting index of the 3x3 subgrid that contains the current cell (row, col). The subgrid is determined by integer division (row // 3 and col // 3).
The two nested loops check each cell in the 3x3 subgrid for the number. If it is found, return False.
If the number is valid (not in the row, column, or subgrid), return True.
3. sudoku(grid)

def sudoku(grid):
    for row in range(9):
        for col in range(9):
            if grid[row][col] == 0:
                # Try numbers from 1 to 9
                for num in range(1, 10):
                    if slove(grid, row, col, num):
                        grid[row][col] = num
                        
                        # Recursively try to solve the rest of the grid
                        if sudoku(grid):
                            return True
                        
                        # Backtrack if placing the number didn't work
                        grid[row][col] = 0
                
                # If no number works, return False
                return False
    
    # If the grid is completely filled, return True
    return True
Purpose: This function solves the Sudoku puzzle using the backtracking algorithm.
Explanation:
The outer loop (for row in range(9)) iterates through each row of the grid.
The inner loop (for col in range(9)) iterates through each column in the current row.
If the cell is empty (grid[row][col] == 0), it tries placing numbers 1 to 9 in the cell.
slove(grid, row, col, num) is called to check if placing the current number is valid.
If valid, the number is placed in the cell (grid[row][col] = num).
The function then calls itself recursively (sudoku(grid)) to solve the rest of the puzzle. If it succeeds, the function returns True, meaning the puzzle is solved.
If placing the number didn't lead to a solution, the function backtracks by resetting the current cell to 0 (grid[row][col] = 0) and tries the next number.
If no valid number can be placed in an empty cell, the function returns False to indicate that no solution is possible from the current state.
If the grid is completely filled (i.e., no empty cells), the function returns True, indicating that the puzzle is solved.
Main Program
4. Initializing the Grid and Solving

grid = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]
Purpose: This defines the initial state of the Sudoku grid, where 0 represents empty cells.
5. Printing the Initial Grid

print(grid)     
Purpose: This line prints the initial grid to the console. However, you may want to use print_grid(grid) here to print it in a readable format.
6. Solving the Sudoku and Printing the Result

if sudoku(grid):
    print("Sudoku solved:")
    print_grid(grid)
else:
    print("No solution exists.")
Explanation:
The sudoku(grid) function is called to try solving the grid.
If the function returns True, it means the puzzle was solved, and the solved grid is printed using print_grid(grid).
If sudoku(grid) returns False, it means the puzzle cannot be solved (though this will not occur for a valid Sudoku puzzle).
Example Output
Given the input grid, the program will output:

plaintext
Copy
Edit
Sudoku solved:
5 3 4 6 7 8 9 1 2 
6 7 2 1 9 5 3 4 8 
1 9 8 3 4 2 5 6 7 
8 5 9 7 6 1 4 2 3 
4 2 6 8 5 3 7 9 1 
7 1 3 9 2 4 8 5 6 
9 6 1 5 3 7 2 8 4 
2 8 7 4 1 9 6 3 5 
3 4 5 2 8 6 1 7 9 
Summary
print_grid: Prints the Sudoku grid in a readable format.
slove: Checks if placing a number in a specific cell is valid.
sudoku: Solves the Sudoku puzzle using backtracking by recursively trying numbers and backtracking if a number doesn’t work.
Main Program: Initializes the grid, calls the sudoku function to solve it, and prints the solved grid or a message if no solution exists.

"""

