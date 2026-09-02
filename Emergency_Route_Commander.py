import tkinter as tk
from tkinter import ttk, messagebox
import heapq
import time
import math
import random
import networkx as nx
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================
TRAFFIC_LEVELS = {
    'LOW': {'name': 'Low Traffic', 'multiplier': 1.0, 'color': '#2ecc71', 'width': 2.5, 'style': 'solid'},
    'MEDIUM': {'name': 'Medium Traffic', 'multiplier': 1.3, 'color': '#f1c40f', 'width': 3.0, 'style': 'solid'},
    'HIGH': {'name': 'High Traffic', 'multiplier': 1.7, 'color': '#e67e22', 'width': 3.5, 'style': 'solid'},
    'HEAVY': {'name': 'Heavy Traffic', 'multiplier': 2.5, 'color': '#e74c3c', 'width': 4.5, 'style': 'solid'},
    'BLOCKED': {'name': 'Blocked Road', 'multiplier': float('inf'), 'color': '#2b2d42', 'width': 1.5, 'style': 'dashed'}
}

VEHICLES = {
    'Ambulance': {'icon': '🚑', 'speed_kmh': 60.0, 'desc': 'High priority emergency response'},
    'Fire Engine': {'icon': '🚒', 'speed_kmh': 50.0, 'desc': 'Heavy tactical response vehicle'}
}

# Dark theme palette
THEME = {
    'bg_main': '#0b0d17',
    'bg_panel': '#141726',
    'bg_card': '#1d2136',
    'border': '#2d334d',
    'accent_cyan': '#00f5d4',
    'accent_blue': '#3a86ff',
    'accent_purple': '#8338ec',
    'accent_gold': '#ffb703',
    'accent_red': '#ff0055',
    'text_bright': '#ffffff',
    'text_normal': '#e2e8f0',
    'text_muted': '#94a3b8'
}


# ==============================================================================
# CLASS 1: TrafficGraph (Graph Data Model)
# ==============================================================================
class TrafficGraph:
    """
    Manages the road network graph using NetworkX and adjacency structures.
    Supports dynamic traffic condition updates, distances, and node layouts.
    """
    def __init__(self):
        self.graph = nx.Graph()
        self.pos = {}
        self.node_names = {}
        self.load_default_smart_city()

    def clear(self):
        self.graph.clear()
        self.pos.clear()
        self.node_names.clear()

    def add_intersection(self, node_id, label=None, pos=None):
        self.graph.add_node(node_id)
        self.node_names[node_id] = label if label else str(node_id)
        if pos:
            self.pos[node_id] = pos

    def add_road(self, u, v, distance_km, traffic_level='LOW'):
        level = traffic_level if traffic_level in TRAFFIC_LEVELS else 'LOW'
        mult = TRAFFIC_LEVELS[level]['multiplier']
        weight = distance_km * mult if mult != float('inf') else float('inf')
        self.graph.add_edge(u, v, distance=float(distance_km), traffic=level, weight=weight)

    def update_road_traffic(self, u, v, traffic_level):
        if self.graph.has_edge(u, v):
            level = traffic_level if traffic_level in TRAFFIC_LEVELS else 'LOW'
            mult = TRAFFIC_LEVELS[level]['multiplier']
            dist = self.graph[u][v]['distance']
            weight = dist * mult if mult != float('inf') else float('inf')
            self.graph[u][v]['traffic'] = level
            self.graph[u][v]['weight'] = weight

    def get_neighbors(self, u):
        neighbors = []
        if u in self.graph:
            for v in self.graph.neighbors(u):
                edge_data = self.graph[u][v]
                neighbors.append((v, edge_data))
        return neighbors

    def reset_all_traffic(self, level='LOW'):
        for u, v in self.graph.edges():
            self.update_road_traffic(u, v, level)

    def get_traffic_counts(self):
        counts = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'HEAVY': 0, 'BLOCKED': 0}
        for u, v, data in self.graph.edges(data=True):
            t = data.get('traffic', 'LOW')
            if t in counts:
                counts[t] += 1
        return counts

    def load_default_smart_city(self):
        """
        Loads pre-configured 14-intersection Smart City graph.
        Demonstration Scenario:
        Default route from A to J: A -> C -> G -> J (Cost 15.0).
        When C-G becomes Heavy traffic (Cost 12.5), reroutes to A -> B -> E -> H -> J (Cost 18.0).
        """
        self.clear()
        nodes_info = {
            'A': (1.0, 4.0), 'B': (3.0, 5.5), 'C': (3.0, 3.5), 'D': (2.0, 1.5),
            'E': (5.5, 5.5), 'F': (4.5, 1.5), 'G': (5.5, 3.5), 'H': (8.0, 5.0),
            'I': (7.0, 1.5), 'J': (8.0, 3.2), 'K': (10.0, 4.5), 'L': (10.0, 2.0),
            'M': (8.5, 1.0), 'N': (10.5, 1.0)
        }

        for name, pos in nodes_info.items():
            self.add_intersection(name, name, pos)

        roads = [
            ('A', 'B', 5.0), ('A', 'C', 4.0), ('A', 'D', 7.0),
            ('B', 'E', 4.0), ('B', 'C', 3.0),
            ('C', 'G', 5.0), ('C', 'E', 6.0),
            ('D', 'F', 6.0), ('D', 'C', 5.0),
            ('E', 'H', 4.0), ('E', 'G', 5.0),
            ('F', 'I', 5.0), ('F', 'G', 6.0),
            ('G', 'J', 6.0), ('G', 'H', 4.0),
            ('H', 'J', 5.0), ('H', 'K', 5.0), ('H', 'M', 5.0),
            ('I', 'J', 8.0), ('I', 'M', 4.0),
            ('J', 'K', 4.0), ('J', 'L', 5.0),
            ('K', 'L', 6.0), ('L', 'N', 5.0), ('M', 'N', 4.0)
        ]

        for u, v, dist in roads:
            self.add_road(u, v, dist, 'LOW')

    def generate_random_city(self, num_nodes=15, num_edges=25):
        """
        Generates a connected random city road graph with clean node spacing.
        """
        self.clear()
        node_labels = [chr(65 + i) if i < 26 else f"N{i+1}" for i in range(num_nodes)]
        
        G_temp = nx.connected_watts_strogatz_graph(n=num_nodes, k=min(4, num_nodes-1), p=0.3, seed=random.randint(1, 10000))
        mapping = {i: node_labels[i] for i in range(num_nodes)}
        G_temp = nx.relabel_nodes(G_temp, mapping)

        pos_dict = nx.kamada_kawai_layout(G_temp)
        for n in G_temp.nodes():
            x, y = pos_dict[n]
            self.add_intersection(n, n, (round(x * 10, 2), round(y * 10, 2)))

        traffic_choices = ['LOW', 'LOW', 'LOW', 'MEDIUM', 'HIGH']
        for u, v in G_temp.edges():
            dist = round(random.uniform(3.0, 15.0), 1)
            t_level = random.choice(traffic_choices)
            self.add_road(u, v, dist, t_level)


