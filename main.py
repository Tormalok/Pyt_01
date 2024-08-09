import os
from dotenv import load_dotenv
import requests
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

load_dotenv()

# Your Mapbox API key
mapbox_api_key = os.getenv('MAPBOX_API_KEY')

# List of coordinates of landmarks (latitude, longitude) and their names
landmarks = [
    (5.65188, -0.18683, 'Balme Library'),
    (5.65142, -0.18549, 'Department of Physics'),
    (5.65450, -0.18368, 'Department of Computer Science'),
    (5.64050, -0.16750, 'Great Hall'),
    (5.63900, -0.16650, 'University Square'),
    (5.64000, -0.16700, 'Commonwealth Hall'),
    (5.64020, -0.16680, 'Legon Hall'),
    (5.64080, -0.16730, 'Mensah Sarbah Hall'),
    (5.64050, -0.16800, 'Nkrumah Hall'),
    (5.63850, -0.16500, 'University Hospital'),
    (5.63990, -0.16600, 'Institute of African Studies'),
    (5.63800, -0.16400, 'Noguchi Memorial Institute for Medical Research'),
    (5.63850, -0.16550, 'School of Public Health'),
    (5.63930, -0.16640, 'Department of Geography and Resource Development'),
    (5.63970, -0.16710, 'Department of Psychology'),
    (5.63950, -0.16690, 'Department of Sociology'),
    (5.63980, -0.16720, 'Department of Political Science'),
    (5.63850, -0.16800, 'Sports Fields'),
    (5.63920, -0.16780, 'University Guest Centre'),
    (5.63800, -0.16850, 'UG Sports Stadium'),
    (5.64000, -0.16800, 'Botanical Gardens'),
    (5.63930, -0.16850, 'Athletic Oval'),
    (5.63940, -0.16780, 'Legon Pool Side'),
    (5.64960, -0.18720, 'University of Ghana Business School'),
]

# Extract coordinates and names
coordinates = [(lat, lon) for lat, lon, name in landmarks]
names = [name for lat, lon, name in landmarks]

# Convert coordinates to the required format for Mapbox
locations = ["{:.6f},{:.6f}".format(lon, lat) for lat, lon in coordinates]
loc_string = ";".join(locations)  # Semicolon-separated string of coordinates

# Function to make Mapbox API call for the matrix
def get_mapbox_matrix(locations, profile):
    url = f"https://api.mapbox.com/directions-matrix/v1/mapbox/{profile}/{locations}"
    params = {
        'annotations': 'duration,distance',
        'access_token': mapbox_api_key
    }
    call = requests.get(url, params=params)
    
    if call.status_code == 200:
        return call.json()
    else:
        raise Exception(f"Error: {call.status_code}, {call.reason}")

# Get matrices for driving-car and walking
matrix_car = get_mapbox_matrix(loc_string, 'driving')
matrix_walking = get_mapbox_matrix(loc_string, 'walking')

# Extract distances (in meters) and durations (in seconds)
distances_car = matrix_car['distances']
durations_car = matrix_car['durations']
distances_walking = matrix_walking['distances']
durations_walking = matrix_walking['durations']

# Create a graph using NetworkX
G = nx.Graph()

# Add nodes with positions and names
for i, (coord, name) in enumerate(zip(coordinates, names)):
    G.add_node(i, pos=coord, label=name)

# Add edges with distances and durations as weights
for i in range(len(distances_car)):
    for j in range(len(distances_car[i])):
        if i != j and distances_car[i][j] is not None:  # Avoid self-loops and null values
            G.add_edge(i, j, distance_car=distances_car[i][j] / 1000,  # Convert meters to kilometers
                       duration_car=durations_car[i][j] / 60,  # Convert seconds to minutes
                       distance_walking=distances_walking[i][j] / 1000,
                       duration_walking=durations_walking[i][j] / 60)

