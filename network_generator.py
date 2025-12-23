"""
Network Generator Module
Generates random networks using Erdős–Rényi model with specified properties
"""

import networkx as nx
import numpy as np
from typing import Dict, Tuple
import random


class NetworkGenerator:
    """Generate and manage network topology with node and link properties"""
    
    def __init__(self, num_nodes: int = 250, connection_prob: float = 0.4, seed: int = None):
        """
        Initialize network generator
        
        Args:
            num_nodes: Number of nodes in the network
            connection_prob: Probability of edge creation (Erdős–Rényi parameter)
            seed: Random seed for reproducibility
        """
        self.num_nodes = num_nodes
        self.connection_prob = connection_prob
        self.seed = seed
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        self.graph = None
        
    def generate_connected_network(self) -> nx.Graph:
        """
        Generate a connected Erdős–Rényi network
        
        Returns:
            Connected graph with specified properties
        """
        # Generate network until we get a connected one
        max_attempts = 100
        for attempt in range(max_attempts):
            G = nx.erdos_renyi_graph(self.num_nodes, self.connection_prob, seed=self.seed)
            
            if nx.is_connected(G):
                self.graph = G
                self._assign_node_properties()
                self._assign_link_properties()
                return G
            
            # Increase seed for next attempt if seed was provided
            if self.seed is not None:
                self.seed += 1
        
        # If we couldn't generate a connected graph, force connectivity
        G = nx.erdos_renyi_graph(self.num_nodes, self.connection_prob, seed=self.seed)
        
        # Connect all components
        components = list(nx.connected_components(G))
        for i in range(len(components) - 1):
            node1 = random.choice(list(components[i]))
            node2 = random.choice(list(components[i + 1]))
            G.add_edge(node1, node2)
        
        self.graph = G
        self._assign_node_properties()
        self._assign_link_properties()
        return G
    
    def _assign_node_properties(self):
        """Assign properties to each node"""
        for node in self.graph.nodes():
            # Processing Delay: [0.5 ms - 2.0 ms]
            processing_delay = np.random.uniform(0.5, 2.0)
            
            # Node Reliability: [0.95, 0.999]
            node_reliability = np.random.uniform(0.95, 0.999)
            
            self.graph.nodes[node]['processing_delay'] = processing_delay
            self.graph.nodes[node]['reliability'] = node_reliability
            
            # Generate random geographical coordinates
            # Lat: -90 to 90, Lng: -180 to 180
            self.graph.nodes[node]['lat'] = np.random.uniform(-60, 80)  # Avoid extreme poles
            self.graph.nodes[node]['lng'] = np.random.uniform(-180, 180)
    
    def _assign_link_properties(self):
        """Assign properties to each link (edge)"""
        for edge in self.graph.edges():
            # Bandwidth: [100 Mbps, 1000 Mbps]
            bandwidth = np.random.uniform(100, 1000)
            
            # Link Delay: [3 ms, 15 ms]
            link_delay = np.random.uniform(3, 15)
            
            # Link Reliability: [0.95, 0.999]
            link_reliability = np.random.uniform(0.95, 0.999)
            
            self.graph.edges[edge]['bandwidth'] = bandwidth
            self.graph.edges[edge]['delay'] = link_delay
            self.graph.edges[edge]['reliability'] = link_reliability
    
    def get_path_metrics(self, path: list) -> Dict[str, float]:
        """
        Calculate metrics for a given path
        
        Args:
            path: List of nodes representing the path
            
        Returns:
            Dictionary containing total_delay, total_reliability, and resource_cost
        """
        if not path or len(path) < 2:
            return {
                'total_delay': float('inf'),
                'total_reliability': 0.0,
                'resource_cost': float('inf')
            }
        
        total_delay = 0.0
        total_reliability = 1.0
        resource_cost = 0.0
        
        # Calculate metrics
        for i in range(len(path)):
            # Add node processing delay and reliability
            node = path[i]
            total_delay += self.graph.nodes[node]['processing_delay']
            total_reliability *= self.graph.nodes[node]['reliability']
            
            # Add link delay and reliability (except for last node)
            if i < len(path) - 1:
                edge = (path[i], path[i + 1])
                # Handle undirected graph
                if edge not in self.graph.edges():
                    edge = (path[i + 1], path[i])
                
                if edge in self.graph.edges():
                    total_delay += self.graph.edges[edge]['delay']
                    total_reliability *= self.graph.edges[edge]['reliability']
                    # Resource cost is based on bandwidth usage
                    resource_cost += 1000.0 / self.graph.edges[edge]['bandwidth']
                else:
                    # Invalid path
                    return {
                        'total_delay': float('inf'),
                        'total_reliability': 0.0,
                        'resource_cost': float('inf')
                    }
        
        return {
            'total_delay': total_delay,
            'total_reliability': total_reliability,
            'resource_cost': resource_cost
        }
    
    def calculate_total_cost(self, path: list, weights: Dict[str, float]) -> float:
        """
        Calculate total cost using weighted sum method
        
        Args:
            path: List of nodes representing the path
            weights: Dictionary with keys 'delay', 'reliability', 'resource'
            
        Returns:
            Total cost value
        """
        metrics = self.get_path_metrics(path)
        
        # Normalize reliability (convert to cost: 1 - reliability)
        reliability_cost = 1.0 - metrics['total_reliability']
        
        total_cost = (
            weights['delay'] * metrics['total_delay'] +
            weights['reliability'] * reliability_cost +
            weights['resource'] * metrics['resource_cost']
        )
        
        return total_cost
    
    def verify_connectivity(self, source: int, destination: int) -> bool:
        """
        Verify that there is a path between source and destination
        
        Args:
            source: Source node
            destination: Destination node
            
        Returns:
            True if path exists, False otherwise
        """
        if self.graph is None:
            return False
        
        return nx.has_path(self.graph, source, destination)
    
    def get_shortest_path(self, source: int, destination: int) -> list:
        """
        Get shortest path using Dijkstra's algorithm
        
        Args:
            source: Source node
            destination: Destination node
            
        Returns:
            List of nodes representing the shortest path
        """
        if not self.verify_connectivity(source, destination):
            return []
        
        return nx.shortest_path(self.graph, source, destination)
    
    def save_network(self, filename: str):
        """Save network to file"""
        if self.graph is not None:
            nx.write_gpickle(self.graph, filename)
    
    def load_network(self, filename: str):
        """Load network from file"""
        self.graph = nx.read_gpickle(filename)
