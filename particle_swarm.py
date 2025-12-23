"""
Particle Swarm Optimization for Network Path Optimization
"""

import random
import numpy as np
from typing import List, Tuple, Dict
import networkx as nx


class ParticleSwarmOptimization:
    """Particle Swarm Optimization for finding optimal paths in networks"""
    
    def __init__(self, graph: nx.Graph, source: int, destination: int,
                 num_particles: int = 50, num_iterations: int = 100,
                 w: float = 0.7, c1: float = 1.5, c2: float = 1.5):
        """
        Initialize Particle Swarm Optimization
        
        Args:
            graph: Network graph
            source: Source node
            destination: Destination node
            num_particles: Number of particles in swarm
            num_iterations: Number of iterations
            w: Inertia weight
            c1: Cognitive parameter (personal best)
            c2: Social parameter (global best)
        """
        self.graph = graph
        self.source = source
        self.destination = destination
        self.num_particles = num_particles
        self.num_iterations = num_iterations
        self.w = w
        self.c1 = c1
        self.c2 = c2
        
        self.weights = {'delay': 0.33, 'reliability': 0.33, 'resource': 0.34}
        self.network_generator = None
        
        self.nodes_list = list(graph.nodes())
    
    def set_weights(self, weights: Dict[str, float]):
        """Set weights for multi-objective optimization"""
        self.weights = weights
    
    def set_network_generator(self, network_generator):
        """Set network generator for metric calculations"""
        self.network_generator = network_generator
    
    def _path_to_position(self, path: List[int]) -> np.ndarray:
        """Convert path to position vector (for PSO)"""
        # Encode path as sequence of node indices
        max_length = len(self.graph.nodes())
        position = np.zeros(max_length)
        
        for i, node in enumerate(path[:max_length]):
            position[i] = float(node)
        
        return position
    
    def _position_to_path(self, position: np.ndarray) -> List[int]:
        """Convert position vector to valid path"""
        # Extract nodes from position
        nodes = [int(round(p)) % len(self.nodes_list) if p != 0 else 0 
                for p in position if p != 0]
        
        # Map to actual node IDs
        path_nodes = [self.nodes_list[n] for n in nodes if 0 <= n < len(self.nodes_list)]
        
        # Ensure source and destination
        if not path_nodes or path_nodes[0] != self.source:
            path_nodes.insert(0, self.source)
        if path_nodes[-1] != self.destination:
            path_nodes.append(self.destination)
        
        # Remove duplicates while maintaining order
        seen = set()
        unique_path = []
        for node in path_nodes:
            if node not in seen:
                seen.add(node)
                unique_path.append(node)
        
        # Repair path to ensure connectivity
        return self._repair_path(unique_path)
    
    def _repair_path(self, path: List[int]) -> List[int]:
        """Repair path to ensure it's valid and connected"""
        if not path or len(path) < 2:
            try:
                return nx.shortest_path(self.graph, self.source, self.destination)
            except:
                return [self.source, self.destination]
        
        repaired = [path[0]]
        
        for i in range(1, len(path)):
            current = repaired[-1]
            target = path[i]
            
            if current == target:
                continue
            
            # Check if there's a direct edge
            if self.graph.has_edge(current, target):
                repaired.append(target)
            else:
                # Find shortest path between them
                try:
                    bridge = nx.shortest_path(self.graph, current, target)
                    repaired.extend(bridge[1:])
                except:
                    # Skip this node if unreachable
                    continue
        
        # Ensure we end at destination
        if repaired[-1] != self.destination:
            try:
                bridge = nx.shortest_path(self.graph, repaired[-1], self.destination)
                repaired.extend(bridge[1:])
            except:
                try:
                    return nx.shortest_path(self.graph, self.source, self.destination)
                except:
                    return [self.source, self.destination]
        
        return repaired
    
    def _generate_random_path(self) -> List[int]:
        """Generate a random valid path"""
        try:
            # Start with shortest path
            path = nx.shortest_path(self.graph, self.source, self.destination)
            
            # Randomly add some intermediate nodes
            for _ in range(random.randint(0, 3)):
                if len(path) >= 2:
                    insert_pos = random.randint(1, len(path) - 1)
                    current = path[insert_pos - 1]
                    neighbors = [n for n in self.graph.neighbors(current) 
                               if n not in path]
                    if neighbors:
                        path.insert(insert_pos, random.choice(neighbors))
            
            return self._repair_path(path)
        except:
            return [self.source, self.destination]
    
    def _calculate_cost(self, path: List[int]) -> float:
        """Calculate cost of a path"""
        if not self.network_generator:
            return float('inf')
        
        return self.network_generator.calculate_total_cost(path, self.weights)
    
    def optimize(self) -> Tuple[List[int], float, Dict]:
        """
        Run PSO optimization
        
        Returns:
            Tuple of (best_path, best_cost, statistics)
        """
        if not self.network_generator:
            return [], float('inf'), {}
        
        # Initialize particles
        particles = []
        velocities = []
        personal_best_positions = []
        personal_best_costs = []
        
        for _ in range(self.num_particles):
            # Initialize with random path
            path = self._generate_random_path()
            position = self._path_to_position(path)
            
            particles.append(position)
            velocities.append(np.random.randn(len(position)) * 0.1)
            personal_best_positions.append(position.copy())
            personal_best_costs.append(self._calculate_cost(path))
        
        # Find global best
        global_best_idx = np.argmin(personal_best_costs)
        global_best_position = personal_best_positions[global_best_idx].copy()
        global_best_cost = personal_best_costs[global_best_idx]
        
        history = {
            'best_cost': [],
            'avg_cost': [],
            'diversity': []
        }
        
        for iteration in range(self.num_iterations):
            for i in range(self.num_particles):
                # Update velocity
                r1 = random.random()
                r2 = random.random()
                
                cognitive = self.c1 * r1 * (personal_best_positions[i] - particles[i])
                social = self.c2 * r2 * (global_best_position - particles[i])
                
                velocities[i] = self.w * velocities[i] + cognitive + social
                
                # Update position
                particles[i] = particles[i] + velocities[i]
                
                # Convert to path and evaluate
                path = self._position_to_path(particles[i])
                cost = self._calculate_cost(path)
                
                # Update personal best
                if cost < personal_best_costs[i]:
                    personal_best_costs[i] = cost
                    personal_best_positions[i] = particles[i].copy()
                    
                    # Update global best
                    if cost < global_best_cost:
                        global_best_cost = cost
                        global_best_position = particles[i].copy()
            
            # Record statistics
            history['best_cost'].append(global_best_cost)
            history['avg_cost'].append(np.mean(personal_best_costs))
            
            # Calculate diversity (average distance between particles)
            distances = []
            for i in range(len(particles)):
                for j in range(i + 1, len(particles)):
                    dist = np.linalg.norm(particles[i] - particles[j])
                    distances.append(dist)
            history['diversity'].append(np.mean(distances) if distances else 0)
        
        # Convert best position to path
        best_path = self._position_to_path(global_best_position)
        
        return best_path, global_best_cost, history
