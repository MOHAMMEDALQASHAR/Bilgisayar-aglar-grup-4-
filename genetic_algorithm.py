"""
Genetic Algorithm for Network Path Optimization
"""

import random
import numpy as np
from typing import List, Tuple, Dict
import networkx as nx


class GeneticAlgorithm:
    """Genetic Algorithm for finding optimal paths in networks"""
    
    def __init__(self, graph: nx.Graph, source: int, destination: int,
                 population_size: int = 30, generations: int = 30,
                 mutation_rate: float = 0.1, crossover_rate: float = 0.8,
                 elite_size: int = 5):
        """
        Initialize Genetic Algorithm
        
        Args:
            graph: Network graph
            source: Source node
            destination: Destination node
            population_size: Number of individuals in population
            generations: Number of generations to evolve
            mutation_rate: Probability of mutation
            crossover_rate: Probability of crossover
            elite_size: Number of elite individuals to preserve
        """
        self.graph = graph
        self.source = source
        self.destination = destination
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_size = elite_size
        
        self.weights = {'delay': 0.33, 'reliability': 0.33, 'resource': 0.34}
        self.network_generator = None
        
    def set_weights(self, weights: Dict[str, float]):
        """Set weights for multi-objective optimization"""
        self.weights = weights
    
    def set_network_generator(self, network_generator):
        """Set network generator for metric calculations"""
        self.network_generator = network_generator
    
    def _generate_random_path(self) -> List[int]:
        """Generate a random valid path from source to destination"""
        try:
            # Get shortest path as base
            path = nx.shortest_path(self.graph, self.source, self.destination)
            
            # Randomly extend the path with neighbors
            if random.random() < 0.5 and len(path) > 2:
                insert_pos = random.randint(1, len(path) - 1)
                current_node = path[insert_pos - 1]
                next_node = path[insert_pos]
                
                neighbors = list(self.graph.neighbors(current_node))
                neighbors = [n for n in neighbors if n not in path[:insert_pos]]
                
                if neighbors:
                    new_node = random.choice(neighbors)
                    if nx.has_path(self.graph, new_node, next_node):
                        path.insert(insert_pos, new_node)
            
            return path
        except:
            return []
    
    def _initialize_population(self) -> List[List[int]]:
        """Initialize population with random paths"""
        population = []
        
        # Add shortest path
        try:
            shortest = nx.shortest_path(self.graph, self.source, self.destination)
            population.append(shortest)
        except:
            pass
        
        # Generate random paths
        attempts = 0
        max_attempts = self.population_size * 10
        
        while len(population) < self.population_size and attempts < max_attempts:
            path = self._generate_random_path()
            if path and path not in population:
                population.append(path)
            attempts += 1
        
        # Fill remaining with shortest path if needed
        while len(population) < self.population_size:
            try:
                shortest = nx.shortest_path(self.graph, self.source, self.destination)
                population.append(shortest[:])
            except:
                population.append([self.source, self.destination])
        
        return population
    
    def _calculate_fitness(self, path: List[int]) -> float:
        """Calculate fitness of a path (lower cost = higher fitness)"""
        if not self.network_generator:
            return 0.0
        
        cost = self.network_generator.calculate_total_cost(path, self.weights)
        
        # Convert cost to fitness (inverse relationship)
        if cost == float('inf') or cost == 0:
            return 0.0
        
        return 1.0 / cost
    
    def _selection(self, population: List[List[int]], fitnesses: List[float]) -> List[int]:
        """Select parent using tournament selection"""
        tournament_size = 5
        tournament = random.sample(list(zip(population, fitnesses)), 
                                  min(tournament_size, len(population)))
        winner = max(tournament, key=lambda x: x[1])
        return winner[0]
    
    def _crossover(self, parent1: List[int], parent2: List[int]) -> Tuple[List[int], List[int]]:
        """Perform crossover between two parents"""
        if random.random() > self.crossover_rate:
            return parent1[:], parent2[:]
        
        # Find common nodes
        common_nodes = set(parent1) & set(parent2)
        common_nodes.discard(self.source)
        common_nodes.discard(self.destination)
        
        if not common_nodes:
            return parent1[:], parent2[:]
        
        # Pick a random common node as crossover point
        crossover_node = random.choice(list(common_nodes))
        
        # Find indices
        idx1 = parent1.index(crossover_node)
        idx2 = parent2.index(crossover_node)
        
        # Create offspring
        child1 = parent1[:idx1] + parent2[idx2:]
        child2 = parent2[:idx2] + parent1[idx1:]
        
        # Validate paths
        child1 = self._repair_path(child1)
        child2 = self._repair_path(child2)
        
        return child1, child2
    
    def _mutate(self, path: List[int]) -> List[int]:
        """Mutate a path"""
        if random.random() > self.mutation_rate or len(path) <= 2:
            return path
        
        mutated = path[:]
        
        mutation_type = random.randint(0, 2)
        
        if mutation_type == 0:  # Insert a random node
            insert_pos = random.randint(1, len(mutated) - 1)
            current_node = mutated[insert_pos - 1]
            neighbors = list(self.graph.neighbors(current_node))
            neighbors = [n for n in neighbors if n not in mutated]
            
            if neighbors:
                new_node = random.choice(neighbors)
                mutated.insert(insert_pos, new_node)
        
        elif mutation_type == 1 and len(mutated) > 3:  # Remove a random node
            remove_pos = random.randint(1, len(mutated) - 2)
            mutated.pop(remove_pos)
        
        else:  # Replace a segment
            if len(mutated) > 3:
                pos1 = random.randint(1, len(mutated) - 2)
                pos2 = random.randint(pos1 + 1, len(mutated) - 1)
                
                try:
                    segment = nx.shortest_path(self.graph, mutated[pos1 - 1], mutated[pos2])
                    mutated = mutated[:pos1] + segment[1:pos2] + mutated[pos2:]
                except:
                    pass
        
        return self._repair_path(mutated)
    
    def _repair_path(self, path: List[int]) -> List[int]:
        """Repair invalid path"""
        if not path:
            try:
                return nx.shortest_path(self.graph, self.source, self.destination)
            except:
                return [self.source, self.destination]
        
        # Ensure source and destination
        if path[0] != self.source:
            path.insert(0, self.source)
        if path[-1] != self.destination:
            path.append(self.destination)
        
        # Remove duplicates while maintaining order
        seen = set()
        repaired = []
        for node in path:
            if node not in seen:
                seen.add(node)
                repaired.append(node)
        
        # Verify connectivity and fix if needed
        fixed = [repaired[0]]
        for i in range(1, len(repaired)):
            if not self.graph.has_edge(fixed[-1], repaired[i]):
                # Find path between disconnected nodes
                try:
                    bridge = nx.shortest_path(self.graph, fixed[-1], repaired[i])
                    fixed.extend(bridge[1:])
                except:
                    # If no path, restart from current node
                    fixed = [repaired[i]]
            else:
                fixed.append(repaired[i])
        
        # Ensure we end at destination
        if fixed[-1] != self.destination:
            try:
                bridge = nx.shortest_path(self.graph, fixed[-1], self.destination)
                fixed.extend(bridge[1:])
            except:
                return nx.shortest_path(self.graph, self.source, self.destination)
        
        return fixed
    
    def optimize(self) -> Tuple[List[int], float, Dict]:
        """
        Run genetic algorithm optimization
        
        Returns:
            Tuple of (best_path, best_cost, statistics)
        """
        # Initialize population
        population = self._initialize_population()
        
        best_path = None
        best_fitness = 0.0
        history = {
            'best_fitness': [],
            'avg_fitness': [],
            'diversity': []
        }
        
        for generation in range(self.generations):
            # Calculate fitness for all individuals
            fitnesses = [self._calculate_fitness(path) for path in population]
            
            # Track best solution
            max_fitness_idx = np.argmax(fitnesses)
            if fitnesses[max_fitness_idx] > best_fitness:
                best_fitness = fitnesses[max_fitness_idx]
                best_path = population[max_fitness_idx][:]
            
            # Record statistics
            history['best_fitness'].append(best_fitness)
            history['avg_fitness'].append(np.mean(fitnesses))
            history['diversity'].append(len(set(map(tuple, population))))
            
            # Create new population
            new_population = []
            
            # Elitism: keep best individuals
            elite_indices = np.argsort(fitnesses)[-self.elite_size:]
            for idx in elite_indices:
                new_population.append(population[idx][:])
            
            # Generate offspring
            while len(new_population) < self.population_size:
                parent1 = self._selection(population, fitnesses)
                parent2 = self._selection(population, fitnesses)
                
                child1, child2 = self._crossover(parent1, parent2)
                
                child1 = self._mutate(child1)
                child2 = self._mutate(child2)
                
                new_population.append(child1)
                if len(new_population) < self.population_size:
                    new_population.append(child2)
            
            population = new_population[:self.population_size]
        
        # Calculate final cost
        if best_path and self.network_generator:
            best_cost = self.network_generator.calculate_total_cost(best_path, self.weights)
        else:
            best_cost = float('inf')
        
        return best_path, best_cost, history
