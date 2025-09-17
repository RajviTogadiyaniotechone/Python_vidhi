# Detail : Matrix Multiplication (Strassen's Algorithm)

import numpy as np

def add(A, B):
    return np.add(A, B)

def subtract(A, B):
    return np.subtract(A, B)

# Strassen's Algorithm for Matrix Multiplication
def strassen(A, B):
    # Base case when matrix size is 1x1
    if len(A) == 1:
        return A * B
    
    # Split the matrices A and B into four submatrices
    mid = len(A) // 2
    A11 = A[:mid, :mid]
    A12 = A[:mid, mid:]
    A21 = A[mid:, :mid]
    A22 = A[mid:, mid:]
    
    B11 = B[:mid, :mid]
    B12 = B[:mid, mid:]
    B21 = B[mid:, :mid]
    B22 = B[mid:, mid:]
    
    # 7 products according to Strassen's formula
    M1 = strassen(A11, subtract(B12, B22))
    M2 = strassen(add(A11, A12), B22)
    M3 = strassen(add(A21, A22), B11)
    M4 = strassen(A22, subtract(B21, B11))
    M5 = strassen(add(A11, A22), add(B11, B22))
    M6 = strassen(subtract(A12, A22), add(B21, B22))
    M7 = strassen(subtract(A11, A21), add(B11, B12))
    
    # Compute the result matrix C by combining the M1 to M7
    C11 = add(subtract(add(M5, M4), M2), M6)
    C12 = add(M1, M2)
    C21 = add(M3, M4)
    C22 = add(subtract(add(M5, M1), M3), M7)
    
    # Combine the 4 submatrices into the final matrix
    C = np.zeros((len(A), len(B[0])))
    C[:mid, :mid] = C11
    C[:mid, mid:] = C12
    C[mid:, :mid] = C21
    C[mid:, mid:] = C22
    
    return C

# Function to take input matrix from user
def take_matrix_input(rows, cols):
    matrix = []
    print(f"Enter the elements of the {rows}x{cols} matrix:")
    for i in range(rows):
        row = list(map(int, input(f"Enter row {i+1} (space-separated): ").split()))
        matrix.append(row)
    return np.array(matrix)

# Get matrix dimensions and elements from user
def get_matrices():
    
    print("Matrix A:")
    rows_A = int(input("Enter the number of rows for matrix A: "))
    cols_A = int(input("Enter the number of columns for matrix A: "))
    A = take_matrix_input(rows_A, cols_A)

    print("Matrix B:")
    rows_B = int(input("Enter the number of rows for matrix B: "))
    cols_B = int(input("Enter the number of columns for matrix B: "))
    B = take_matrix_input(rows_B, cols_B)

    # Check if multiplication is possible (i.e., columns of A == rows of B)
    if cols_A != rows_B:
        print("Matrix multiplication is not possible. The number of columns in A must equal the number of rows in B.")
        return None, None
    
    return A, B


A, B = get_matrices()
if A is not None and B is not None:
    result = strassen(A, B)


print("\nMatrix A (as an array):")
print(np.array(A))
print("\nMatrix B (as an array):")
print(np.array(B))
print("\nThe resulting matrix (as an array) is:")
print(result)
