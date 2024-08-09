import requests
import networkx as nx
import matplotlib.pyplot as plt

# Your ORS API key
api_key = '5b3ce3597851110001cf6248ea0a82eeeede4ffda9f40d106dacc46a'

# List of coordinates of landmarks (latitude, longitude) and their names
landmarks = [
  (5.65188, -0.18683, 'Balme Library'),
  (5.65142, -0.18549, 'Department of Physics'),
  (5.6545, -0.18368, 'Department of Computer Science'),
  (5.6405, -0.1675, 'Great Hall'),
  (5.639, -0.1665, 'University Square'),
  (5.64, -0.167, 'Commonwealth Hall'),
  (5.6402, -0.1668, 'Legon Hall'),
  (5.6408, -0.1673, 'Mensah Sarbah Hall'),
  (5.6405, -0.168, 'Nkrumah Hall'),
  (5.6385, -0.165, 'University Hospital'),
  (5.6399, -0.166, 'Institute of African Studies'),
  (5.638, -0.164, 'Noguchi Memorial Institute for Medical Research'),
  (5.6385, -0.1655, 'School of Public Health'),
  (5.6393, -0.1664, 'Department of Geography and Resource Development'),
  (5.6397, -0.1671, 'Department of Psychology'),
  (5.6395, -0.1669, 'Department of Sociology'),
  (5.6398, -0.1672, 'Department of Political Science'),
  (5.6385, -0.168, 'Sports Fields'),
  (5.6392, -0.1678, 'University Guest Centre'),
  (5.638, -0.1685, 'UG Sports Stadium'),
  (5.64, -0.168, 'Botanical Gardens'),
  (5.6393, -0.1685, 'Athletic Oval'),
  (5.6394, -0.1678, 'Legon Pool Side'),
  (5.6496, -0.1872, 'University of Ghana Business School'),
  (5.6511, -0.1862, 'Department of Mathematics'),
  (5.6491, -0.185, 'Department of Chemistry'),
  (5.6521, -0.1868, 'School of Engineering Sciences'),
  (5.6532, -0.1883, 'School of Pharmacy'),
  (5.6527, -0.1853, 'School of Law'),
  (5.6509, -0.186, 'Department of Statistics'),
  (5.6515, -0.1847, 'Department of Economics'),
  (5.6504, -0.1859, 'Department of Biological Sciences'),
  (5.6508, -0.1875, 'Department of Biochemistry, Cell and Molecular Biology'),
  (5.652, -0.187, 'Department of Nutrition and Food Science'),
  (5.6537, -0.1859, 'School of Agriculture'),
  (5.6518,
  -0.1835,
  'Institute of Statistical, Social and Economic Research (ISSER)'),
  (5.6524, -0.183, 'School of Communication Studies'),
  (5.648, -0.1843, 'Volta Hall'),
  (5.649, -0.1838, 'Akuafo Hall'),
  (5.6485, -0.184, 'Commonwealth Hall New Annex'),
  (5.6487, -0.1839, 'Legon Hall Annex A'),
  (5.6482, -0.1837, 'Legon Hall Annex B'),
  (5.6475, -0.182, 'Pentagon Hostel'),
  (5.647, -0.1817, 'James Topp Nelson Yankah Hall'),
  (5.6465, -0.1814, 'Alexander Adum Kwapong Hall'),
  (5.646, -0.1811, 'Hilla Limann Hall'),
  (5.6455, -0.1808, 'Jean Nelson Aka Hall'),
];

# Extract coordinates and names
coordinates = [(lat, lon) for lat, lon, name in landmarks]
names = [name for lat, lon, name in landmarks]

# Convert coordinates to the required format
locations = [[coord[1], coord[0]] for coord in coordinates]  # ORS expects [lon, lat]

# Function to make ORS API call for a given profile
def get_ors_matrix(locations, profile):
    body = {
        "locations": locations,
        "metrics": ["distance", "duration"],
        "units": "km"
    }
    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        'Authorization': api_key,
        'Content-Type': 'application/json; charset=utf-8'
    }
    call = requests.post(f'https://api.openrouteservice.org/v2/matrix/{profile}', json=body, headers=headers)
    if call.status_code == 200:
        return call.json()
    else:
        raise Exception(f"Error: {call.status_code}, {call.reason}")

