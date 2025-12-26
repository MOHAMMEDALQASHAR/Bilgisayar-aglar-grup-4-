"""
Tabu Search for Network Path Optimization
"""

import random
import networkx as nx
import math
from typing import List, Tuple, Dict, Any

class TabuSearch:
    """Tabu Search algorithm for finding optimal paths in networks"""
    
    def __init__(self, graph: nx.Graph, source: int, destination: int,
                 tabu_tenure: int = 10, num_iterations: int = 50, 
                 neighborhood_size: int = 20):
        """
        Initialize Tabu Search
        
        Args:
            graph: Network graph
            source: Source node
            destination: Destination node
            tabu_tenure: Number of iterations a move stays tabu
            num_iterations: Maximum number of iterations
            neighborhood_size: Number of neighbors to generate per iteration
        """
        self.graph = graph
        self.source = source
        self.destination = destination
        self.tabu_tenure = tabu_tenure
        self.num_iterations = num_iterations
        self.neighborhood_size = neighborhood_size
        
        # Default weights
        self.weights = {'delay': 0.33, 'reliability': 0.33, 'resource': 0.34}
        self.network_generator = None
        
        # Tabu list stores moves (or paths) that are forbidden
        # We'll store hash of paths or edges to keep it simple
        self.tabu_list = {}
        
    def set_weights(self, weights: Dict[str, float]):
        """Set weights for multi-objective optimization"""
        self.weights = weights
        
    def set_network_generator(self, network_generator):
        """Set network generator for metric calculations"""
        self.network_generator = network_generator

    def _calculate_cost(self, path: List[int]) -> float:
        """Calculate cost of a path using network generator"""
        if not self.network_generator:
            return float('inf')
        return self.network_generator.calculate_total_cost(path, self.weights)
        
    def _get_initial_solution(self) -> List[int]:
        """Get initial solution (shortest path by hops or random)"""
        try:
            return nx.shortest_path(self.graph, self.source, self.destination)
        except:
             # Fallback if no path found (disconnected) - though app checks this first
            return [self.source, self.destination]

    def _generate_neighbor(self, current_path: List[int]) -> List[int]:
        """
        Generate a neighbor solution by modifying the current path.
        Modification operators:
        1. Remove a node (shortening)
        2. Insert a node (detour)
        3. Swap nodes (re-ordering - rarely valid in graphs but possible)
        4. Replace subsection with shortest path
        """
        if len(current_path) < 2:
            return current_path[:]
            
        new_path = current_path[:]
        op = random.random()
        
        if op < 0.3 and len(new_path) > 2:
            # 1. Remove a random node (not source/dest) & repair
            idx = random.randint(1, len(new_path) - 2)
            new_path.pop(idx)
        
        elif op < 0.6:
            # 2. Insert a node
            if len(new_path) >= 2:
                idx = random.randint(1, len(new_path)-1) # Insert before idx
                prev_node = new_path[idx-1]
                # Pick a neighbor of prev_node not in path
                candidates = [n for n in self.graph.neighbors(prev_node) if n not in new_path]
                if candidates:
                    new_node = random.choice(candidates)
                    new_path.insert(idx, new_node)
        
        elif op < 0.8 and len(new_path) > 3:
            # 3. Replace segment with valid sub-path
            idx1 = random.randint(1, len(new_path)-3)
            idx2 = random.randint(idx1+1, len(new_path)-2)
            # Try to connect idx1 to idx2 via shortest path
            try:
                sub_path = nx.shortest_path(self.graph, new_path[idx1], new_path[idx2])
                # Splice: start...idx1 + sub_path[1:-1] + idx2...end
                new_path = new_path[:idx1+1] + sub_path[1:-1] + new_path[idx2:]
            except:
                pass

        # Repair path to ensure validity
        return self._repair_path(new_path)

    def _repair_path(self, path: List[int]) -> List[int]:
        """Ensure path is connected and strictly simple (no loops)"""
        if not path: return path
        
        # 1. Ensure Start/End
        if path[0] != self.source: path.insert(0, self.source)
        if path[-1] != self.destination: path.append(self.destination)
        
        # 2. Loop removal
        seen = {}
        clean_path = []
        for node in path:
            if node in seen:
                # Cycle detected, rollback to first occurrence
                first_idx = seen[node]
                clean_path = clean_path[:first_idx+1]
                # Rebuild seen dict since we removed items
                seen = {n: i for i, n in enumerate(clean_path)}
            else:
                seen[node] = len(clean_path)
                clean_path.append(node)
        
        path = clean_path
        
        # 3. Connectivity fix
        final_path = [path[0]]
        for i in range(1, len(path)):
            u, v = final_path[-1], path[i]
            if not self.graph.has_edge(u, v):
                # Gap detected, bridge with shortest path
                try:
                    bridge = nx.shortest_path(self.graph, u, v)
                    final_path.extend(bridge[1:])
                except:
                    # If no bridge, cut path and try to go to destination directly from u
                    try:
                        end_bridge = nx.shortest_path(self.graph, u, self.destination)
                        final_path.extend(end_bridge[1:])
                        return final_path
                    except:
                        # Failed completely
                        return final_path # May be invalid
            else:
                final_path.append(v)
                
        return final_path

    def optimize(self) -> Tuple[List[int], float, Dict[str, Any]]:
        """Run Tabu Search"""
        if not self.network_generator:
            return [], 0.0, {}

        current_path = self._get_initial_solution()
        current_cost = self._calculate_cost(current_path)
        
        best_path = current_path[:]
        best_cost = current_cost
        
        history = {
            'best_cost': [],
            'current_cost': []
        }
        
        for iteration in range(self.num_iterations):
            # Neighborhood Search
            best_neighbor_path = None
            best_neighbor_cost = float('inf')
            
            # Generate candidates
            for _ in range(self.neighborhood_size):
                neighbor = self._generate_neighbor(current_path)
                if not neighbor: continue
                
                neighbor_cost = self._calculate_cost(neighbor)
                
                # Convert path to tuple for hashability
                path_hash = tuple(neighbor)
                
                # Check Tabu status
                is_tabu = False
                if path_hash in self.tabu_list:
                    # Decrement tenure
                    if self.tabu_list[path_hash] > iteration:
                        is_tabu = True
                
                # Aspiration Criteria: Allow tabu if it's better than global best
                if is_tabu and neighbor_cost < best_cost:
                    is_tabu = False
                
                if not is_tabu:
                    if neighbor_cost < best_neighbor_cost:
                        best_neighbor_cost = neighbor_cost
                        best_neighbor_path = neighbor
            
            # Update current solution if we found a valid neighbor
            if best_neighbor_path:
                current_path = best_neighbor_path
                current_cost = best_neighbor_cost
                
                # Add to tabu list
                self.tabu_list[tuple(current_path)] = iteration + self.tabu_tenure
                
                # Update global best
                if current_cost < best_cost:
                    best_cost = current_cost
                    best_path = current_path[:]
            
            # Cleanup tabu list (optional, or handled by current iteration check)
            
            history['best_cost'].append(best_cost)
            history['current_cost'].append(current_cost)
            
        return best_path, best_cost, history