# ==============================================================================
# CLASS 2: DijkstraRouter (Routing Algorithms Engine)
# ==============================================================================
class DijkstraRouter:
    """
    Implements Min-Heap Dijkstra, BFS, and Floyd-Warshall shortest path algorithms.
    """
    @staticmethod
    def run_dijkstra(traffic_graph, start_node, target_node):
        start_time = time.perf_counter()
        
        pq = [(0.0, start_node, [start_node], 0.0)]
        visited = {}
        steps = []
        nodes_explored = 0
        
        while pq:
            cost, u, path, dist = heapq.heappop(pq)
            
            if u in visited and visited[u] <= cost:
                continue
            
            visited[u] = cost
            nodes_explored += 1
            
            heap_nodes = [item[1] for item in pq]
            steps.append({
                'step_num': len(steps) + 1,
                'current_node': u,
                'current_cost': cost,
                'current_dist': dist,
                'path_so_far': list(path),
                'visited_set': set(visited.keys()),
                'candidate_nodes': set(heap_nodes),
                'heap_snapshot': [(round(item[0], 1), item[1]) for item in pq]
            })
            
            if u == target_node:
                exec_time_ms = (time.perf_counter() - start_time) * 1000.0
                return {
                    'found': True,
                    'path': path,
                    'total_cost': round(cost, 2),
                    'total_dist': round(dist, 2),
                    'nodes_explored': nodes_explored,
                    'exec_time_ms': round(exec_time_ms, 4),
                    'steps': steps
                }
                
            for v, edge_data in traffic_graph.get_neighbors(u):
                if edge_data['traffic'] == 'BLOCKED':
                    continue
                w = edge_data['weight']
                d_edge = edge_data['distance']
                new_cost = cost + w
                new_dist = dist + d_edge
                
                if v not in visited or new_cost < visited[v]:
                    heapq.heappush(pq, (new_cost, v, path + [v], new_dist))
                    
        exec_time_ms = (time.perf_counter() - start_time) * 1000.0
        return {
            'found': False,
            'path': [],
            'total_cost': float('inf'),
            'total_dist': 0.0,
            'nodes_explored': nodes_explored,
            'exec_time_ms': round(exec_time_ms, 4),
            'steps': steps
        }

    @staticmethod
    def run_bfs(traffic_graph, start_node, target_node):
        start_time = time.perf_counter()
        queue = [(start_node, [start_node])]
        visited = {start_node}
        nodes_explored = 0
        
        while queue:
            u, path = queue.pop(0)
            nodes_explored += 1
            
            if u == target_node:
                exec_time_ms = (time.perf_counter() - start_time) * 1000.0
                total_dist = 0.0
                total_cost = 0.0
                for i in range(len(path)-1):
                    n1, n2 = path[i], path[i+1]
                    ed = traffic_graph.graph[n1][n2]
                    total_dist += ed['distance']
                    total_cost += ed['weight']
                return {
                    'found': True,
                    'path': path,
                    'total_cost': round(total_cost, 2),
                    'total_dist': round(total_dist, 2),
                    'nodes_explored': nodes_explored,
                    'exec_time_ms': round(exec_time_ms, 4)
                }
                
            for v, edge_data in traffic_graph.get_neighbors(u):
                if edge_data['traffic'] != 'BLOCKED' and v not in visited:
                    visited.add(v)
                    queue.append((v, path + [v]))
                    
        exec_time_ms = (time.perf_counter() - start_time) * 1000.0
        return {
            'found': False, 'path': [], 'total_cost': float('inf'),
            'total_dist': 0.0, 'nodes_explored': nodes_explored, 'exec_time_ms': round(exec_time_ms, 4)
        }

    @staticmethod
    def run_floyd_warshall(traffic_graph, start_node, target_node):
        start_time = time.perf_counter()
        nodes = list(traffic_graph.graph.nodes())
        n = len(nodes)
        node_to_idx = {nodes[i]: i for i in range(n)}
        
        dist_matrix = [[float('inf')] * n for _ in range(n)]
        next_node = [[None] * n for _ in range(n)]
        
        for i in range(n):
            dist_matrix[i][i] = 0.0
            
        for u, v, data in traffic_graph.graph.edges(data=True):
            if data['traffic'] != 'BLOCKED':
                i, j = node_to_idx[u], node_to_idx[v]
                w = data['weight']
                dist_matrix[i][j] = w
                dist_matrix[j][i] = w
                next_node[i][j] = j
                next_node[j][i] = i
                
        nodes_explored = 0
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    nodes_explored += 1
                    if dist_matrix[i][k] + dist_matrix[k][j] < dist_matrix[i][j]:
                        dist_matrix[i][j] = dist_matrix[i][k] + dist_matrix[k][j]
                        next_node[i][j] = next_node[i][k]
                        
        exec_time_ms = (time.perf_counter() - start_time) * 1000.0
        
        u_idx, v_idx = node_to_idx[start_node], node_to_idx[target_node]
        if next_node[u_idx][v_idx] is None:
            return {'found': False, 'path': [], 'total_cost': float('inf'), 'total_dist': 0.0, 'nodes_explored': nodes_explored, 'exec_time_ms': round(exec_time_ms, 4)}
            
        path = [start_node]
        curr = u_idx
        while curr != v_idx:
            curr = next_node[curr][v_idx]
            path.append(nodes[curr])
            
        total_dist = 0.0
        for i in range(len(path)-1):
            total_dist += traffic_graph.graph[path[i]][path[i+1]]['distance']
            
        return {
            'found': True,
            'path': path,
            'total_cost': round(dist_matrix[u_idx][v_idx], 2),
            'total_dist': round(total_dist, 2),
            'nodes_explored': nodes_explored,
            'exec_time_ms': round(exec_time_ms, 4)
        }


