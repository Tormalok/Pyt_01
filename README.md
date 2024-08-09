# Route Finder Documentation (Mini)

## Overview

The Route Finder is a Python program that calculates the shortest path between various landmarks on the University of Ghana campus. It utilizes the Mapbox API to retrieve distance and duration matrices for driving and walking routes. The program then visualizes these paths using the NetworkX library and displays them graphically with Matplotlib.  
The program uses several algorithms and techniques to achieve the desired functionality. Below is a list of these algorithms, along with an explanation of their techniques and how they contribute to the program's efficiency:

### 1. Dijkstra's Algorithm

- **Technique Used**: This algorithm is used for finding the shortest paths between nodes in a graph, which may represent, for example, road networks. It is implemented in NetworkX as `nx.dijkstra_path`.

- **Usage in Program**: In the function `find_shortest_path_with_waypoints`, Dijkstra's algorithm is employed to find the shortest path based on the travel mode (driving or walking). The weights used for the graph are `duration_car` for driving and `duration_walking` for walking.

- **Efficiency Contribution**: Dijkstra's algorithm is well-suited for graphs with non-negative weights, offering a time complexity of \(O((V + E) \log V)\), where \(V\) is the number of vertices and \(E\) is the number of edges. This ensures that the shortest path is found efficiently, even in relatively large graphs.

### 2. Cross Product for Distance Calculation

- **Technique Used**: The program calculates the perpendicular distance from a node to a line segment using the cross product. This is a geometric approach used to find the shortest distance from a point to a line.

- **Usage in Program**: In the `find_shortest_path_with_waypoints` function, the distance from a node to the line connecting the start and end nodes is calculated using the cross product. This helps in identifying the nearest node to include as a waypoint in case the path is direct (only includes the start and end nodes).

- **Efficiency Contribution**: By calculating the perpendicular distance, the program ensures that the path found is not only short in terms of total distance but also optimizes the route in the context of geographical layout, leading to more realistic pathfinding.

### 3. Greedy Algorithm for Path with Waypoints

- **Technique Used**: A greedy algorithm is used to construct a path that includes specific waypoints. The algorithm finds the shortest path between consecutive waypoints, ensuring that each segment of the journey is optimized.

- **Usage in Program**: When the user specifies waypoints in the `find_shortest_path_with_waypoints` function, the program calculates the shortest path between each consecutive pair of waypoints using a greedy approach. It then combines these segments to form the full path.

- **Efficiency Contribution**: The greedy algorithm simplifies the process of waypoint routing by optimizing each segment independently. While it may not always produce the global optimum, it is efficient and effective for the purpose of including waypoints in the route.

### 4. Graph Construction and Edge Weighting

- **Technique Used**: The program constructs a graph where nodes represent landmarks, and edges represent the paths between them. Each edge is weighted based on travel distance and duration, corresponding to the selected mode of transportation.

- **Usage in Program**: The graph is constructed in the main section of the program using `NetworkX`. Nodes are added with their positions and names, and edges are added with weights for driving and walking modes (`distance_car`, `duration_car`, `distance_walking`, `duration_walking`).

- **Efficiency Contribution**: Proper graph construction ensures that shortest path algorithms, like Dijkstra's, operate efficiently. By accurately weighting edges, the program can reliably find the shortest and most appropriate routes based on the selected travel mode.

### 5. API Integration

- **Technique Used**: The program integrates with the Mapbox API to retrieve up-to-date distance and duration data between landmarks. This offloads complex geographical calculations to the API and ensures accuracy.

- **Usage in Program**: The `get_mapbox_matrix` function sends a request to the Mapbox API, which returns matrices of distances and durations for the specified landmarks and travel mode. This data is then used to weight the edges of the graph.

- **Efficiency Contribution**: By leveraging the Mapbox API, the program ensures accurate and current data for route calculations. This approach also improves efficiency by delegating complex computations to a specialized service.

### 6. Path Visualization

- **Technique Used**: The program visualizes the graph and the computed shortest path using the `Matplotlib` library. Nodes and edges are drawn on a plot, with the shortest path highlighted for clarity.

- **Usage in Program**: After computing the shortest path, the program uses `Matplotlib` to create a visual representation of the entire graph. It highlights the selected path, labels nodes with their names, and annotates edges with their respective weights (distance and duration).

- **Efficiency Contribution**: Visualization provides an intuitive way for users to understand the route, making it easier to interpret the results. While this does not directly contribute to algorithmic efficiency, it enhances the usability and accessibility of the program.

### 7. Interactive User Interface

- **Technique Used**: The program employs a simple command-line interface to interact with the user. This interface guides the user through selecting the start and end points, the travel mode, and any waypoints.

- **Usage in Program**: The interactive part of the program is handled in the `main()` function, where the user is prompted to make selections and input data. The program then processes this input and provides the corresponding route and visualization.

- **Efficiency Contribution**: The interactive interface ensures that users can easily provide input and receive results without needing to understand the underlying code. This improves the overall user experience and makes the program more accessible to non-technical users.
