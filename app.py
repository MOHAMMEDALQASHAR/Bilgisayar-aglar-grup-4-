"""
Flask Backend API for Network Path Optimization
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import time
import numpy as np

from network_generator import NetworkGenerator
from genetic_algorithm import GeneticAlgorithm
from ant_colony import AntColonyOptimization
from particle_swarm import ParticleSwarmOptimization
from simulated_annealing import SimulatedAnnealing

app = Flask(__name__)
CORS(app)

# Global network instance
network_gen = None
graph = None


@app.route('/')
def index():
    """Serve main page"""
    return render_template('index.html')


@app.route('/api/generate_network', methods=['POST'])
def generate_network():
    """Generate new network"""
    global network_gen, graph
    
    try:
        data = request.json
        num_nodes = data.get('num_nodes', 250)
        connection_prob = data.get('connection_prob', 0.4)
        seed = data.get('seed', None)
        
        # Generate network
        network_gen = NetworkGenerator(num_nodes, connection_prob, seed)
        graph = network_gen.generate_connected_network()
        
        # Prepare network data for visualization
        nodes_data = []
        for node in graph.nodes():
            nodes_data.append({
                'id': int(node),
                'lat': float(graph.nodes[node]['lat']),
                'lng': float(graph.nodes[node]['lng']),
                'processing_delay': float(graph.nodes[node]['processing_delay']),
                'reliability': float(graph.nodes[node]['reliability'])
            })
        
        edges_data = []
        for edge in graph.edges():
            edges_data.append({
                'source': int(edge[0]),
                'target': int(edge[1]),
                'bandwidth': float(graph.edges[edge]['bandwidth']),
                'delay': float(graph.edges[edge]['delay']),
                'reliability': float(graph.edges[edge]['reliability'])
            })
        
        return jsonify({
            'success': True,
            'nodes': nodes_data,
            'edges': edges_data,
            'num_nodes': len(nodes_data),
            'num_edges': len(edges_data)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/optimize', methods=['POST'])
def optimize_path():
    """Run optimization algorithm"""
    global network_gen, graph
    
    if network_gen is None or graph is None:
        return jsonify({
            'success': False,
            'error': 'Ağ oluşturulmadı. Lütfen önce ağı oluşturun.'
        }), 400
    
    try:
        data = request.json
        
        source = int(data.get('source'))
        destination = int(data.get('destination'))
        algorithm = data.get('algorithm', 'GA')
        weights = data.get('weights', {
            'delay': 0.33,
            'reliability': 0.33,
            'resource': 0.34
        })
        
        # Verify source and destination exist
        if source not in graph.nodes() or destination not in graph.nodes():
            return jsonify({
                'success': False,
                'error': 'Geçersiz kaynak veya hedef düğüm'
            }), 400
        
        # Verify connectivity
        if not network_gen.verify_connectivity(source, destination):
            return jsonify({
                'success': False,
                'error': 'Kaynak ve hedef arasında yol yok'
            }), 400
        
        # Initialize algorithm
        start_time = time.time()
        
        if algorithm == 'GA':
            algo = GeneticAlgorithm(graph, source, destination)
        elif algorithm == 'ACO':
            algo = AntColonyOptimization(graph, source, destination)
        elif algorithm == 'PSO':
            algo = ParticleSwarmOptimization(graph, source, destination)
        elif algorithm == 'SA':
            algo = SimulatedAnnealing(graph, source, destination)
        else:
            return jsonify({
                'success': False,
                'error': f'Bilinmeyen algoritma: {algorithm}'
            }), 400
        
        # Set weights and network generator
        algo.set_weights(weights)
        algo.set_network_generator(network_gen)
        
        # Run optimization
        best_path, best_cost, history = algo.optimize()
        
        execution_time = time.time() - start_time
        
        # Calculate detailed metrics
        metrics = network_gen.get_path_metrics(best_path)
        
        return jsonify({
            'success': True,
            'path': [int(node) for node in best_path],
            'cost': float(best_cost),
            'metrics': {
                'total_delay': float(metrics['total_delay']),
                'total_reliability': float(metrics['total_reliability']),
                'resource_cost': float(metrics['resource_cost'])
            },
            'execution_time': float(execution_time),
            'path_length': len(best_path),
            'algorithm': algorithm
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/compare_algorithms', methods=['POST'])
def compare_algorithms():
    """Compare all algorithms"""
    global network_gen, graph
    
    if network_gen is None or graph is None:
        return jsonify({
            'success': False,
            'error': 'Ağ oluşturulmadı'
        }), 400
    
    try:
        data = request.json
        source = int(data.get('source'))
        destination = int(data.get('destination'))
        weights = data.get('weights', {
            'delay': 0.33,
            'reliability': 0.33,
            'resource': 0.34
        })
        
        results = {}
        algorithms = {
            'GA': GeneticAlgorithm,
            'ACO': AntColonyOptimization,
            'PSO': ParticleSwarmOptimization,
            'SA': SimulatedAnnealing
        }
        
        for algo_name, AlgoClass in algorithms.items():
            start_time = time.time()
            
            algo = AlgoClass(graph, source, destination)
            algo.set_weights(weights)
            algo.set_network_generator(network_gen)
            
            best_path, best_cost, history = algo.optimize()
            execution_time = time.time() - start_time
            
            metrics = network_gen.get_path_metrics(best_path)
            
            results[algo_name] = {
                'path': [int(node) for node in best_path],
                'cost': float(best_cost),
                'metrics': {
                    'total_delay': float(metrics['total_delay']),
                    'total_reliability': float(metrics['total_reliability']),
                    'resource_cost': float(metrics['resource_cost'])
                },
                'execution_time': float(execution_time),
                'path_length': len(best_path)
            }
        
        return jsonify({
            'success': True,
            'results': results
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/run_tests', methods=['POST'])
def run_tests():
    """Run comprehensive tests with multiple scenarios"""
    global network_gen, graph
    
    if network_gen is None or graph is None:
        return jsonify({
            'success': False,
            'error': 'Ağ oluşturulmadı'
        }), 400
    
    try:
        data = request.json
        num_tests = data.get('num_tests', 20)
        
        # Generate random test cases
        import random
        nodes = list(graph.nodes())
        test_cases = []
        
        for _ in range(num_tests):
            source = random.choice(nodes)
            destination = random.choice([n for n in nodes if n != source])
            
            # Verify connectivity
            if network_gen.verify_connectivity(source, destination):
                test_cases.append({
                    'source': source,
                    'destination': destination
                })
        
        # Run all algorithms on all test cases
        results = {
            'GA': [],
            'ACO': [],
            'PSO': [],
            'SA': []
        }
        
        algorithms = {
            'GA': GeneticAlgorithm,
            'ACO': AntColonyOptimization,
            'PSO': ParticleSwarmOptimization,
            'SA': SimulatedAnnealing
        }
        
        weights = {'delay': 0.33, 'reliability': 0.33, 'resource': 0.34}
        
        for test_idx, test_case in enumerate(test_cases):
            source = test_case['source']
            destination = test_case['destination']
            
            for algo_name, AlgoClass in algorithms.items():
                start_time = time.time()
                
                algo = AlgoClass(graph, source, destination)
                algo.set_weights(weights)
                algo.set_network_generator(network_gen)
                
                best_path, best_cost, history = algo.optimize()
                execution_time = time.time() - start_time
                
                metrics = network_gen.get_path_metrics(best_path)
                
                results[algo_name].append({
                    'test_id': test_idx,
                    'source': source,
                    'destination': destination,
                    'cost': float(best_cost),
                    'execution_time': float(execution_time),
                    'path_length': len(best_path),
                    'total_delay': float(metrics['total_delay']),
                    'total_reliability': float(metrics['total_reliability']),
                    'resource_cost': float(metrics['resource_cost'])
                })
        
        # Calculate statistics
        statistics = {}
        for algo_name in algorithms.keys():
            costs = [r['cost'] for r in results[algo_name]]
            times = [r['execution_time'] for r in results[algo_name]]
            delays = [r['total_delay'] for r in results[algo_name]]
            reliabilities = [r['total_reliability'] for r in results[algo_name]]
            
            statistics[algo_name] = {
                'mean_cost': float(np.mean(costs)),
                'std_cost': float(np.std(costs)),
                'min_cost': float(np.min(costs)),
                'max_cost': float(np.max(costs)),
                'mean_time': float(np.mean(times)),
                'std_time': float(np.std(times)),
                'mean_delay': float(np.mean(delays)),
                'mean_reliability': float(np.mean(reliabilities))
            }
        
        return jsonify({
            'success': True,
            'num_tests': len(test_cases),
            'results': results,
            'statistics': statistics
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
