#0/1 knapsack problem

def knapSack(W, wt, val):
    n = len(wt)
    
    k = []
    for i in range(n + 1): 
        row = []  # Create a new row
        for j in range(W + 1): 
            row.append(0) 
        k.append(row)  # Add the row to the k table
    
  
    for i in range(n + 1): 
        for w in range(W + 1):                            
            if i == 0 or w == 0:                                    
                k[i][w] = 0  
            elif wt[i - 1] <= w:
                k[i][w] = max(val[i - 1] + k[i - 1][w - wt[i - 1]], k[i - 1][w])
            else:
                k[i][w] = k[i - 1][w]
    
    return k[n][W]

profit = list(map(int, input("Enter the profit values of the items (comma-separated): ").split(',')))  # Values of the items
weight = list(map(int, input("Enter the weights of the items (comma-separated): ").split(',')))  # Weights of the items
W = int(input("Enter the capacity of the knapsack: ")) 


print("Maximum value that can be obtained: ", knapSack(W, weight, profit))
