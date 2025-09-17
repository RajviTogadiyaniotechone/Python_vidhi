import heapq  # to use the priority queue (min-heap)

def dijkstra(graph, start):
    
    distances = {node: float('inf') for node in graph}
    
    distances[start] = 0
    
    priority_queue = [(0, start)]
    
    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)
        
        if current_distance > distances[current_node]:
            continue
        
        for neighbor, weight in graph[current_node]:
            distance = current_distance + weight  
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(priority_queue, (distance, neighbor))
    
    return distances

def display_shortest_distances(graph, start_node):
    
    shortest_distances = dijkstra(graph, start_node)
    
    print(f"Shortest distances from {start_node}:")
    for node, distance in shortest_distances.items():
        print(f"  {node}: {distance}")

graph = {
    'A' : [('B',4),('C',8)],
    'B' : [('D',8),('C',11)],
    'D' : [('I',2),('E',7),('G',4)],
    'C' : [('H',1),('I',7)],
    'E' : [('F',9),('G',14)], 
    'F' : [], 
    'G' : [('F',10)],
    'H' : [('G',2)],
    'I' : [('H',6)]     
}
start_node = 'A'

display_shortest_distances(graph, start_node)