# ==============================================================================
# CLASS 3: GraphVisualizer (Matplotlib Embedding & Render Engine)
# ==============================================================================
class GraphVisualizer:
    """
    Renders the interactive NetworkX graph on an embedded Matplotlib canvas.
    Handles route highlights, vehicle markers, dynamic step states, and edge clicks.
    """
    def __init__(self, parent_frame, on_edge_click_callback=None):
        self.parent_frame = parent_frame
        self.on_edge_click_callback = on_edge_click_callback
        
        self.fig = Figure(figsize=(10, 7.5), facecolor=THEME['bg_main'])
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.canvas.mpl_connect('button_press_event', self._on_canvas_click)
        
        self.current_traffic_graph = None
        self.selected_edge = None

    def draw_network(self, traffic_graph, route_info=None, step_data=None, vehicle_type='Ambulance', selected_edge=None, vehicle_node=None):
        """
        Main drawing function. Redraws the entire graph with updated states.
        """
        self.current_traffic_graph = traffic_graph
        self.selected_edge = selected_edge
        self.ax.clear()
        self.ax.set_facecolor(THEME['bg_main'])
        self.ax.axis('off')
        
        G = traffic_graph.graph
        pos = traffic_graph.pos
        
        if not G.nodes():
            self.canvas.draw_idle()
            return

        # ----------------------------------------------------------------------
        # 1. Draw Edges
        # ----------------------------------------------------------------------
        for u, v, data in G.edges(data=True):
            t_level = data.get('traffic', 'LOW')
            t_info = TRAFFIC_LEVELS.get(t_level, TRAFFIC_LEVELS['LOW'])
            
            x_values = [pos[u][0], pos[v][0]]
            y_values = [pos[u][1], pos[v][1]]
            
            edge_sorted = tuple(sorted((u, v)))
            is_selected = (selected_edge and tuple(sorted(selected_edge)) == edge_sorted)
            
            color = t_info['color']
            width = t_info['width']
            linestyle = t_info['style']
            
            if is_selected:
                color = THEME['accent_gold']
                width = width + 2.5
            
            self.ax.plot(x_values, y_values, color=color, linewidth=width, linestyle=linestyle, zorder=1, alpha=0.85)

        # ----------------------------------------------------------------------
        # 2. Draw Edge Labels (Distance & Traffic)
        # ----------------------------------------------------------------------
        edge_labels = {}
        for u, v, data in G.edges(data=True):
            dist = data['distance']
            t_level = data['traffic']
            t_name = TRAFFIC_LEVELS[t_level]['name'].split()[0]
            if t_level == 'BLOCKED':
                label = f"{dist:.1f}km\n❌ BLOCKED"
            else:
                label = f"{dist:.1f}km\n({t_name})"
            edge_labels[(u, v)] = label

        nx.draw_networkx_edge_labels(
            G, pos, edge_labels=edge_labels, ax=self.ax,
            font_size=8, font_color=THEME['text_normal'],
            font_family='sans-serif',
            bbox=dict(boxstyle='round,pad=0.2', fc=THEME['bg_panel'], ec=THEME['border'], alpha=0.85)
        )

        # ----------------------------------------------------------------------
        # 3. Draw Highlighted Emergency Route
        # ----------------------------------------------------------------------
        if route_info and route_info.get('found') and len(route_info['path']) > 1:
            p = route_info['path']
            for i in range(len(p)-1):
                u, v = p[i], p[i+1]
                x_vals = [pos[u][0], pos[v][0]]
                y_vals = [pos[u][1], pos[v][1]]
                
                # Outer glow
                self.ax.plot(x_vals, y_vals, color=THEME['accent_cyan'], linewidth=10.0, alpha=0.3, zorder=2)
                # Inner bright line
                self.ax.plot(x_vals, y_vals, color=THEME['accent_cyan'], linewidth=5.0, zorder=3)
                
                # Directional arrow
                dx = (pos[v][0] - pos[u][0]) * 0.4
                dy = (pos[v][1] - pos[u][1]) * 0.4
                mid_x = pos[u][0] + (pos[v][0] - pos[u][0]) * 0.5
                mid_y = pos[u][1] + (pos[v][1] - pos[u][1]) * 0.5
                self.ax.annotate(
                    '', xy=(mid_x + dx*0.2, mid_y + dy*0.2), xytext=(mid_x - dx*0.2, mid_y - dy*0.2),
                    arrowprops=dict(arrowstyle="-|>", color=THEME['accent_cyan'], lw=2, mutation_scale=16),
                    zorder=4
                )

        # ----------------------------------------------------------------------
        # 4. Draw Vehicle Marker
        # ----------------------------------------------------------------------
        v_target_node = vehicle_node if vehicle_node else (route_info['path'][0] if route_info and route_info.get('found') else None)
        if v_target_node and v_target_node in pos:
            v_pos = pos[v_target_node]
            icon_str = VEHICLES.get(vehicle_type, VEHICLES['Ambulance'])['icon']
            self.ax.text(
                v_pos[0], v_pos[1] + 0.55, icon_str,
                fontsize=24, ha='center', va='center', zorder=12,
                bbox=dict(boxstyle='circle,pad=0.25', fc=THEME['accent_purple'], ec=THEME['accent_cyan'], lw=2)
            )

        # ----------------------------------------------------------------------
        # 5. Draw Nodes with Dynamic State Colors
        # ----------------------------------------------------------------------
        node_colors = []
        for n in G.nodes():
            if step_data:
                curr = step_data.get('current_node')
                visited_set = step_data.get('visited_set', set())
                candidates = step_data.get('candidate_nodes', set())
                
                if n == curr:
                    color = THEME['accent_purple']  # 🟣 Current Node
                elif n in visited_set:
                    color = THEME['accent_blue']    # 🔵 Visited Node
                elif n in candidates:
                    color = THEME['accent_gold']    # 🟡 Candidate Node
                else:
                    color = '#25293d'               # ⚪ Unvisited Node
            elif route_info and route_info.get('found') and n in route_info.get('path', []):
                color = THEME['accent_cyan']        # 🟢 Path Node
            else:
                color = THEME['bg_card']            # Standard Node

            node_colors.append(color)

        nx.draw_networkx_nodes(
            G, pos, ax=self.ax, node_color=node_colors,
            node_size=1100, edgecolors=THEME['accent_blue'], linewidths=2.0
        )

        labels = {n: str(n) for n in G.nodes()}
        nx.draw_networkx_labels(
            G, pos, labels=labels, ax=self.ax,
            font_size=11, font_color=THEME['text_bright'],
            font_weight='bold', font_family='sans-serif'
        )

        # ----------------------------------------------------------------------
        # 6. Floating Dijkstra Step Status Overlay (if visualizer step active)
        # ----------------------------------------------------------------------
        if step_data:
            step_num = step_data.get('step_num', 1)
            curr_node = step_data.get('current_node', '?')
            curr_dist = step_data.get('current_dist', 0.0)
            pq_size = len(step_data.get('heap_snapshot', []))
            
            info_text = (
                f"⚡ DIJKSTRA LIVE\n"
                f"Step: {step_num}\n"
                f"Current Node: {curr_node}\n"
                f"Distance: {curr_dist:.1f} km\n"
                f"Priority Queue Size: {pq_size}"
            )
            self.ax.text(
                0.03, 0.95, info_text, transform=self.ax.transAxes,
                fontsize=9, fontfamily='Consolas', fontweight='bold',
                color=THEME['accent_cyan'], va='top', ha='left', zorder=20,
                bbox=dict(boxstyle='round,pad=0.5', fc=THEME['bg_panel'], ec=THEME['accent_purple'], lw=2, alpha=0.9)
            )

        self.canvas.draw_idle()

    def _on_canvas_click(self, event):
        if event.xdata is None or event.ydata is None or not self.current_traffic_graph:
            return
            
        click_x, click_y = event.xdata, event.ydata
        pos = self.current_traffic_graph.pos
        
        closest_edge = None
        min_dist = float('inf')
        
        for u, v in self.current_traffic_graph.graph.edges():
            p1 = pos[u]
            p2 = pos[v]
            dist = self._point_to_segment_dist((click_x, click_y), p1, p2)
            if dist < min_dist:
                min_dist = dist
                closest_edge = (u, v)
                
        if min_dist < 0.8 and closest_edge:
            if self.on_edge_click_callback:
                self.on_edge_click_callback(closest_edge)

    @staticmethod
    def _point_to_segment_dist(p, p1, p2):
        x, y = p
        x1, y1 = p1
        x2, y2 = p2
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            return math.hypot(x - x1, y - y1)
        t = ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)
        t = max(0.0, min(1.0, t))
        nearest_x = x1 + t * dx
        nearest_y = y1 + t * dy
        return math.hypot(x - nearest_x, y - nearest_y)


