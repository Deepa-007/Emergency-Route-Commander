# 🚑 Emergency Route Commander

## Real-Time Emergency Vehicle Routing System

**Emergency Route Commander** is an interactive Smart City Emergency Vehicle Routing System designed to help ambulances and fire engines find the optimal route through a dynamic road network.

The system uses **Dijkstra's Shortest Path Algorithm with a Min-Heap Priority Queue** to calculate the most efficient route while considering changing traffic conditions.

The project provides a colourful and interactive graph-based visualization of a smart city road network, allowing users to observe how traffic changes affect emergency vehicle routing.

---

# ✨ Features

- 🚑 Ambulance Route Planning
- 🚒 Fire Engine Route Planning
- 🗺️ Interactive Smart City Road Network
- ⚡ Dijkstra's Algorithm with Min-Heap
- 🚦 Dynamic Traffic Management
- 🔄 Real-Time Route Recalculation
- 🚨 Traffic Incident Simulation
- 🎯 Optimal Route Highlighting
- 🚑 Emergency Vehicle Animation
- 🎲 Random City Network Generation
- ▶ Step-by-Step Dijkstra Visualization
- 📊 Algorithm Comparison
- 🔍 Interactive Road Selection
- 🎓 Data Structure Visualization

---

# 🗺️ Traffic Conditions

The system supports multiple traffic conditions.

| Traffic Condition | Multiplier | Description |
|---|---:|---|
| 🟢 Low Traffic | ×1.0 | Normal road conditions |
| 🟡 Medium Traffic | ×1.3 | Moderate congestion |
| 🟠 High Traffic | ×1.7 | Increased congestion |
| 🔴 Heavy Traffic | ×2.5 | Severe congestion |
| ⚫ Blocked Road | ∞ | Road unavailable |

The road cost is dynamically calculated based on:

```text
Traffic Cost = Road Distance × Traffic Multiplier
```

---

# 🧠 Algorithms Used

## 1. Dijkstra's Algorithm

Dijkstra's Algorithm is the primary routing algorithm used in the system.

It calculates the shortest weighted path between the emergency vehicle's starting location and destination.

The algorithm considers:

- Road distance
- Traffic conditions
- Dynamic traffic weights
- Blocked roads

### Time Complexity

```text
O((V + E) log V)
```

---

## 2. Breadth-First Search (BFS)

BFS is included for algorithm comparison.

It finds a route with the minimum number of intersections but does not consider traffic-weighted road costs.

### Time Complexity

```text
O(V + E)
```

---

## 3. Floyd-Warshall Algorithm

Floyd-Warshall is included for comparison with Dijkstra's Algorithm.

It computes shortest paths between all pairs of intersections.

### Time Complexity

```text
O(V³)
```

---

# 🏗️ Data Structures Used

## Adjacency Graph

The smart-city road network is represented using a graph structure containing intersections and roads.

## Min-Heap Priority Queue

Python's `heapq` module is used as a Min-Heap Priority Queue for efficient Dijkstra shortest-path computation.

## HashMap / Dictionary

Python dictionaries are used for efficient storage and management of graph and traffic-related data.

## HashSet / Set

Sets are used for efficient visited-node tracking during algorithm execution.

---

# 🚦 Dynamic Traffic Management

Users can dynamically update the traffic condition of any road.

The system automatically:

1. Updates the road weight.
2. Changes the road colour.
3. Updates traffic statistics.
4. Recalculates the optimal route when required.

Users can also simulate traffic incidents.

🚨 When an incident occurs, a road may experience heavy traffic or become blocked, allowing the system to demonstrate real-time route adaptation.

---

# 🎮 Algorithm Visualization

The application provides step-by-step visualization of Dijkstra's Algorithm.

Different node states are visually represented:

- 🟣 Current Node
- 🔵 Visited Node
- 🟡 Candidate Node
- ⚪ Unvisited Node
- 🟢 Final Route

This feature makes the project useful for understanding and demonstrating shortest-path algorithms.

---

# 🖥️ Technologies Used

- Python
- Tkinter
- NetworkX
- Matplotlib
- Heapq

---

# 📸 Screenshots

## Main Smart City Dashboard

Add your screenshot here:

```markdown
![Main Dashboard](screenshots/main-dashboard.png)
```

## Optimal Emergency Route

```markdown
![Optimal Route](screenshots/optimal-route.png)
```

## Dynamic Traffic Update

```markdown
![Traffic Update](screenshots/traffic-update.png)
```

## Dijkstra Algorithm Visualization

```markdown
![Algorithm Visualization](screenshots/algorithm-visualization.png)
```

---

# 🚀 Installation

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/Emergency-Route-Commander.git
```

## 2. Navigate to the Project Folder

```bash
cd Emergency-Route-Commander
```

## 3. Install Required Libraries

```bash
pip install -r requirements.txt
```

## 4. Run the Application

```bash
python Emergency_Route_Commander.py
```

---

# 🎯 How to Use

1. Select an emergency vehicle.
2. Select the starting intersection.
3. Select the destination intersection.
4. Click **FIND OPTIMAL ROUTE**.
5. Observe the highlighted shortest route.
6. Modify traffic conditions if required.
7. Click **UPDATE TRAFFIC**.
8. Recalculate the route.
9. Use **SIMULATE INCIDENT** to demonstrate real-time routing.
10. Use **SHOW ALGORITHM STEPS** to visualize Dijkstra's Algorithm.

---

# 📊 Default Demonstration

The application includes a preconfigured Smart City road network.

A demonstration scenario can be performed by calculating an emergency route and then introducing heavy traffic or a traffic incident on one of the roads.

The system dynamically updates the graph and recalculates the most efficient available route.

---

# 🔮 Future Enhancements

- Real-time GPS integration
- Live traffic API integration
- Multiple emergency vehicle coordination
- Real city map integration
- Machine learning traffic prediction
- Web-based deployment
- Mobile application support
- Emergency vehicle priority management

---

# 👩‍💻 Author

**V Deepa Dharshini**

---

# ⭐ Project Objective

The objective of this project is to demonstrate the practical application of graph algorithms and efficient data structures in a real-world Smart City environment.

Emergency Route Commander combines:

- Graph Theory
- Dijkstra's Algorithm
- Min-Heap Priority Queues
- Dynamic Weighted Graphs
- Hash-Based Data Structures
- Interactive Visualization

to create a real-time emergency vehicle routing simulator.

---

⭐ If you found this project interesting, consider giving the repository a star!