# Function to find shortest path with optional waypoints
def find_shortest_path_with_waypoints(start, end, mode, waypoints=None):
    if waypoints is None:
        # Find the shortest path directly
        if mode == 1:
            path = nx.dijkstra_path(G, source=start, target=end, weight='duration_car')
        else:
            path = nx.dijkstra_path(G, source=start, target=end, weight='duration_walking')
        
        # Check if the path is direct (i.e., includes only start and end nodes)
        if len(path) == 2:
            # If it's a walking route, add an intermediate node
            if mode == 2:
                nearest_node = None
                shortest_distance = float('inf')
                
                for node in G.nodes():
                    if node != start and node != end:
                        # Calculate the distance from the node to the line connecting start and end
                        distance_to_line = np.abs(np.cross(np.array(G.nodes[end]['pos']) - np.array(G.nodes[start]['pos']),
                                                           np.array(G.nodes[start]['pos']) - np.array(G.nodes[node]['pos']))) / np.linalg.norm(np.array(G.nodes[end]['pos']) - np.array(G.nodes[start]['pos']))
                        if distance_to_line < shortest_distance:
                            nearest_node = node
                            shortest_distance = distance_to_line
                
                if nearest_node is not None:
                    # Find a new path including the nearest node
                    new_path = nx.shortest_path(G, source=start, target=nearest_node, weight='duration_walking')
                    new_path += nx.shortest_path(G, source=nearest_node, target=end, weight='duration_walking')[1:]
                    path = list(dict.fromkeys(new_path))  # Remove duplicates
    else:
        # Create a path with waypoints
        all_nodes = [start] + waypoints + [end]
        path = []
        for i in range(len(all_nodes) - 1):
            segment = nx.shortest_path(G, source=all_nodes[i], target=all_nodes[i + 1], 
                                       weight='duration_' + ('car' if mode == 1 else 'walking'))
            if i == 0:
                path.extend(segment)
            else:
                path.extend(segment[1:])  # Avoid duplicating the starting node
        path = list(dict.fromkeys(path))  # Remove duplicates
    return path


# Interactive part for user input
def main():
    while True:
        print("\nWelcome to the Route Finder!")
        print("1. Find shortest path automatically")
        print("2. Find shortest path with specific waypoints")
        print("3. Quit")

        choice = input("Choose an option (1, 2, or 3): ")
        if choice == '1' or choice == '2':
            # Display all landmarks with their associated numbers
            print("\nLandmarks:")
            for i, name in enumerate(names):
                print(f"Node {i}: {name}")

            # Get user input for start and end locations
            try:
                start = int(input("\nEnter the number for the start location: "))
                end = int(input("Enter the number for the end location: "))
                print("Select the mode of travel:")
                print("1: Driving")
                print("2: Walking")
                mode = int(input("Enter the number for your preferred mode of travel: "))
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue
            
            # Initialize waypoints based on choice
            waypoints = []
            if choice == '2':
                waypoints_input = input("Enter the numbers of waypoints to include, separated by commas (e.g., 1,3,5): ")
                if waypoints_input:
                    waypoints = list(map(int, waypoints_input.split(',')))
                
            # Find the shortest path
            path = find_shortest_path_with_waypoints(start, end, mode, waypoints)
            path_length = nx.path_weight(G, path, 'duration_' + ('car' if mode == 1 else 'walking'))
            path_distance = sum(G[u][v]['distance_' + ('car' if mode == 1 else 'walking')] for u, v in zip(path[:-1], path[1:]))
            travel_mode = "driving" if mode == 1 else "walking"
            
            # Display the shortest path and its distance
            print(f"\nThe shortest path from Node {start} to Node {end} is:")
            for node in path:
                print(f"Node {node}: {G.nodes[node]['label']}")
            
            # Convert path length to hours and minutes
            path_length_minutes = round(path_length)
            if path_length_minutes >= 60:
                hours = path_length_minutes // 60
                minutes = path_length_minutes % 60
                time_str = f"{hours} hour(s) {minutes} min(s)"
            else:
                time_str = f"{path_length_minutes} min(s)"
                
            print(f"Total distance: {path_distance:.2f} km")
            print(f"Total travel time: {time_str}")

            # Visualization
            pos = nx.get_node_attributes(G, 'pos')
            labels = nx.get_node_attributes(G, 'label')
            edge_labels = {(i, j): f"Car: {d['distance_car']:.1f}km, {d['duration_car']:.1f}min\nWalking: {d['distance_walking']:.1f}km, {d['duration_walking']:.1f}min"
                           for i, j, d in G.edges(data=True)}
            
            # Draw the entire graph
            plt.figure(figsize=(15, 10))
            nx.draw(G, pos, with_labels=False, node_size=500, node_color='skyblue', edge_color='gray')

            # Highlight the shortest path
            path_edges = list(zip(path, path[1:]))
            nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='green', width=2)

            # Draw node labels
            nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, font_color='black')

            # Draw edges with their weights
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)

            plt.title(f"Shortest Path from {G.nodes[start]['label']} to {G.nodes[end]['label']} by {travel_mode.capitalize()}")
            plt.show()

        elif choice == '3':
            print("Quitting the program. Have a great day!")
            break
        else:
            print("Invalid choice. Please choose 1, 2, or 3.")

if __name__ == "__main__":
    main()