# ==============================================================================
# MAIN APPLICATION WINDOW: EmergencyRouteCommanderApp
# ==============================================================================
class EmergencyRouteCommanderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EMERGENCY ROUTE COMMANDER — Real-Time Emergency Vehicle Routing System")
        self.root.geometry("1440x880")
        self.root.minsize(1280, 760)
        self.root.configure(bg=THEME['bg_main'])

        self.traffic_graph = TrafficGraph()
        self.last_route_result = None
        self.selected_edge = None
        self.animation_running = False
        self.vehicle_anim_running = False

        self._configure_styles()
        self._build_header()
        self._build_main_layout()

        self._refresh_comboboxes()
        self.visualizer.draw_network(self.traffic_graph)

    def _configure_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('default')
        
        self.style.configure('TFrame', background=THEME['bg_panel'])
        self.style.configure('Card.TFrame', background=THEME['bg_card'], relief='flat')
        self.style.configure('TLabel', background=THEME['bg_panel'], foreground=THEME['text_normal'], font=('Segoe UI', 10))
        self.style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'), foreground=THEME['accent_cyan'])
        self.style.configure('SubHeader.TLabel', font=('Segoe UI', 10), foreground=THEME['text_muted'])

    def _build_header(self):
        header_frame = tk.Frame(self.root, bg=THEME['bg_panel'], height=65, highlightbackground=THEME['border'], highlightthickness=1)
        header_frame.pack(fill=tk.X, side=tk.TOP, padx=10, pady=(10, 5))

        title_box = tk.Frame(header_frame, bg=THEME['bg_panel'])
        title_box.pack(side=tk.LEFT, padx=15, pady=6)

        lbl_title = tk.Label(
            title_box, text="🚑 EMERGENCY ROUTE COMMANDER",
            font=('Segoe UI', 15, 'bold'), fg=THEME['accent_cyan'], bg=THEME['bg_panel']
        )
        lbl_title.pack(anchor='w')

        lbl_sub = tk.Label(
            title_box, text="Real-Time Smart City Emergency Routing System — Dynamic Shortest Path Optimization",
            font=('Segoe UI', 9), fg=THEME['text_muted'], bg=THEME['bg_panel']
        )
        lbl_sub.pack(anchor='w')

        # Live Header Statistics Badges
        badge_box = tk.Frame(header_frame, bg=THEME['bg_panel'])
        badge_box.pack(side=tk.RIGHT, padx=15)

        self.lbl_node_badge = tk.Label(
            badge_box, text="Intersections: 14", font=('Segoe UI', 8, 'bold'),
            fg=THEME['accent_gold'], bg=THEME['bg_card'], padx=8, pady=4, relief='groove', bd=1
        )
        self.lbl_node_badge.pack(side=tk.LEFT, padx=3)

        self.lbl_edge_badge = tk.Label(
            badge_box, text="Roads: 25", font=('Segoe UI', 8, 'bold'),
            fg=THEME['accent_cyan'], bg=THEME['bg_card'], padx=8, pady=4, relief='groove', bd=1
        )
        self.lbl_edge_badge.pack(side=tk.LEFT, padx=3)

        self.lbl_stats_low = tk.Label(
            badge_box, text="🟢 Low: --", font=('Segoe UI', 8, 'bold'),
            fg='#2ecc71', bg=THEME['bg_card'], padx=8, pady=4, relief='groove', bd=1
        )
        self.lbl_stats_low.pack(side=tk.LEFT, padx=3)

        self.lbl_stats_heavy = tk.Label(
            badge_box, text="🔴 Heavy: --", font=('Segoe UI', 8, 'bold'),
            fg='#e74c3c', bg=THEME['bg_card'], padx=8, pady=4, relief='groove', bd=1
        )
        self.lbl_stats_heavy.pack(side=tk.LEFT, padx=3)

        self.lbl_stats_blocked = tk.Label(
            badge_box, text="🚧 Blocked: --", font=('Segoe UI', 8, 'bold'),
            fg='#94a3b8', bg=THEME['bg_card'], padx=8, pady=4, relief='groove', bd=1
        )
        self.lbl_stats_blocked.pack(side=tk.LEFT, padx=3)

    def _build_main_layout(self):
        """
        Main body division: 72% Width for Matplotlib Canvas, 28% Width for Control Panel.
        NO main vertical scrollbar — full vertical expansion for graph!
        """
        main_container = tk.Frame(self.root, bg=THEME['bg_main'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        main_container.columnconfigure(0, weight=3)
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(0, weight=1)

        # ----------------------------------------------------------------------
        # LEFT COLUMN: Matplotlib Graph Canvas (72% Width, FULL Vertical Height)
        # ----------------------------------------------------------------------
        graph_container = tk.Frame(main_container, bg=THEME['bg_panel'], highlightbackground=THEME['border'], highlightthickness=1)
        graph_container.grid(row=0, column=0, sticky='nsew', padx=(0, 5))

        # Bottom Bar: Single Compact Traffic Legend Strip
        legend_bar = tk.Frame(graph_container, bg=THEME['bg_panel'], height=32)
        legend_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=4)

        tk.Label(legend_bar, text="Traffic Legend:", font=('Segoe UI', 8, 'bold'), fg=THEME['text_bright'], bg=THEME['bg_panel']).pack(side=tk.LEFT, padx=(0, 6))

        legend_items = [
            ("🟢 Low Traffic", "#2ecc71"),
            ("🟡 Medium Traffic", "#f1c40f"),
            ("🟠 High Traffic", "#e67e22"),
            ("🔴 Heavy Traffic", "#e74c3c"),
            ("⚫ Blocked Road", "#4a4e69"),
            ("🔵 Optimal Route", "#00f5d4")
        ]

        for text_str, color_hex in legend_items:
            badge = tk.Label(
                legend_bar, text=text_str, font=('Segoe UI', 8, 'bold'),
                fg=color_hex, bg=THEME['bg_card'], padx=6, pady=2
            )
            badge.pack(side=tk.LEFT, padx=3)

        self.lbl_click_status = tk.Label(
            legend_bar, text="💡 Click any road on graph to select & edit",
            font=('Segoe UI', 8, 'italic'), fg=THEME['text_muted'], bg=THEME['bg_panel']
        )
        self.lbl_click_status.pack(side=tk.RIGHT, padx=5)

        # Matplotlib Graph Visualizer (expands vertically to fill space)
        self.visualizer = GraphVisualizer(graph_container, on_edge_click_callback=self._on_graph_edge_clicked)

        # ----------------------------------------------------------------------
        # RIGHT COLUMN: Control Sidebar (28% Width)
        # ----------------------------------------------------------------------
        right_panel = tk.Frame(main_container, bg=THEME['bg_panel'], highlightbackground=THEME['border'], highlightthickness=1)
        right_panel.grid(row=0, column=1, sticky='nsew', padx=(5, 0))

        panel_canvas = tk.Canvas(right_panel, bg=THEME['bg_panel'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=panel_canvas.yview)
        scrollable_frame = tk.Frame(panel_canvas, bg=THEME['bg_panel'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: panel_canvas.configure(scrollregion=panel_canvas.bbox("all"))
        )
        panel_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        panel_canvas.configure(yscrollcommand=scrollbar.set)

        panel_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._build_navigation_controls(scrollable_frame)
        self._build_traffic_controls(scrollable_frame)
        self._build_compact_results_card(scrollable_frame)
        self._build_educational_tools(scrollable_frame)

    # --------------------------------------------------------------------------
    # RIGHT SIDEBAR SECTION 1: Navigation Command
    # --------------------------------------------------------------------------
    def _build_navigation_controls(self, parent):
        sec = tk.LabelFrame(parent, text=" 🚑 NAVIGATION COMMAND ", font=('Segoe UI', 9, 'bold'), fg=THEME['accent_cyan'], bg=THEME['bg_panel'], padx=8, pady=8)
        sec.pack(fill=tk.X, padx=8, pady=6)

        tk.Label(sec, text="Emergency Vehicle:", font=('Segoe UI', 8, 'bold')).pack(anchor='w')
        self.cb_vehicle = ttk.Combobox(sec, values=list(VEHICLES.keys()), state='readonly', font=('Segoe UI', 8))
        self.cb_vehicle.set('Ambulance')
        self.cb_vehicle.pack(fill=tk.X, pady=(2, 6))

        grid_nodes = tk.Frame(sec, bg=THEME['bg_panel'])
        grid_nodes.pack(fill=tk.X, pady=2)
        grid_nodes.columnconfigure(0, weight=1)
        grid_nodes.columnconfigure(1, weight=1)

        tk.Label(grid_nodes, text="Start Node:", font=('Segoe UI', 8)).grid(row=0, column=0, sticky='w')
        self.cb_start = ttk.Combobox(grid_nodes, state='readonly', width=8, font=('Segoe UI', 8))
        self.cb_start.grid(row=1, column=0, sticky='ew', padx=(0, 4), pady=(2, 6))

        tk.Label(grid_nodes, text="Destination:", font=('Segoe UI', 8)).grid(row=0, column=1, sticky='w')
        self.cb_target = ttk.Combobox(grid_nodes, state='readonly', width=8, font=('Segoe UI', 8))
        self.cb_target.grid(row=1, column=1, sticky='ew', padx=(4, 0), pady=(2, 6))

        btn_find = tk.Button(
            sec, text="🚀 FIND OPTIMAL ROUTE", font=('Segoe UI', 9, 'bold'),
            bg=THEME['accent_cyan'], fg='#000000', activebackground='#00d2b4',
            relief='flat', pady=5, cursor='hand2', command=self.on_find_route
        )
        btn_find.pack(fill=tk.X, pady=3)

        btn_anim = tk.Button(
            sec, text="▶ SHOW ALGORITHM STEPS", font=('Segoe UI', 8, 'bold'),
            bg=THEME['accent_purple'], fg='#ffffff', activebackground='#6c2bd9',
            relief='flat', pady=4, cursor='hand2', command=self.on_start_step_animation
        )
        btn_anim.pack(fill=tk.X, pady=3)

        btn_clear = tk.Button(
            sec, text="❌ CLEAR ROUTE", font=('Segoe UI', 8, 'bold'),
            bg=THEME['bg_card'], fg=THEME['text_muted'], activebackground=THEME['border'],
            relief='groove', pady=2, cursor='hand2', command=self.on_clear_route
        )
        btn_clear.pack(fill=tk.X, pady=(2, 0))

    # --------------------------------------------------------------------------
    # RIGHT SIDEBAR SECTION 2: Dynamic Traffic Control
    # --------------------------------------------------------------------------
    def _build_traffic_controls(self, parent):
        sec = tk.LabelFrame(parent, text=" ⚡ DYNAMIC TRAFFIC CONTROL ", font=('Segoe UI', 9, 'bold'), fg=THEME['accent_gold'], bg=THEME['bg_panel'], padx=8, pady=8)
        sec.pack(fill=tk.X, padx=8, pady=6)

        tk.Label(sec, text="Select Road (or click graph):", font=('Segoe UI', 8)).pack(anchor='w')
        self.cb_roads = ttk.Combobox(sec, state='readonly', font=('Segoe UI', 8))
        self.cb_roads.pack(fill=tk.X, pady=(2, 6))
        self.cb_roads.bind("<<ComboboxSelected>>", self._on_road_combobox_selected)

        tk.Label(sec, text="Traffic Condition:", font=('Segoe UI', 8)).pack(anchor='w')
        self.cb_traffic = ttk.Combobox(
            sec, values=[f"{v['name']} (x{v['multiplier']})" if v['multiplier'] != float('inf') else f"{v['name']} (∞)" for k, v in TRAFFIC_LEVELS.items()],
            state='readonly', font=('Segoe UI', 8)
        )
        self.cb_traffic.set("Heavy Traffic (x2.5)")
        self.cb_traffic.pack(fill=tk.X, pady=(2, 6))

        btn_update = tk.Button(
            sec, text="⚡ UPDATE TRAFFIC", font=('Segoe UI', 8, 'bold'),
            bg=THEME['accent_gold'], fg='#000000', activebackground='#e0a000',
            relief='flat', pady=4, cursor='hand2', command=self.on_update_traffic
        )
        btn_update.pack(fill=tk.X, pady=3)

        # 🚨 SIMULATE INCIDENT BUTTON
        btn_incident = tk.Button(
            sec, text="🚨 SIMULATE INCIDENT", font=('Segoe UI', 9, 'bold'),
            bg=THEME['accent_red'], fg='#ffffff', activebackground='#d90429',
            relief='flat', pady=4, cursor='hand2', command=self.on_simulate_incident
        )
        btn_incident.pack(fill=tk.X, pady=3)

        grid_btn = tk.Frame(sec, bg=THEME['bg_panel'])
        grid_btn.pack(fill=tk.X, pady=3)
        grid_btn.columnconfigure(0, weight=1)
        grid_btn.columnconfigure(1, weight=1)

        btn_reset = tk.Button(
            grid_btn, text="🔄 Reset Network", font=('Segoe UI', 8),
            bg=THEME['bg_card'], fg=THEME['text_normal'], relief='groove',
            command=self.on_reset_network
        )
        btn_reset.grid(row=0, column=0, sticky='ew', padx=(0, 2))

        btn_rand = tk.Button(
            grid_btn, text="🎲 Random City", font=('Segoe UI', 8),
            bg=THEME['bg_card'], fg=THEME['text_normal'], relief='groove',
            command=self.on_generate_random_city_dialog
        )
        btn_rand.grid(row=0, column=1, sticky='ew', padx=(2, 0))

    # --------------------------------------------------------------------------
    # RIGHT SIDEBAR SECTION 3: COMPACT ROUTE RESULT CARD
    # --------------------------------------------------------------------------
    def _build_compact_results_card(self, parent):
        self.f_results_card = tk.LabelFrame(parent, text=" 🚑 ROUTE METRICS ", font=('Segoe UI', 9, 'bold'), fg=THEME['accent_blue'], bg=THEME['bg_panel'], padx=8, pady=8)
        
        self.lbl_card_title = tk.Label(self.f_results_card, text="🚑 ROUTE FOUND", font=('Segoe UI', 9, 'bold'), fg=THEME['accent_cyan'], bg=THEME['bg_panel'])
        self.lbl_card_title.pack(anchor='w')

        self.lbl_card_route = tk.Label(self.f_results_card, text="Route: --", font=('Segoe UI', 9, 'bold'), fg=THEME['text_bright'], bg=THEME['bg_panel'], wraplength=220, justify='left')
        self.lbl_card_route.pack(anchor='w', pady=(2, 4))

        card_box = tk.Frame(self.f_results_card, bg=THEME['bg_card'], padx=6, pady=6, highlightbackground=THEME['border'], highlightthickness=1)
        card_box.pack(fill=tk.X)

        self.lbl_card_dist = tk.Label(card_box, text="Distance: -- km", font=('Segoe UI', 8), bg=THEME['bg_card'], fg=THEME['text_normal'])
        self.lbl_card_dist.pack(anchor='w')

        self.lbl_card_cost = tk.Label(card_box, text="Traffic Cost: --", font=('Segoe UI', 8), bg=THEME['bg_card'], fg=THEME['text_normal'])
        self.lbl_card_cost.pack(anchor='w')

        self.lbl_card_time = tk.Label(card_box, text="Time: -- min", font=('Segoe UI', 8, 'bold'), bg=THEME['bg_card'], fg=THEME['accent_gold'])
        self.lbl_card_time.pack(anchor='w')

        self.lbl_card_nodes = tk.Label(card_box, text="Nodes Explored: --", font=('Segoe UI', 8), bg=THEME['bg_card'], fg=THEME['text_muted'])
        self.lbl_card_nodes.pack(anchor='w')

        self.lbl_card_algo = tk.Label(card_box, text="⚡ Dijkstra + Min-Heap", font=('Segoe UI', 8, 'bold'), bg=THEME['bg_card'], fg=THEME['accent_cyan'])
        self.lbl_card_algo.pack(anchor='w', pady=(2, 0))

    # --------------------------------------------------------------------------
    # RIGHT SIDEBAR SECTION 4: Educational Tools
    # --------------------------------------------------------------------------
    def _build_educational_tools(self, parent):
        sec = tk.LabelFrame(parent, text=" 🎓 EDUCATIONAL TOOLS ", font=('Segoe UI', 9, 'bold'), fg=THEME['text_bright'], bg=THEME['bg_panel'], padx=8, pady=8)
        sec.pack(fill=tk.X, padx=8, pady=6)

        btn_ds = tk.Button(
            sec, text="🔍 VIEW DATA STRUCTURES", font=('Segoe UI', 8, 'bold'),
            bg=THEME['bg_card'], fg=THEME['accent_cyan'], activebackground=THEME['border'],
            relief='groove', pady=3, cursor='hand2', command=self.on_show_data_structures_modal
        )
        btn_ds.pack(fill=tk.X, pady=2)

        btn_comp = tk.Button(
            sec, text="📈 ALGORITHM COMPARISON", font=('Segoe UI', 8, 'bold'),
            bg=THEME['bg_card'], fg=THEME['accent_gold'], activebackground=THEME['border'],
            relief='groove', pady=3, cursor='hand2', command=self.on_show_algorithm_comparison_modal
        )
        btn_comp.pack(fill=tk.X, pady=2)

    # ==========================================================================
    # EVENT HANDLERS & LOGIC
    # ==========================================================================
    def _refresh_comboboxes(self):
        nodes = sorted(list(self.traffic_graph.graph.nodes()))
        self.cb_start['values'] = nodes
        self.cb_target['values'] = nodes
        
        if 'A' in nodes and 'J' in nodes:
            self.cb_start.set('A')
            self.cb_target.set('J')
        elif nodes:
            self.cb_start.set(nodes[0])
            self.cb_target.set(nodes[-1])

        roads = [f"{u} — {v} ({data['traffic']})" for u, v, data in self.traffic_graph.graph.edges(data=True)]
        self.cb_roads['values'] = sorted(roads)
        if roads:
            self.cb_roads.set(sorted(roads)[0])

        counts = self.traffic_graph.get_traffic_counts()
        self.lbl_node_badge.config(text=f"Intersections: {len(nodes)}")
        self.lbl_edge_badge.config(text=f"Roads: {len(roads)}")
        self.lbl_stats_low.config(text=f"🟢 Low: {counts['LOW']}")
        self.lbl_stats_heavy.config(text=f"🔴 Heavy: {counts['HEAVY']}")
        self.lbl_stats_blocked.config(text=f"🚧 Blocked: {counts['BLOCKED']}")

    def _on_graph_edge_clicked(self, edge_tuple):
        u, v = edge_tuple
        self.selected_edge = (u, v)
        
        for val in self.cb_roads['values']:
            if (f"{u} — {v}" in val) or (f"{v} — {u}" in val):
                self.cb_roads.set(val)
                break
                
        self.lbl_click_status.config(text=f"Selected Road: {u} — {v}")
        self.visualizer.draw_network(self.traffic_graph, route_info=self.last_route_result, selected_edge=self.selected_edge)

    def _on_road_combobox_selected(self, event):
        val = self.cb_roads.get()
        if '—' in val:
            parts = val.split()[0:3]
            u, v = parts[0], parts[2]
            self.selected_edge = (u, v)
            self.visualizer.draw_network(self.traffic_graph, route_info=self.last_route_result, selected_edge=self.selected_edge)

    def on_update_traffic(self):
        val = self.cb_roads.get()
        if not val or '—' not in val:
            messagebox.showwarning("Select Road", "Please select a valid road from the dropdown or click on the graph.")
            return

        parts = val.split()
        u, v = parts[0], parts[2]

        selected_traffic_str = self.cb_traffic.get()
        level = 'LOW'
        if 'Medium' in selected_traffic_str: level = 'MEDIUM'
        elif 'High' in selected_traffic_str: level = 'HIGH'
        elif 'Heavy' in selected_traffic_str: level = 'HEAVY'
        elif 'Blocked' in selected_traffic_str: level = 'BLOCKED'

        self.traffic_graph.update_road_traffic(u, v, level)
        self._refresh_comboboxes()
        
        for item in self.cb_roads['values']:
            if (f"{u} — {v}" in item) or (f"{v} — {u}" in item):
                self.cb_roads.set(item)
                break
                
        self.selected_edge = (u, v)

        if self.last_route_result:
            self.on_find_route()
        else:
            self.visualizer.draw_network(self.traffic_graph, selected_edge=self.selected_edge)

        messagebox.showinfo("Traffic Updated", f"Traffic on road {u} — {v} set to {TRAFFIC_LEVELS[level]['name']}.")

    def on_simulate_incident(self):
        edges = list(self.traffic_graph.graph.edges())
        if not edges:
            return
            
        u, v = random.choice(edges)
        new_condition = random.choice(['HEAVY', 'BLOCKED', 'HEAVY'])
        
        self.traffic_graph.update_road_traffic(u, v, new_condition)
        self._refresh_comboboxes()
        self.selected_edge = (u, v)

        for item in self.cb_roads['values']:
            if (f"{u} — {v}" in item) or (f"{v} — {u}" in item):
                self.cb_roads.set(item)
                break

        cond_name = TRAFFIC_LEVELS[new_condition]['name']
        messagebox.showwarning(
            "🚨 TRAFFIC INCIDENT DETECTED",
            f"🚨 EMERGENCY ALERT!\n\nRoad Incident Detected on: {u} — {v}\nNew Condition: {cond_name}\n\nUpdating road network..."
        )

        if self.last_route_result:
            self.on_find_route()
        else:
            self.visualizer.draw_network(self.traffic_graph, selected_edge=self.selected_edge)

    def on_find_route(self):
        start = self.cb_start.get()
        target = self.cb_target.get()
        vehicle = self.cb_vehicle.get()

        if not start or not target:
            messagebox.showwarning("Input Required", "Please select both Start and Destination intersections.")
            return

        if start == target:
            messagebox.showinfo("Same Node", "Start and Destination are the same intersection.")
            return

        self.animation_running = False

        res = DijkstraRouter.run_dijkstra(self.traffic_graph, start, target)
        self.last_route_result = res

        self.f_results_card.pack(fill=tk.X, padx=8, pady=6)

        if res['found']:
            path_str = " → ".join(res['path'])
            speed = VEHICLES[vehicle]['speed_kmh']
            est_minutes = round((res['total_cost'] / speed) * 60.0, 1)

            self.lbl_card_title.config(text=f"🚑 {vehicle.upper()} ROUTE FOUND", fg=THEME['accent_cyan'])
            self.lbl_card_route.config(text=f"Route: {path_str}")
            self.lbl_card_dist.config(text=f"Distance: {res['total_dist']} km")
            self.lbl_card_cost.config(text=f"Traffic Cost: {res['total_cost']}")
            self.lbl_card_time.config(text=f"Est Time: {est_minutes} min")
            self.lbl_card_nodes.config(text=f"Nodes Explored: {res['nodes_explored']}")

            self._animate_vehicle_along_path(res['path'], vehicle)
        else:
            self.lbl_card_title.config(text="❌ NO PATH AVAILABLE", fg=THEME['accent_red'])
            self.lbl_card_route.config(text="Route: BLOCKED")
            self.lbl_card_dist.config(text="Distance: -- km")
            self.lbl_card_cost.config(text="Traffic Cost: ∞")
            self.lbl_card_time.config(text="Est Time: ∞ min")
            self.lbl_card_nodes.config(text=f"Nodes Explored: {res['nodes_explored']}")
            self.visualizer.draw_network(self.traffic_graph, route_info=res, vehicle_type=vehicle, selected_edge=self.selected_edge)

    def _animate_vehicle_along_path(self, path_nodes, vehicle_type):
        self.vehicle_anim_running = True
        self._step_vehicle_animation(path_nodes, current_idx=0, vehicle_type=vehicle_type)

    def _step_vehicle_animation(self, path_nodes, current_idx, vehicle_type):
        if not self.vehicle_anim_running or current_idx >= len(path_nodes):
            self.vehicle_anim_running = False
            self.visualizer.draw_network(
                self.traffic_graph, route_info=self.last_route_result,
                vehicle_type=vehicle_type, selected_edge=self.selected_edge,
                vehicle_node=path_nodes[-1] if path_nodes else None
            )
            return

        curr_node = path_nodes[current_idx]
        self.visualizer.draw_network(
            self.traffic_graph, route_info=self.last_route_result,
            vehicle_type=vehicle_type, selected_edge=self.selected_edge,
            vehicle_node=curr_node
        )

        self.root.after(350, lambda: self._step_vehicle_animation(path_nodes, current_idx + 1, vehicle_type))

    def on_start_step_animation(self):
        start = self.cb_start.get()
        target = self.cb_target.get()
        if not start or not target or start == target:
            messagebox.showwarning("Input Required", "Please select valid Start and Destination nodes.")
            return

        res = DijkstraRouter.run_dijkstra(self.traffic_graph, start, target)
        steps = res.get('steps', [])

        if not steps:
            messagebox.showinfo("No Steps", "No path exploration steps available.")
            return

        self.animation_running = True
        self._run_step_animation_loop(steps, step_idx=0, final_route=res)

    def _run_step_animation_loop(self, steps, step_idx, final_route):
        if not self.animation_running or step_idx >= len(steps):
            self.animation_running = False
            self.visualizer.draw_network(self.traffic_graph, route_info=final_route, vehicle_type=self.cb_vehicle.get(), selected_edge=self.selected_edge)
            return

        step_data = steps[step_idx]
        self.visualizer.draw_network(self.traffic_graph, step_data=step_data, selected_edge=self.selected_edge)

        self.root.after(550, lambda: self._run_step_animation_loop(steps, step_idx + 1, final_route))

    def on_clear_route(self):
        self.animation_running = False
        self.vehicle_anim_running = False
        self.last_route_result = None
        self.f_results_card.pack_forget()
        self.visualizer.draw_network(self.traffic_graph, selected_edge=self.selected_edge)

    def on_reset_network(self):
        self.traffic_graph.load_default_smart_city()
        self.last_route_result = None
        self.selected_edge = None
        self.f_results_card.pack_forget()
        self._refresh_comboboxes()
        self.visualizer.draw_network(self.traffic_graph)
        messagebox.showinfo("Reset Network", "Smart City road network reset to default conditions.")

    def on_generate_random_city_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Generate Random City Graph")
        dialog.geometry("380x240")
        dialog.configure(bg=THEME['bg_panel'])
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="🎲 Random City Configuration", font=('Segoe UI', 11, 'bold'), fg=THEME['accent_cyan'], bg=THEME['bg_panel']).pack(pady=10)

        f_nodes = tk.Frame(dialog, bg=THEME['bg_panel'])
        f_nodes.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(f_nodes, text="Number of Intersections (10 - 30):", font=('Segoe UI', 9)).pack(anchor='w')
        slider_nodes = tk.Scale(f_nodes, from_=10, to=30, orient=tk.HORIZONTAL, bg=THEME['bg_panel'], fg=THEME['text_bright'], highlightthickness=0)
        slider_nodes.set(15)
        slider_nodes.pack(fill=tk.X)

        def generate_action():
            n = slider_nodes.get()
            self.traffic_graph.generate_random_city(num_nodes=n)
            self.last_route_result = None
            self.selected_edge = None
            self.f_results_card.pack_forget()
            self._refresh_comboboxes()
            self.visualizer.draw_network(self.traffic_graph)
            dialog.destroy()
            messagebox.showinfo("Random City", f"Generated connected city network with {n} intersections!")

        btn_create = tk.Button(
            dialog, text="GENERATE NETWORK", font=('Segoe UI', 10, 'bold'),
            bg=THEME['accent_cyan'], fg='#000000', command=generate_action
        )
        btn_create.pack(pady=15)

    def on_show_data_structures_modal(self):
        modal = tk.Toplevel(self.root)
        modal.title("Data Structures Demonstration & Internal State")
        modal.geometry("720x560")
        modal.configure(bg=THEME['bg_main'])

        tk.Label(modal, text="🔍 DATA STRUCTURES ARCHITECTURE", font=('Segoe UI', 14, 'bold'), fg=THEME['accent_cyan'], bg=THEME['bg_main']).pack(pady=(12, 4))
        tk.Label(modal, text="Demonstration of underlying Adjacency List, Min-Heap Priority Queue, HashMap, and HashSet.", font=('Segoe UI', 9), fg=THEME['text_muted'], bg=THEME['bg_main']).pack(pady=(0, 10))

        text_box = tk.Text(modal, bg=THEME['bg_panel'], fg=THEME['text_bright'], font=('Consolas', 9), wrap='none', highlightbackground=THEME['border'], highlightthickness=1)
        scrollbar_y = ttk.Scrollbar(modal, orient='vertical', command=text_box.yview)
        text_box.configure(yscrollcommand=scrollbar_y.set)

        text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(15, 0), pady=10)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 15), pady=10)

        ds_info = []
        ds_info.append("==========================================================================")
        ds_info.append("1. GRAPH REPRESENTATION: ADJACENCY LIST (HashMap / Dictionary)")
        ds_info.append("   Storage Complexity: O(V + E) for sparse road networks")
        ds_info.append("==========================================================================\n")

        for u in sorted(self.traffic_graph.graph.nodes()):
            ds_info.append(f"Node '{u}':")
            for v, data in self.traffic_graph.get_neighbors(u):
                t_str = data['traffic']
                w_str = f"{data['weight']:.1f}" if data['weight'] != float('inf') else "∞"
                ds_info.append(f"   └──> {v}  [Distance: {data['distance']} km | Traffic: {t_str} | Cost Weight: {w_str}]")
            ds_info.append("")

        ds_info.append("\n==========================================================================")
        ds_info.append("2. PRIORITY QUEUE / MIN-HEAP STRUCTURE (heapq)")
        ds_info.append("   Time Complexity: O((V + E) log V)")
        ds_info.append("==========================================================================")
        ds_info.append("• Binary Min-Heap ordering ensures O(1) minimum node retrieval.")
        ds_info.append("• Heap Tuple Format: (current_cost, node_id, path_sequence, total_dist)")

        ds_info.append("\n==========================================================================")
        ds_info.append("3. VISITED TRACKING & DYNAMIC WEIGHTS (HashSet & HashMap)")
        ds_info.append("==========================================================================")
        ds_info.append("• Visited Set (HashSet): O(1) average lookup to prevent cyclic node re-entry.")
        ds_info.append("• Dynamic Weight Table (HashMap): O(1) traffic multiplier lookup & weight update.")

        text_box.insert(tk.END, "\n".join(ds_info))
        text_box.config(state='disabled')

    def on_show_algorithm_comparison_modal(self):
        start = self.cb_start.get()
        target = self.cb_target.get()
        if not start or not target or start == target:
            messagebox.showwarning("Input Required", "Please select valid Start and Destination nodes first.")
            return

        modal = tk.Toplevel(self.root)
        modal.title("Algorithm Comparison Matrix — BFS vs Dijkstra vs Floyd-Warshall")
        modal.geometry("860x540")
        modal.configure(bg=THEME['bg_main'])

        tk.Label(modal, text="📈 SHORTEST PATH ALGORITHM COMPARISON", font=('Segoe UI', 14, 'bold'), fg=THEME['accent_gold'], bg=THEME['bg_main']).pack(pady=(12, 4))
        tk.Label(modal, text=f"Comparison evaluation for route from '{start}' to '{target}' under current traffic conditions.", font=('Segoe UI', 9), fg=THEME['text_muted'], bg=THEME['bg_main']).pack(pady=(0, 10))

        res_dijkstra = DijkstraRouter.run_dijkstra(self.traffic_graph, start, target)
        res_bfs = DijkstraRouter.run_bfs(self.traffic_graph, start, target)
        res_fw = DijkstraRouter.run_floyd_warshall(self.traffic_graph, start, target)

        cols = ("Algorithm", "Exec Time", "Route Hops", "Distance", "Traffic Cost", "Nodes Processed", "Time Complexity")
        tree = ttk.Treeview(modal, columns=cols, show='headings', height=4)
        
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=115, anchor='center')

        tree.column("Algorithm", width=160, anchor='w')
        tree.pack(fill=tk.X, padx=15, pady=10)

        tree.insert("", tk.END, values=(
            "Dijkstra + Min-Heap", f"{res_dijkstra['exec_time_ms']} ms",
            len(res_dijkstra['path'])-1 if res_dijkstra['found'] else 0,
            f"{res_dijkstra['total_dist']} km", res_dijkstra['total_cost'],
            res_dijkstra['nodes_explored'], "O((V + E) log V)"
        ))
        tree.insert("", tk.END, values=(
            "Breadth-First Search (BFS)", f"{res_bfs['exec_time_ms']} ms",
            len(res_bfs['path'])-1 if res_bfs['found'] else 0,
            f"{res_bfs['total_dist']} km", res_bfs['total_cost'],
            res_bfs['nodes_explored'], "O(V + E)"
        ))
        tree.insert("", tk.END, values=(
            "Floyd-Warshall", f"{res_fw['exec_time_ms']} ms",
            len(res_fw['path'])-1 if res_fw['found'] else 0,
            f"{res_fw['total_dist']} km", res_fw['total_cost'],
            res_fw['nodes_explored'], "O(V³)"
        ))

        exp_box = tk.Text(modal, bg=THEME['bg_panel'], fg=THEME['text_normal'], font=('Segoe UI', 9), wrap='word', height=12, highlightbackground=THEME['border'], highlightthickness=1)
        exp_box.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5, 15))

        explanation = (
            "💡 ALGORITHM ANALYSIS & RECOMMENDATION:\n\n"
            "1. Dijkstra's Algorithm with Min-Heap (RECOMMENDED FOR EMERGENCY ROUTING):\n"
            "   • Optimal for weighted graphs where edges have dynamic traffic delays.\n"
            "   • Guarantees finding the true minimal traffic-cost route.\n"
            "   • Highly scalable for large city road networks with O((V + E) log V) efficiency.\n\n"
            "2. Breadth-First Search (BFS):\n"
            "   • Finds the path with the minimum number of road intersections (hops).\n"
            "   • Ignores edge weights (distance & traffic congestion).\n\n"
            "3. Floyd-Warshall Algorithm:\n"
            "   • Computes all-pairs shortest paths simultaneously.\n"
            "   • High O(V³) computational overhead."
        )

        exp_box.insert(tk.END, explanation)
        exp_box.config(state='disabled')


# ==============================================================================
# APPLICATION ENTRY POINT
# ==============================================================================
if __name__ == '__main__':
    root = tk.Tk()
    app = EmergencyRouteCommanderApp(root)
    root.mainloop()