# Get matrices for driving-car and foot-walking
matrix_car = get_ors_matrix(locations, 'driving-car')
matrix_walking = get_ors_matrix(locations, 'foot-walking')

# Extract distances and durations
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
        if i != j:  # Avoid self-loops
            G.add_edge(i, j, distance_car=distances_car[i][j], duration_car=durations_car[i][j],
                       distance_walking=distances_walking[i][j], duration_walking=durations_walking[i][j])

# Display all landmarks with their associated numbers
print("Landmarks:")
for i, name in enumerate(names):
    print(f"Node {i}: {name}")

# Get user input for start and end locations
start = int(input("Enter the number for the start location: "))
end = int(input("Enter the number for the end location: "))
print("Select the mode of travel:")
print("1: Driving")
print("2: Walking")
mode = int(input("Enter the number for your preferred mode of travel: "))

# Function to find the shortest path with at least one intermediate node
def find_alternative_path(G, start, end, weight, threshold=0.1):
    try:
        shortest_path = nx.dijkstra_path(G, source=start, target=end, weight=weight)
        if len(shortest_path) > 2:  # If there are intermediate nodes
            return shortest_path
    except nx.NetworkXNoPath:
        pass

    # Find alternative paths through intermediate nodes
    best_path = None
    best_path_length = float('inf')

    for node in G.nodes:
        if node != start and node != end:
            try:
                path_via_node = (nx.dijkstra_path(G, source=start, target=node, weight=weight) +
                                 nx.dijkstra_path(G, source=node, target=end, weight=weight)[1:])
                path_length = sum(G[u][v][weight] for u, v in zip(path_via_node[:-1], path_via_node[1:]))
                if path_length < best_path_length * (1 + threshold):
                    best_path = path_via_node
                    best_path_length = path_length
            except nx.NetworkXNoPath:
                continue

    return best_path if best_path else []

# Find the shortest path or alternative path based on the selected mode
weight = 'duration_car' if mode == 1 else 'duration_walking'
shortest_path = find_alternative_path(G, start, end, weight)
path_distance = sum(G[u][v][f'distance_{weight.split("_")[1]}'] for u, v in zip(shortest_path[:-1], shortest_path[1:]))
path_length = sum(G[u][v][weight] for u, v in zip(shortest_path[:-1], shortest_path[1:]))
travel_mode = "driving" if mode == 1 else "walking"

# Display the shortest path and its distance
print(f"The shortest path from Node {start} to Node {end} is:")
for node in shortest_path:
    print(f"Node {node}: {G.nodes[node]['label']}")

# Convert path length to hours and minutes
path_length_minutes = round(path_length)
if path_length_minutes >= 60:
    hours = path_length_minutes // 60
    minutes = path_length_minutes % 60
    time_str = f"{hours} hours {minutes} mins"
else:
    time_str = f"{path_length_minutes} mins"

print(f"Total distance: {path_distance:.2f} km")
print(f"Total travel time: {time_str}")

# Visualization (Commented Out)
# pos = nx.get_node_attributes(G, 'pos')
# labels = nx.get_node_attributes(G, 'label')
# edge_labels = {(i, j): f"Car: {d['distance_car']:.1f}km, {d['duration_car']:.1f}min\nWalking: {d['distance_walking']:.1f}km, {d['duration_walking']:.1f}min"
#                for i, j, d in G.edges(data=True)}

# Draw the entire graph
# plt.figure(figsize=(15, 10))
# nx.draw(G, pos, with_labels=False, node_size=500, node_color='skyblue', edge_color='gray')

# Highlight the shortest path
# path_edges = list(zip(shortest_path, shortest_path[1:]))
# nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='green', width=2)

# Draw node labels
# nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, font_color='black')

# Draw edges with their weights
# nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)

# plt.title(f"Shortest Path from {G.nodes[start]['label']} to {G.nodes[end]['label']} by {travel_mode.capitalize()}")
# plt.show()