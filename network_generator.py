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
        
    
    def load_from_data(self, nodes_df, edges_df):
        """
        Build graph from pandas DataFrames
        
        Args:
            nodes_df: DataFrame containing node data
            edges_df: DataFrame containing edge data
            
        Returns:
            NetworkX graph object
        """
        G = nx.Graph()
        
        # Add nodes
        for _, row in nodes_df.iterrows():
            node_id = int(row['node_id'])
            G.add_node(node_id)
            
            # Map columns to properties
            G.nodes[node_id]['processing_delay'] = float(row['s_ms']) if 's_ms' in row else 1.0
            G.nodes[node_id]['reliability'] = float(row['r_node']) if 'r_node' in row else 0.99
            
            # Generate random geographical coordinates for visualization
            G.nodes[node_id]['lat'] = np.random.uniform(-60, 80)
            G.nodes[node_id]['lng'] = np.random.uniform(-180, 180)
            
        # Add edges
        for _, row in edges_df.iterrows():
            src = int(row['src'])
            dst = int(row['dst'])
            
            # Ensure nodes exist
            if not G.has_node(src):
                G.add_node(src)
                G.nodes[src]['processing_delay'] = 1.0
                G.nodes[src]['reliability'] = 0.99
                G.nodes[src]['lat'] = np.random.uniform(-60, 80)
                G.nodes[src]['lng'] = np.random.uniform(-180, 180)
                
            if not G.has_node(dst):
                G.add_node(dst)
                G.nodes[dst]['processing_delay'] = 1.0
                G.nodes[dst]['reliability'] = 0.99
                G.nodes[dst]['lat'] = np.random.uniform(-60, 80)
                G.nodes[dst]['lng'] = np.random.uniform(-180, 180)
            
            G.add_edge(src, dst)
            
            # Map columns to properties
            G.edges[src, dst]['bandwidth'] = float(row['capacity_mbps']) if 'capacity_mbps' in row else 100.0
            G.edges[src, dst]['delay'] = float(row['delay_ms']) if 'delay_ms' in row else 5.0
            G.edges[src, dst]['reliability'] = float(row['r_link']) if 'r_link' in row else 0.99
            
        self.graph = G
        return G

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
                'resource_cost': float('inf'),
                'min_bandwidth': 0.0
            }
        
        total_delay = 0.0
        total_reliability = 1.0
        resource_cost = 0.0
        min_bandwidth = float('inf')
        
        # Calculate metrics
        for i in range(len(path)):
            # Add node processing delay and reliability
            node = path[i]
            
            # Per PDF/network_model.py: Source and Dest nodes do NOT contribute to processing delay
            # Only intermediate nodes add delay.
            if i > 0 and i < len(path) - 1:
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
                    bandwidth = self.graph.edges[edge]['bandwidth']
                    resource_cost += 1000.0 / bandwidth
                    
                    if bandwidth < min_bandwidth:
                        min_bandwidth = bandwidth
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
            'resource_cost': resource_cost,
            'min_bandwidth': min_bandwidth
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
        import math
        
        metrics = self.get_path_metrics(path)
        
        # Calculate Reliability Cost using -log method (from network_model.py)
        # reliability_cost = -log(total_reliability)
        # Avoid log(0)
        if metrics['total_reliability'] > 0:
            reliability_cost = -math.log(metrics['total_reliability'])
        else:
            reliability_cost = float('inf')
        
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
