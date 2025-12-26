"""
Ant Colony Optimization for Network Path Optimization
"""

import random
import numpy as np
from typing import List, Tuple, Dict
import networkx as nx


class AntColonyOptimization:
    """Ant Colony Optimization for finding optimal paths in networks"""
    
    def __init__(self, graph: nx.Graph, source: int, destination: int,
                 num_ants: int = 10, num_iterations: int = 10,
                 alpha: float = 1.0, beta: float = 2.0,
                 evaporation_rate: float = 0.5, Q: float = 100.0):
        """
        Initialize Ant Colony Optimization
        
        Args:
            graph: Network graph
            source: Source node
            destination: Destination node
            num_ants: Number of ants
            num_iterations: Number of iterations
            alpha: Pheromone importance factor
            beta: Heuristic importance factor
            evaporation_rate: Pheromone evaporation rate
            Q: Pheromone deposit factor
        """
        self.graph = graph
        self.source = source
        self.destination = destination
        self.num_ants = num_ants
        self.num_iterations = num_iterations
        self.alpha = alpha
        self.beta = beta
        self.evaporation_rate = evaporation_rate
        self.Q = Q
        
        self.weights = {'delay': 0.33, 'reliability': 0.33, 'resource': 0.34}
        self.network_generator = None
        
        # Initialize pheromone matrix
        self.pheromone = {}
        self._initialize_pheromones()
    
    def set_weights(self, weights: Dict[str, float]):
        """Set weights for multi-objective optimization"""
        self.weights = weights
    
    def set_network_generator(self, network_generator):
        """Set network generator for metric calculations"""
        self.network_generator = network_generator
    
    def _initialize_pheromones(self):
        """Initialize pheromone levels on all edges"""
        for edge in self.graph.edges():
            self.pheromone[edge] = 1.0
            self.pheromone[(edge[1], edge[0])] = 1.0  # Undirected graph
    
    def _get_heuristic(self, node1: int, node2: int) -> float:
        """Calculate heuristic value for edge (inverse of cost)"""
        edge = (node1, node2)
        if edge not in self.graph.edges():
            edge = (node2, node1)
        
        if edge not in self.graph.edges():
            return 0.0
        
        # Heuristic based on inverse of delay and resource cost
        delay = self.graph.edges[edge]['delay']
        bandwidth = self.graph.edges[edge]['bandwidth']
        
        # Higher bandwidth and lower delay = better heuristic
        heuristic = bandwidth / (delay + 1.0)
        
        return heuristic
    
    def _select_next_node(self, current_node: int, visited: set, 
                         candidates: List[int]) -> int:
        """Select next node based on pheromone and heuristic"""
        if not candidates:
            return None
        
        probabilities = []
        
        for candidate in candidates:
            # Get pheromone level
            edge = (current_node, candidate)
            if edge not in self.pheromone:
                edge = (candidate, current_node)
            
            tau = self.pheromone.get(edge, 0.1)
            
            # Get heuristic value
            eta = self._get_heuristic(current_node, candidate)
            
            # Calculate probability
            if eta > 0:
                prob = (tau ** self.alpha) * (eta ** self.beta)
            else:
                prob = tau ** self.alpha
            
            probabilities.append(prob)
        
        # Normalize probabilities
        total = sum(probabilities)
        if total > 0:
            probabilities = [p / total for p in probabilities]
        else:
            probabilities = [1.0 / len(candidates)] * len(candidates)
        
        # Select node based on probabilities
        selected = np.random.choice(candidates, p=probabilities)
        
        return selected
    
    def _construct_path(self) -> List[int]:
        """Construct a path for one ant"""
        path = [self.source]
        visited = {self.source}
        current = self.source
        
        max_steps = len(self.graph.nodes()) * 2
        steps = 0
        
        while current != self.destination and steps < max_steps:
            # Get unvisited neighbors
            neighbors = list(self.graph.neighbors(current))
            candidates = [n for n in neighbors if n not in visited]
            
            # If destination is a neighbor, prefer it
            if self.destination in neighbors:
                if random.random() < 0.8:  # 80% chance to go to destination
                    current = self.destination
                    path.append(current)
                    break
            
            if not candidates:
                # Dead end - try to find path from here to destination
                try:
                    remaining_path = nx.shortest_path(self.graph, current, 
                                                     self.destination)
                    path.extend(remaining_path[1:])
                    break
                except:
                    # No path available
                    return []
            
            # Select next node
            next_node = self._select_next_node(current, visited, candidates)
            
            if next_node is None:
                break
            
            path.append(next_node)
            visited.add(next_node)
            current = next_node
            steps += 1
        
        # Verify path reaches destination
        if path[-1] != self.destination:
            try:
                # Complete path to destination
                bridge = nx.shortest_path(self.graph, path[-1], self.destination)
                path.extend(bridge[1:])
            except:
                return []
        
        return path
    
    def _update_pheromones(self, paths: List[List[int]], costs: List[float]):
        """Update pheromone levels based on ant paths"""
        # Evaporation
        for edge in self.pheromone:
            self.pheromone[edge] *= (1 - self.evaporation_rate)
        
        # Deposit pheromones
        for path, cost in zip(paths, costs):
            if not path or cost == float('inf'):
                continue
            
            # Amount of pheromone to deposit (inverse of cost)
            delta = self.Q / cost if cost > 0 else 0
            
            # Deposit on each edge in path
            for i in range(len(path) - 1):
                edge = (path[i], path[i + 1])
                rev_edge = (path[i + 1], path[i])
                
                if edge in self.pheromone:
                    self.pheromone[edge] += delta
                if rev_edge in self.pheromone:
                    self.pheromone[rev_edge] += delta
    
    def optimize(self) -> Tuple[List[int], float, Dict]:
        """
        Run ACO optimization
        
        Returns:
            Tuple of (best_path, best_cost, statistics)
        """
        if not self.network_generator:
            return [], float('inf'), {}
        
        best_path = None
        best_cost = float('inf')
        
        history = {
            'best_cost': [],
            'avg_cost': [],
            'num_ants_succeeded': []
        }
        
        for iteration in range(self.num_iterations):
            # Construct paths for all ants
            paths = []
            costs = []
            
            for ant in range(self.num_ants):
                path = self._construct_path()
                
                if path:
                    cost = self.network_generator.calculate_total_cost(path, 
                                                                       self.weights)
                    paths.append(path)
                    costs.append(cost)
                    
                    # Update best solution
                    if cost < best_cost:
                        best_cost = cost
                        best_path = path[:]
            
            # Update pheromones
            if paths:
                self._update_pheromones(paths, costs)
            
            # Record statistics
            history['best_cost'].append(best_cost)
            if costs:
                history['avg_cost'].append(np.mean(costs))
            else:
                history['avg_cost'].append(best_cost)
            history['num_ants_succeeded'].append(len(paths))
        
        return best_path, best_cost, history
